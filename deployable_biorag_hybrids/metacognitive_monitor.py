"""
Metacognitive Monitor — PFC Self-Calibration Layer
====================================================
The second half of Pillar 6.

pfc_engine.py  → impulse control  (should I act on this NOW?)
metacognitive_monitor.py → self-calibration (are my pillars trustworthy?)

Biology:
  The prefrontal cortex doesn't just gate impulses.
  It also monitors whether its own strategies are working.
  When a strategy consistently fails, the PFC shifts executive control —
  reduces weight on the failing subsystem, elevates others.

  This is metacognition: thinking about the quality of your own thinking.

What this does:
  - Maintains a decision_log per pillar
  - After every N steps, computes rolling fail rate attributed to each pillar
  - Adjusts pillar trust scores: metacog.trust[pillar_name] ∈ [0.1, 1.5]
  - Trust scores multiply into QuintSignalBus.fuse() confidence weighting

  QuintSignalBus.fuse() BEFORE:
    weighted_sum = sum(s.action_weights[a] * s.confidence for s in signals)

  QuintSignalBus.fuse() AFTER:
    weighted_sum = sum(
        s.action_weights[a] * s.confidence * metacog.trust[s.pillar_name]
        for s in signals
    )

Concrete failure modes detected:
  - CME causing more failures than it prevents → reduce CME trust
  - BioRAG bleeding contexts (same context, different results) → reduce BioRAG trust
  - Bandit exploring too much in a stable environment → tighten explore rate
  - TFE orphaning keys prematurely → reduce TFE confidence weight

Design principles:
  - Trust scores change SLOWLY (biological: PFC doesn't panic)
  - Trust never reaches 0 (every pillar retains minimum voice)
  - Trust can exceed 1.0 (a performing pillar gets amplified)
  - All adjustments are logged for audit trail / NoesisCards
  - Reset-safe: trust decays toward 1.0 if no signal (regression to mean)
"""

import math
from collections import deque, defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple


# ─────────────────────────────────────────────────────────────
# DECISION LOG ENTRY — one record per step
# ─────────────────────────────────────────────────────────────

@dataclass
class DecisionRecord:
    """
    What happened at one step.
    Logged after update() — includes outcome and which pillars were active.
    """
    step:            int
    context_key:     str
    action:          str
    success:         bool
    pillar_signals:  Dict[str, float]  # pillar_name → confidence it emitted
    pfc_verdict:     str               # PROCEED / SLOW / ESCALATE
    novelty_score:   float
    uncertainty_score: float


# ─────────────────────────────────────────────────────────────
# PILLAR PERFORMANCE TRACKER
# ─────────────────────────────────────────────────────────────

@dataclass
class PillarPerformance:
    """
    Rolling performance metrics for one pillar.
    Computed from decision_log attribution.
    """
    pillar_name:      str
    steps_active:     int   = 0     # steps where this pillar had confidence > 0
    attributed_wins:  float = 0.0   # weighted successes attributed to this pillar
    attributed_losses: float = 0.0  # weighted failures attributed to this pillar

    @property
    def total_attributed(self) -> float:
        return self.attributed_wins + self.attributed_losses

    @property
    def win_rate(self) -> float:
        if self.total_attributed < 1.0:
            return 0.5  # no data → neutral
        return self.attributed_wins / self.total_attributed

    @property
    def loss_rate(self) -> float:
        return 1.0 - self.win_rate


# ─────────────────────────────────────────────────────────────
# METACOGNITIVE MONITOR CONFIG
# ─────────────────────────────────────────────────────────────

