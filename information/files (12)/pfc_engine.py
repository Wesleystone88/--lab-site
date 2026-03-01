"""
Pillar 6 — PFC (Prefrontal Cortex Engine)
==========================================
The impulse control layer. Sits between signal bus fusion and
final action selection in QuintBioRAGAgent.

Biology:
  The prefrontal cortex does NOT decide what action to take.
  The limbic system (Bandit + BioRAG) already wants to act.
  The PFC evaluates: should I act on that impulse RIGHT NOW?

  Three functions:
    1. Consequence modeling  — if I'm wrong, how bad?
    2. Novelty gating        — am I in familiar or novel territory?
    3. Escalation logic      — when to pause and surface to human

Architecture fit:
  Reads from:  PEE (uncertainty), TFE (novelty), CME (constraint confidence)
  Outputs:     PFCVerdict — PROCEED / SLOW / ESCALATE
  Sits in:     choose() — AFTER signal bus fusion, BEFORE Bandit samples

  The Bandit still makes the final call.
  PFC just adjusts the weights and attaches a verdict the caller can act on.

  ESCALATE does not mean the agent crashes or refuses.
  It means: here is my best action AND a flag saying "human should review this."
  The caller (Witch Bridge Executive loop) decides what to do with that flag.

Key design principle:
  PFC is READ-ONLY at decision time.
  It observes pillar state, computes a verdict, adjusts weights.
  It does NOT modify memory, posteriors, or TFE state.
  Those are update() responsibilities.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from collections import deque


# ─────────────────────────────────────────────────────────────
# VERDICT — the PFC's output signal
# ─────────────────────────────────────────────────────────────

class PFCVerdict(Enum):
    """
    Three-state output. Maps to biological PFC inhibition levels.

    PROCEED   — familiar territory, confidence acceptable, act normally
    SLOW      — novelty or uncertainty detected, reduce action weights
                on low-confidence actions, prefer conservative options
    ESCALATE  — uncertainty + high stakes, surface to oversight layer
                agent still acts (best guess) but flags for human review
    """
    PROCEED   = "PROCEED"
    SLOW      = "SLOW"
    ESCALATE  = "ESCALATE"


@dataclass
class PFCSignal:
    """
    Full output of one PFC evaluation cycle.

    verdict           : what the PFC recommends
    consequence_risk  : estimated badness-if-wrong (0=safe, 1=catastrophic)
    novelty_score     : how unfamiliar is this context (0=known, 1=unseen)
    uncertainty_score : how uncertain is the agent right now (0=confident, 1=blind)
    adjusted_weights  : action weights after PFC dampening (feed these to Bandit)
    rationale         : human-readable reason for verdict
    stakes            : what domain-level risk was detected
    """
    verdict:           PFCVerdict
    consequence_risk:  float
    novelty_score:     float
    uncertainty_score: float
    adjusted_weights:  Dict[str, float]
    rationale:         str
    stakes:            str = "standard"


# ─────────────────────────────────────────────────────────────
# PFC CONFIG — thresholds that define the operating envelope
# ─────────────────────────────────────────────────────────────

@dataclass
class PFCConfig:
    """
    Tunable thresholds. Different domains need different calibration.

    Medical domain  : lower escalate_threshold (less tolerance for uncertainty)
    Coding domain   : higher novelty_tolerance (exploration is fine)
    Legal domain    : lower consequence_ceiling (errors are expensive)

    This is how domain loading will work — swap the config, same PFC.
    """
    # Novelty gating
    novelty_slow_threshold:     float = 0.5   # novelty above this → SLOW
    novelty_escalate_threshold: float = 0.8   # novelty above this (+ high stakes) → ESCALATE

    # Uncertainty gating
    uncertainty_slow_threshold:     float = 0.6   # uncertainty above this → SLOW
    uncertainty_escalate_threshold: float = 0.85  # uncertainty above this → ESCALATE

    # Consequence gating
    consequence_ceiling: float = 0.75  # consequence_risk above this → forces ESCALATE review

    # Weight dampening when SLOW
    slow_dampen_factor:  float = 0.4   # multiply uncertain action weights by this
    slow_floor:          float = 0.05  # minimum weight after dampening

    # History for novelty estimation
    context_memory_size: int = 200     # how many recent contexts to remember

    # Stakes detection: CME constraint density above this = "high stakes"
    high_stakes_cme_threshold: float = 0.6

    # Minimum Bandit evidence before PFC trusts confidence scores
    min_evidence_steps: int = 10


# ─────────────────────────────────────────────────────────────
# PREFRONTAL CORTEX ENGINE
# ─────────────────────────────────────────────────────────────

class PFCEngine:
    """
    Pillar 6 — Prefrontal Cortex.

    Instantiate once inside QuintBioRAGAgent.
    Call evaluate() inside choose() after signal bus fusion.

    Args:
        config: PFCConfig — operating thresholds (swap for domain loading)
    """

    def __init__(self, config: Optional[PFCConfig] = None):
        self.config = config or PFCConfig()

        # Rolling context history for novelty estimation
        # Stores frozenset(context.items()) → count seen
        self._context_counts: Dict[frozenset, int] = {}
        self._context_history: deque = deque(maxlen=self.config.context_memory_size)

        # Running stats for self-monitoring
        self._total_evaluations: int = 0
        self._verdict_counts: Dict[str, int] = {v.value: 0 for v in PFCVerdict}
        self._escalation_log: deque = deque(maxlen=50)  # last 50 escalations

    # ─────────────────────────────────────────────
    # MAIN EVALUATION — called in choose()
    # ─────────────────────────────────────────────

    def evaluate(
        self,
        context:        Dict[str, str],
        actions:        List[str],
        fused_weights:  Dict[str, float],
        bandit_posteriors: Dict[str, Any],   # {action: BetaParams}
        cme_hard_blocks:   Dict[str, bool],  # from CME bias surface
        tfe_novelty_hint:  float = 0.0,      # 0=familiar, 1=all keys orphaned
    ) -> PFCSignal:
        """
        Core PFC evaluation. Called AFTER signal bus fusion, BEFORE Bandit samples.

        Parameters
        ----------
        context           : current condition dict
        actions           : available actions
        fused_weights     : output of QuintSignalBus.fuse()
        bandit_posteriors : current Beta posteriors for this context
        cme_hard_blocks   : which actions CME flagged as dangerous
        tfe_novelty_hint  : TFE-derived novelty signal (fraction of orphaned keys)

        Returns
        -------
        PFCSignal with verdict and adjusted weights
        """
        self._total_evaluations += 1

        # ── 1. Novelty Score ──────────────────────────────────────────
        # How unfamiliar is this context?
        # Combines TFE orphan signal with context frequency history.
        context_key = frozenset(context.items())
        seen_count  = self._context_counts.get(context_key, 0)

        if seen_count == 0:
            # Never seen this exact context
            frequency_novelty = 1.0
        else:
            # Decay: contexts seen many times are familiar
            frequency_novelty = max(0.0, 1.0 - math.log(1 + seen_count) / math.log(1 + 50))

        # Blend TFE hint with frequency novelty (TFE is more precise)
        novelty_score = 0.4 * frequency_novelty + 0.6 * tfe_novelty_hint
        novelty_score = min(1.0, novelty_score)

        # ── 2. Uncertainty Score ──────────────────────────────────────
        # How uncertain is the agent about this context?
        # Reads Bandit posterior evidence depth.
        uncertainty_score = self._compute_uncertainty(actions, bandit_posteriors)

        # ── 3. Consequence Risk ───────────────────────────────────────
        # If the agent is wrong here, how bad is it?
        # Proxied by: CME constraint density + action weight spread
        consequence_risk = self._compute_consequence_risk(
            actions, fused_weights, cme_hard_blocks
        )

        # ── 4. Stakes Detection ───────────────────────────────────────
        # High stakes = many CME constraints active in this context
        cme_block_fraction = sum(1 for v in cme_hard_blocks.values() if v) / max(1, len(actions))
        high_stakes = cme_block_fraction >= self.config.high_stakes_cme_threshold
        stakes_label = "high" if high_stakes else "standard"

        # ── 5. Verdict Logic ──────────────────────────────────────────
        verdict, rationale = self._compute_verdict(
            novelty_score, uncertainty_score, consequence_risk, high_stakes
        )

        # ── 6. Weight Adjustment ──────────────────────────────────────
        # PFC adjusts weights based on verdict
        adjusted_weights = self._adjust_weights(
            verdict, actions, fused_weights, bandit_posteriors, cme_hard_blocks
        )

        # ── 7. Update Context Memory ──────────────────────────────────
        self._context_counts[context_key] = seen_count + 1
        self._context_history.append(context_key)

        # ── 8. Stats ──────────────────────────────────────────────────
        self._verdict_counts[verdict.value] += 1
        if verdict == PFCVerdict.ESCALATE:
            self._escalation_log.append({
                "context": dict(context),
                "novelty": round(novelty_score, 3),
                "uncertainty": round(uncertainty_score, 3),
                "consequence": round(consequence_risk, 3),
                "rationale": rationale,
            })

        return PFCSignal(
            verdict=verdict,
            consequence_risk=round(consequence_risk, 4),
            novelty_score=round(novelty_score, 4),
            uncertainty_score=round(uncertainty_score, 4),
            adjusted_weights=adjusted_weights,
            rationale=rationale,
            stakes=stakes_label,
        )

    # ─────────────────────────────────────────────
    # INTERNAL COMPUTATIONS
    # ─────────────────────────────────────────────

    def _compute_uncertainty(
        self,
        actions: List[str],
        posteriors: Dict[str, Any],
    ) -> float:
        """
        Uncertainty = how little evidence the Bandit has.

        High uncertainty: posteriors are thin (few observations).
        Low uncertainty: posteriors are well-informed (many observations).

        Uses the total observation count across all actions.
        Empty posteriors → maximum uncertainty.
        """
        if not posteriors:
            return 1.0

        total_observations = 0
        for act in actions:
            if act in posteriors:
                p = posteriors[act]
                # BetaParams: alpha + beta = prior(2) + observations
                total_observations += (p.alpha + p.beta - 2.0)

        # Log scale: 0 obs = 1.0, 10 obs = ~0.5, 50 obs = ~0.2, 200+ obs = ~0.0
        uncertainty = max(0.0, 1.0 - math.log(1 + total_observations) / math.log(1 + 200))
        return uncertainty

    def _compute_consequence_risk(
        self,
        actions: List[str],
        fused_weights: Dict[str, float],
        cme_hard_blocks: Dict[str, bool],
    ) -> float:
        """
        Consequence risk = how dangerous is it to be wrong here?

        Two signals:
          1. CME has flagged dangerous actions — risk is elevated
          2. Fused weights are clustered (agent is committed to one action) —
             if that action is wrong, there's no fallback

        Spread metric: high spread = many plausible options = lower risk of being trapped
        Low spread (agent committed to one action) = higher consequence if wrong
        """
        # CME constraint pressure
        n_blocked = sum(1 for v in cme_hard_blocks.values() if v)
        cme_risk = n_blocked / max(1, len(actions))

        # Weight concentration risk (how committed is the agent?)
        weights = [fused_weights.get(a, 1.0) for a in actions]
        if len(weights) <= 1:
            concentration_risk = 0.5
        else:
            w_max = max(weights)
            w_sum = sum(weights)
            # Herfindahl-like concentration: if one action dominates, risk is higher
            concentration = (w_max / w_sum) if w_sum > 0 else 1.0
            # High concentration alone isn't bad — it's bad when combined with uncertainty
            # So we use it as a moderate signal
            concentration_risk = concentration * 0.5

        # Blend: CME risk weighted more heavily (it's domain knowledge)
        consequence_risk = 0.65 * cme_risk + 0.35 * concentration_risk
        return min(1.0, consequence_risk)

    def _compute_verdict(
        self,
        novelty:     float,
        uncertainty: float,
        consequence: float,
        high_stakes: bool,
    ) -> Tuple[PFCVerdict, str]:
        """
        Verdict logic — biological: PFC inhibits when novelty + stakes exceed threshold.

        Priority order:
          1. ESCALATE conditions (highest priority)
          2. SLOW conditions
          3. PROCEED (default)
        """
        cfg = self.config

        # ── ESCALATE conditions ───────────────────────────────────────
        # Condition A: extreme uncertainty regardless of domain
        if uncertainty >= cfg.uncertainty_escalate_threshold:
            return PFCVerdict.ESCALATE, (
                f"Extreme uncertainty ({uncertainty:.2f}) — "
                f"insufficient evidence to act with confidence"
            )

        # Condition B: high novelty + high stakes together
        if novelty >= cfg.novelty_escalate_threshold and high_stakes:
            return PFCVerdict.ESCALATE, (
                f"Novel context ({novelty:.2f}) in high-stakes domain — "
                f"escalating to oversight before acting"
            )

        # Condition C: high consequence risk + meaningful uncertainty
        if consequence >= cfg.consequence_ceiling and uncertainty >= cfg.uncertainty_slow_threshold:
            return PFCVerdict.ESCALATE, (
                f"High consequence risk ({consequence:.2f}) with uncertainty ({uncertainty:.2f}) — "
                f"cost of error too high to proceed autonomously"
            )

        # ── SLOW conditions ───────────────────────────────────────────
        # Condition D: notable novelty
        if novelty >= cfg.novelty_slow_threshold:
            return PFCVerdict.SLOW, (
                f"Novelty detected ({novelty:.2f}) — "
                f"dampening low-confidence actions"
            )

        # Condition E: meaningful uncertainty
        if uncertainty >= cfg.uncertainty_slow_threshold:
            return PFCVerdict.SLOW, (
                f"Uncertainty elevated ({uncertainty:.2f}) — "
                f"preferring conservative actions"
            )

        # ── PROCEED ───────────────────────────────────────────────────
        return PFCVerdict.PROCEED, (
            f"Familiar context, acceptable uncertainty — proceeding normally"
        )

    def _adjust_weights(
        self,
        verdict:         PFCVerdict,
        actions:         List[str],
        fused_weights:   Dict[str, float],
        posteriors:      Dict[str, Any],
        cme_hard_blocks: Dict[str, bool],
    ) -> Dict[str, float]:
        """
        Translate verdict into concrete weight adjustments.

        PROCEED   → weights unchanged
        SLOW      → dampen actions with low Bandit confidence
                    (actions with thin posteriors get reduced weight)
        ESCALATE  → strongly dampen ALL low-confidence actions,
                    boost the single safest option (highest posterior mean)
                    so the agent still acts but conservatively
        """
        if verdict == PFCVerdict.PROCEED:
            return dict(fused_weights)

        cfg = self.config
        adjusted = dict(fused_weights)

        if verdict == PFCVerdict.SLOW:
            # Dampen actions with thin evidence
            for act in actions:
                if act in posteriors:
                    p = posteriors[act]
                    observations = (p.alpha + p.beta - 2.0)
                    if observations < cfg.min_evidence_steps:
                        # Low evidence → dampen
                        adjusted[act] = max(
                            cfg.slow_floor,
                            adjusted.get(act, 1.0) * cfg.slow_dampen_factor
                        )
                else:
                    # No evidence at all → dampen to floor
                    adjusted[act] = cfg.slow_floor

        elif verdict == PFCVerdict.ESCALATE:
            # Find the safest known action (highest posterior mean, not CME-blocked)
            best_act = None
            best_mean = -1.0

            for act in actions:
                if cme_hard_blocks.get(act, False):
                    continue  # skip explicitly dangerous actions
                if act in posteriors:
                    p = posteriors[act]
                    mean = p.alpha / (p.alpha + p.beta)
                    obs  = p.alpha + p.beta - 2.0
                    # Weight mean by evidence — uncertain mean counts less
                    evidence_factor = min(1.0, obs / cfg.min_evidence_steps)
                    adjusted_mean = mean * evidence_factor
                    if adjusted_mean > best_mean:
                        best_mean = adjusted_mean
                        best_act  = act

            # Dampen everything, then boost the safest known action
            for act in actions:
                adjusted[act] = cfg.slow_floor

            if best_act:
                adjusted[best_act] = 1.0  # full weight on safest known option

        # Normalize: keep weights in [slow_floor, 1.0]
        mx = max(adjusted.values()) if adjusted else 1.0
        if mx > 0:
            adjusted = {a: max(cfg.slow_floor, v / mx) for a, v in adjusted.items()}

        return adjusted

    # ─────────────────────────────────────────────
    # DOMAIN LOADING HOOK
    # ─────────────────────────────────────────────

    def load_domain_config(self, config: PFCConfig) -> None:
        """
        Swap operating thresholds for a new domain.

        This is the domain differentiation hook.
        Call this when loading a new glyph set.
        Does NOT reset context memory — learned familiarity is preserved.

        Usage:
            pfc.load_domain_config(MEDICAL_PFC_CONFIG)
            pfc.load_domain_config(LEGAL_PFC_CONFIG)
            pfc.load_domain_config(CODING_PFC_CONFIG)
        """
        self.config = config

    def reset_context_memory(self) -> None:
        """
        Wipe novelty history. Use when entering a completely new domain
        where past context familiarity is irrelevant.
        """
        self._context_counts.clear()
        self._context_history.clear()

    # ─────────────────────────────────────────────
    # DIAGNOSTICS
    # ─────────────────────────────────────────────

    def get_stats(self) -> Dict[str, Any]:
        """Telemetry for Witch Bridge Cortex panel."""
        total = max(1, self._total_evaluations)
        return {
            "total_evaluations":   self._total_evaluations,
            "verdict_proceed_pct": round(self._verdict_counts["PROCEED"]   / total * 100, 1),
            "verdict_slow_pct":    round(self._verdict_counts["SLOW"]      / total * 100, 1),
            "verdict_escalate_pct":round(self._verdict_counts["ESCALATE"]  / total * 100, 1),
            "unique_contexts_seen":len(self._context_counts),
            "recent_escalations":  len(self._escalation_log),
            "last_escalation":     self._escalation_log[-1] if self._escalation_log else None,
        }

    def get_escalation_log(self) -> list:
        """Full escalation history for audit trail / NoesisCards integration."""
        return list(self._escalation_log)


# ─────────────────────────────────────────────────────────────
# PRESET DOMAIN CONFIGS
# Domain loading is just swapping the config.
# Glyphs map to these presets.
# ─────────────────────────────────────────────────────────────

CODING_PFC_CONFIG = PFCConfig(
    novelty_slow_threshold=0.7,       # coders explore — higher tolerance
    novelty_escalate_threshold=0.95,
    uncertainty_slow_threshold=0.7,
    uncertainty_escalate_threshold=0.9,
    consequence_ceiling=0.85,         # mistakes are recoverable
    slow_dampen_factor=0.5,
    high_stakes_cme_threshold=0.7,
)

MEDICAL_PFC_CONFIG = PFCConfig(
    novelty_slow_threshold=0.3,       # any novelty in medical = caution
    novelty_escalate_threshold=0.6,
    uncertainty_slow_threshold=0.4,
    uncertainty_escalate_threshold=0.7,
    consequence_ceiling=0.5,          # errors cost lives
    slow_dampen_factor=0.2,           # heavy dampening
    high_stakes_cme_threshold=0.3,    # most medical decisions are high stakes
)

LEGAL_PFC_CONFIG = PFCConfig(
    novelty_slow_threshold=0.35,
    novelty_escalate_threshold=0.65,
    uncertainty_slow_threshold=0.45,
    uncertainty_escalate_threshold=0.75,
    consequence_ceiling=0.55,         # legal errors are expensive
    slow_dampen_factor=0.25,
    high_stakes_cme_threshold=0.4,
)

FINANCIAL_PFC_CONFIG = PFCConfig(
    novelty_slow_threshold=0.4,
    novelty_escalate_threshold=0.7,
    uncertainty_slow_threshold=0.5,
    uncertainty_escalate_threshold=0.8,
    consequence_ceiling=0.6,
    slow_dampen_factor=0.3,
    high_stakes_cme_threshold=0.45,
)

# Registry: maps glyph domain tags to configs
# When DomainLoader activates a glyph, it looks up the config here
DOMAIN_CONFIG_REGISTRY = {
    "coding":    CODING_PFC_CONFIG,
    "medical":   MEDICAL_PFC_CONFIG,
    "legal":     LEGAL_PFC_CONFIG,
    "financial": FINANCIAL_PFC_CONFIG,
    "default":   PFCConfig(),  # base config
}