@dataclass
class MetacogConfig:
    """
    Tuning parameters for the metacognitive monitor.

    review_every_n_steps:
        How often to recalibrate trust scores.
        Biological: PFC doesn't re-evaluate every millisecond.
        Default 20 = after every 20 decisions.

    window_size:
        Rolling window for performance tracking.
        Only the last N decisions count.
        Prevents old failures from permanently damning a pillar.

    trust_min / trust_max:
        Hard bounds on trust scores.
        Min=0.1 ensures every pillar retains a voice.
        Max=1.5 allows a strong pillar to be amplified.

    trust_adjust_rate:
        How fast trust scores change per review cycle.
        Low value = slow, stable adjustments (biological PFC behavior).
        High value = fast, reactive adjustments (risky — can oscillate).

    trust_decay_toward_neutral:
        Each cycle, trust drifts back toward 1.0 by this fraction.
        Prevents a pillar from being permanently suppressed.
        Like forgetting old grudges.

    fail_rate_threshold:
        If a pillar's attributed fail rate exceeds this → reduce trust.

    win_rate_bonus_threshold:
        If a pillar's attributed win rate exceeds this → increase trust.

    bandit_explore_stable_threshold:
        If environment appears stable (low flip rate) AND bandit is
        exploring above this rate → flag for tightening.

    context_bleed_threshold:
        Fraction of BioRAG retrievals where context overlap was poor
        → flag BioRAG for trust reduction.
    """
    review_every_n_steps:        int   = 20
    window_size:                 int   = 100
    trust_min:                   float = 0.10
    trust_max:                   float = 1.50
    trust_adjust_rate:           float = 0.08   # per review cycle
    trust_decay_toward_neutral:  float = 0.02   # per review cycle
    fail_rate_threshold:         float = 0.45   # above this → reduce trust
    win_rate_bonus_threshold:    float = 0.70   # above this → increase trust
    bandit_explore_stable_threshold: float = 0.15
    context_bleed_threshold:     float = 0.40
    min_steps_before_adjust:     int   = 10     # don't adjust on first few steps


# ─────────────────────────────────────────────────────────────
# METACOGNITIVE MONITOR
# ─────────────────────────────────────────────────────────────

class MetacognitiveMonitor:
    """
    Pillar 6b — Metacognitive Monitor.

    Instantiate once inside QuintBioRAGAgent alongside PFCEngine.
    
    Call log_decision() inside update() after every outcome.
    Call get_trust() inside QuintSignalBus.fuse() to apply trust multipliers.

    Usage:
        # In QuintBioRAGAgent.__init__:
        self.metacog = MetacognitiveMonitor()

        # In QuintBioRAGAgent.update():
        self.metacog.log_decision(record)
        
        # In QuintSignalBus.fuse() — the hook point:
        trust = metacog.trust  # Dict[str, float]
        effective_confidence = s.confidence * trust.get(s.pillar_name, 1.0)
    """

    # Pillar names — must match pillar_name strings in PillarSignal
    PILLAR_NAMES = ["CME", "TFE", "BioRAG", "SimpleRAG", "RAG-Stub"]

    def __init__(self, config: Optional[MetacogConfig] = None):
        self.config = config or MetacogConfig()

        # Trust scores: pillar_name → float ∈ [trust_min, trust_max]
        # Start at 1.0 (neutral — no prior bias)
        self.trust: Dict[str, float] = defaultdict(lambda: 1.0)

        # Rolling decision log
        self._log: deque = deque(maxlen=self.config.window_size)

        # Per-pillar performance trackers (rolling)
        self._performance: Dict[str, PillarPerformance] = {}

        # Step counter
        self._steps_logged: int = 0
        self._last_review_step: int = 0

        # Audit trail of trust adjustments
        self._adjustment_log: deque = deque(maxlen=100)

        # Bandit explore rate tracking (for stability detection)
        self._explore_history: deque = deque(maxlen=50)

        # BioRAG context quality tracking
        self._biorag_quality: deque = deque(maxlen=50)

        # Environment flip detector (for bandit explore rate tuning)
        self._recent_outcomes: deque = deque(maxlen=30)
        self._flip_count: int = 0

    # ─────────────────────────────────────────────
    # LOGGING — called in update()
    # ─────────────────────────────────────────────

    def log_decision(self, record: DecisionRecord) -> Optional[Dict[str, Any]]:
        """
        Log one decision outcome.
        Called inside update() after every step.

        Returns adjustment report if a review cycle ran, else None.
        """
        self._log.append(record)
        self._steps_logged += 1

        # Track outcome for environment stability detection
        self._recent_outcomes.append(1 if record.success else 0)

        # Attribute outcome to active pillars
        self._attribute_outcome(record)

        # Check if it's time for a review cycle
        steps_since_review = self._steps_logged - self._last_review_step
        if (steps_since_review >= self.config.review_every_n_steps and
                self._steps_logged >= self.config.min_steps_before_adjust):
            return self._run_review_cycle()

        return None

    def log_biorag_quality(self, retrieval_confidence: float) -> None:
        """
        Log BioRAG retrieval quality.
        Called after BioRAG.retrieve() in choose().

        retrieval_confidence: the confidence BioRAG returned (0=no match, 1=strong match)
        Low confidence = context bleed / poor attractor convergence.
        """
        self._biorag_quality.append(retrieval_confidence)

    def log_bandit_explore(self, did_explore: bool) -> None:
        """
        Log whether the Bandit explored this step.
        Called after bandit.get_action() in choose().
        """
        self._explore_history.append(1 if did_explore else 0)

    # ─────────────────────────────────────────────
    # OUTCOME ATTRIBUTION
    # ─────────────────────────────────────────────

    def _attribute_outcome(self, record: DecisionRecord) -> None:
        """
        Attribute success/failure to pillars based on their confidence.

        If CME had high confidence and the action failed →
        CME gets a weighted failure attribution.

        If BioRAG had high confidence and the action succeeded →
        BioRAG gets a weighted success attribution.

        Weight = pillar_confidence / total_confidence (same as fuse() logic)
        This mirrors what actually happened in the decision.
        """
        total_conf = sum(record.pillar_signals.values())
        if total_conf <= 0:
            return

        for pillar_name, confidence in record.pillar_signals.items():
            if confidence <= 0:
                continue

            weight = confidence / total_conf

            if pillar_name not in self._performance:
                self._performance[pillar_name] = PillarPerformance(pillar_name)

            perf = self._performance[pillar_name]
            perf.steps_active += 1

            if record.success:
                perf.attributed_wins  += weight
            else:
                perf.attributed_losses += weight

    # ─────────────────────────────────────────────
    # REVIEW CYCLE — the metacognitive heartbeat
    # ─────────────────────────────────────────────

    def _run_review_cycle(self) -> Dict[str, Any]:
        """
        Review pillar performance and adjust trust scores.
        Called every N steps.

        This is the PFC's self-monitoring loop.
        """
        self._last_review_step = self._steps_logged
        adjustments = {}
        cfg = self.config

        # ── 1. Trust decay toward neutral (forgetting) ────────────────
        # Every review cycle, all trusts drift back toward 1.0
        for pillar in list(self.trust.keys()):
            current = self.trust[pillar]
            if current > 1.0:
                self.trust[pillar] = max(1.0, current - cfg.trust_decay_toward_neutral)
            elif current < 1.0:
                self.trust[pillar] = min(1.0, current + cfg.trust_decay_toward_neutral)

        # ── 2. Pillar performance adjustments ────────────────────────
        for pillar_name, perf in self._performance.items():
            if perf.total_attributed < 3.0:
                continue  # not enough data

            old_trust = self.trust[pillar_name]
            new_trust = old_trust
            reason = None

            # Failing pillar → reduce trust
            if perf.loss_rate > cfg.fail_rate_threshold:
                reduction = cfg.trust_adjust_rate * (perf.loss_rate - cfg.fail_rate_threshold)
                new_trust = max(cfg.trust_min, old_trust - reduction)
                reason = f"loss_rate={perf.loss_rate:.3f} > threshold={cfg.fail_rate_threshold}"

            # Winning pillar → increase trust
            elif perf.win_rate > cfg.win_rate_bonus_threshold:
                bonus = cfg.trust_adjust_rate * (perf.win_rate - cfg.win_rate_bonus_threshold)
                new_trust = min(cfg.trust_max, old_trust + bonus)
                reason = f"win_rate={perf.win_rate:.3f} > threshold={cfg.win_rate_bonus_threshold}"

            if new_trust != old_trust:
                self.trust[pillar_name] = new_trust
                adjustments[pillar_name] = {
                    "old_trust": round(old_trust, 4),
                    "new_trust": round(new_trust, 4),
                    "reason": reason,
                    "win_rate": round(perf.win_rate, 3),
                    "loss_rate": round(perf.loss_rate, 3),
                }

        # ── 3. BioRAG context bleed detection ────────────────────────
        if len(self._biorag_quality) >= 10:
            avg_quality = sum(self._biorag_quality) / len(self._biorag_quality)
            if avg_quality < (1.0 - cfg.context_bleed_threshold):
                # BioRAG is consistently returning low-confidence retrievals
                old_trust = self.trust["BioRAG"]
                new_trust = max(cfg.trust_min, old_trust - cfg.trust_adjust_rate * 0.5)
                self.trust["BioRAG"] = new_trust
                adjustments["BioRAG_bleed"] = {
                    "old_trust": round(old_trust, 4),
                    "new_trust": round(new_trust, 4),
                    "reason": f"avg_retrieval_quality={avg_quality:.3f} — context bleed detected",
                    "avg_retrieval_confidence": round(avg_quality, 3),
                }

        # ── 4. Bandit explore rate in stable environment ──────────────
        explore_rate = self._compute_explore_rate()
        env_stability = self._compute_env_stability()
        bandit_adjustment = self._check_bandit_stability(
            explore_rate, env_stability
        )
        if bandit_adjustment:
            adjustments["Bandit_explore"] = bandit_adjustment

        # ── 5. Reset rolling performance (fresh window) ───────────────
        # Don't reset completely — decay attributed counts
        for perf in self._performance.values():
            perf.attributed_wins   *= 0.7
            perf.attributed_losses *= 0.7
            perf.steps_active = int(perf.steps_active * 0.7)

        # ── 6. Log the adjustment ─────────────────────────────────────
        report = {
            "step": self._steps_logged,
            "adjustments": adjustments,
            "trust_snapshot": {k: round(v, 4) for k, v in self.trust.items()},
            "env_stability": round(env_stability, 3),
            "explore_rate": round(explore_rate, 3),
        }

        if adjustments:
            self._adjustment_log.append(report)

        return report

    # ─────────────────────────────────────────────
    # ENVIRONMENT STABILITY DETECTION
    # ─────────────────────────────────────────────

    def _compute_env_stability(self) -> float:
        """
        How stable is the environment right now?
        0.0 = highly volatile (flip happening)
        1.0 = stable (consistent outcomes)

        Computed from variance in recent outcomes.
        High variance = unstable = environment may have flipped.
        """
        if len(self._recent_outcomes) < 5:
            return 0.5  # not enough data

        outcomes = list(self._recent_outcomes)
        mean = sum(outcomes) / len(outcomes)
        variance = sum((x - mean) ** 2 for x in outcomes) / len(outcomes)

        # Low variance → stable (0 or 1 consistently)
        # High variance (near 0.25 max) → unstable
        stability = 1.0 - (variance / 0.25)
        return max(0.0, min(1.0, stability))

    def _compute_explore_rate(self) -> float:
        """Fraction of recent steps where Bandit explored."""
        if not self._explore_history:
            return 0.0
        return sum(self._explore_history) / len(self._explore_history)

    def _check_bandit_stability(
        self,
        explore_rate: float,
        env_stability: float,
    ) -> Optional[Dict[str, Any]]:
        """
        If environment is stable but Bandit is exploring too much →
        return a recommendation to tighten explore rate.

        We don't directly modify the Bandit (separation of concerns).
        We return a flag the agent can act on.
        """
        cfg = self.config
        if (env_stability > 0.75 and
                explore_rate > cfg.bandit_explore_stable_threshold):
            return {
                "recommendation": "tighten_explore_rate",
                "current_explore_rate": round(explore_rate, 3),
                "env_stability": round(env_stability, 3),
                "reason": (
                    f"Stable environment (stability={env_stability:.2f}) "
                    f"but Bandit exploring at {explore_rate:.1%} — "
                    f"exploration is wasting steps"
                ),
            }
        return None

    # ─────────────────────────────────────────────
    # PUBLIC API — used in fuse() and agent
    # ─────────────────────────────────────────────

    def get_trust(self, pillar_name: str) -> float:
        """
        Get current trust multiplier for a pillar.
        Used inside QuintSignalBus.fuse().

        Returns 1.0 if pillar is unknown (neutral default).
        """
        return self.trust.get(pillar_name, 1.0)

    def get_all_trust(self) -> Dict[str, float]:
        """Full trust snapshot. For diagnostics and NoesisCards."""
        return {k: round(v, 4) for k, v in self.trust.items()}

    def get_stats(self) -> Dict[str, Any]:
        """
        Full telemetry for Witch Bridge Cortex panel.
        Feed into Neural Telemetry alongside PFC impulse stats.
        """
        perf_summary = {}
        for name, perf in self._performance.items():
            perf_summary[name] = {
                "win_rate":         round(perf.win_rate, 3),
                "loss_rate":        round(perf.loss_rate, 3),
                "steps_active":     perf.steps_active,
                "total_attributed": round(perf.total_attributed, 2),
                "current_trust":    round(self.trust.get(name, 1.0), 4),
            }

        return {
            "steps_logged":      self._steps_logged,
            "pillar_performance": perf_summary,
            "trust_scores":      self.get_all_trust(),
            "env_stability":     round(self._compute_env_stability(), 3),
            "bandit_explore_rate": round(self._compute_explore_rate(), 3),
            "recent_adjustments": len(self._adjustment_log),
            "last_adjustment":   self._adjustment_log[-1] if self._adjustment_log else None,
        }

    def get_adjustment_log(self) -> list:
        """
        Full adjustment history for NoesisCards audit trail.
        Each trust adjustment should become an evidence card.
        """
        return list(self._adjustment_log)

    def reset_trust(self) -> None:
        """
        Reset all trust scores to neutral (1.0).
        Use on domain load if you want a clean slate.
        Does NOT reset performance history.
        """
        self.trust = defaultdict(lambda: 1.0)

    # ─────────────────────────────────────────────
    # DOMAIN LOADING HOOK
    # ─────────────────────────────────────────────

    def load_domain_config(self, config: MetacogConfig) -> None:
        """
        Swap metacog thresholds for a new domain.
        Medical domain: tighter fail_rate_threshold (less tolerance for bad pillars).
        Coding domain: looser thresholds (pillars can explore more).
        """
        self.config = config


# ─────────────────────────────────────────────────────────────
# MODIFIED QuintSignalBus.fuse() — THE HOOK POINT
# ─────────────────────────────────────────────────────────────

class MetacogAwareSignalBus:
    """
    Drop-in replacement for QuintSignalBus.
    Identical to QuintSignalBus.fuse() EXCEPT:
      - multiplies each pillar's confidence by metacog.trust[pillar_name]
      - this is the single line change described in the spec

    Usage:
        # In QuintBioRAGAgent.__init__:
        self.bus = MetacogAwareSignalBus(self.metacog)

        # fuse() call is identical — no other changes needed
        fused_weights = self.bus.fuse(signals, actions)
    """

    def __init__(self, metacog: MetacognitiveMonitor):
        self.metacog = metacog

    def fuse(
        self,
        signals: List[Any],   # List[PillarSignal]
        actions: List[str],
    ) -> Dict[str, float]:
        """
        QuintSignalBus.fuse() + metacognitive trust multipliers.

        BEFORE:
            weight_frac = s.confidence / total_confidence

        AFTER:
            effective_confidence = s.confidence * metacog.trust[s.pillar_name]
            weight_frac = effective_confidence / total_effective_confidence

        That's it. One multiplication. Everything else identical.
        """
        if not signals:
            return {a: 1.0 for a in actions}

        # Apply trust multipliers to confidence scores
        effective_confidences = {}
        for sig in signals:
            trust = self.metacog.get_trust(sig.pillar_name)
            effective_confidences[sig.pillar_name] = sig.confidence * trust

        total_effective = sum(
            ec for ec in effective_confidences.values() if ec > 0
        )

        if total_effective == 0:
            return {a: 1.0 for a in actions}

        fused = {a: 0.0 for a in actions}
        for sig in signals:
            ec = effective_confidences.get(sig.pillar_name, 0.0)
            if ec <= 0:
                continue
            weight_frac = ec / total_effective
            for a in actions:
                raw = sig.action_weights.get(a, 1.0)
                fused[a] += weight_frac * raw

        # Normalize to [0.05, 1.0]
        mx = max(fused.values()) if fused else 1.0
        if mx > 0:
            fused = {a: max(0.05, v / mx) for a, v in fused.items()}

        return fused


# ─────────────────────────────────────────────────────────────
# PRESET DOMAIN METACOG CONFIGS
# ─────────────────────────────────────────────────────────────

CODING_METACOG_CONFIG = MetacogConfig(
    review_every_n_steps=25,
    fail_rate_threshold=0.5,          # more tolerant — coding fails are recoverable
    win_rate_bonus_threshold=0.75,
    bandit_explore_stable_threshold=0.2,
)

MEDICAL_METACOG_CONFIG = MetacogConfig(
    review_every_n_steps=10,          # review more often — stakes are high
    fail_rate_threshold=0.30,         # much less tolerant of failing pillars
    win_rate_bonus_threshold=0.80,
    trust_adjust_rate=0.12,           # adjust faster
    bandit_explore_stable_threshold=0.08,  # very tight explore tolerance
    context_bleed_threshold=0.25,     # BioRAG must be precise
)

LEGAL_METACOG_CONFIG = MetacogConfig(
    review_every_n_steps=15,
    fail_rate_threshold=0.35,
    win_rate_bonus_threshold=0.75,
    trust_adjust_rate=0.10,
    bandit_explore_stable_threshold=0.10,
    context_bleed_threshold=0.30,
)

FINANCIAL_METACOG_CONFIG = MetacogConfig(
    review_every_n_steps=15,
    fail_rate_threshold=0.38,
    win_rate_bonus_threshold=0.72,
    trust_adjust_rate=0.09,
    bandit_explore_stable_threshold=0.12,
)

METACOG_DOMAIN_REGISTRY = {
    "coding":    CODING_METACOG_CONFIG,
    "medical":   MEDICAL_METACOG_CONFIG,
    "legal":     LEGAL_METACOG_CONFIG,
    "financial": FINANCIAL_METACOG_CONFIG,
    "default":   MetacogConfig(),
}
