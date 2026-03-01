"""
Quint-Hybrid Agent — The 5th Generation
=========================================
Cognitive Architecture: 5 Pillars

  Pillar 1 — CME  (Constrained Memory Engine)   : Declarative Memory
  Pillar 2 — Bandit (Contextual Thompson Sampler): Procedural Logic
  Pillar 3 — TFE  (Time Field Engine)            : Autonomic Physics
  Pillar 4 — PEE  (Prediction Error Engine)      : Dopaminergic Surprise
  Pillar 5 — RAG  (Retrieval-Augmented Guidance) : Semantic Long-term Memory

Key improvements over Quad-Hybrid:
  1. Dynamic Handoff System: All 5 pillars contribute soft-weighted signals
     into a unified SignalBus. The Bandit samples from this fused posterior,
     not from hard-blocked subsets.
  2. Soft CME Authority: CME no longer issues absolute hard-blocks.
     Instead it contributes a soft penalty weight that the Bandit can
     overcome with sufficient statistical confidence.
  3. RAG Stub Interface: The 5th pillar is a pluggable context retrieval
     interface. The stub returns neutral signals; plug in a real vector
     store (FAISS, Chroma, etc.) when ready.
  4. Confidence-Aware Fusion: Each pillar declares how confident it is
     in its signal. A low-confidence pillar's signal is down-weighted in
     the final fused decision.

NOTE — CME UPGRADE TRACK:
  This agent relies on the current CME from halcyon_research_demo.py.
  When CME is upgraded in 02_Version_History, the following must be tested:
    a) Soft-penalty mode performance vs hard-block mode (T1-Structured)
    b) Re-run master_suite_results.csv to regenerate the full baseline
    c) Apply compression improvements specifically to T1-Structured-L5000
  See: QUAD_HYBRID_BLUEPRINT.md and PHASE_B_ANALYSIS.md for context.
"""

import math
import random
from typing import Dict, List, Tuple, Optional, Any
from collections import deque
from dataclasses import dataclass, field

# ── Path setup ───────────────────────────────────────────────────────────────
import sys, os
_here = os.path.dirname(os.path.abspath(__file__))
_sandbox = os.path.join(_here, '..', 'sandbox_hybrid')
for _p in [_here, _sandbox]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tri_hybrid_v3 import TriHybridAgentV3
from Bandit_engine.state import BetaParams
from Time_engine.state import KeyStateClass
from Time_engine.config import TFEConfig


# ============================================================
# SIGNAL BUS — unified data flowing between pillars
# ============================================================

@dataclass
class PillarSignal:
    """What any pillar emits into the signal bus."""
    action_weights: Dict[str, float] = field(default_factory=dict)  # 0.0=veto to 1.0=full trust
    confidence: float = 0.0   # how confident THIS pillar is in its signal (0–1)
    pillar_name: str = "unknown"


@dataclass
class QuintSignal:
    """PEE surprise signal flowing to all downstream pillars."""
    error_magnitude: float
    error_sign: int            # -1=negative surprise, 0=expected, +1=positive surprise
    encoding_weight: float     # multiplier for downstream learning rate
    tfe_reset: bool
    predicted_prob: float
    prediction_confidence: float


# ============================================================
# PILLAR 4: Prediction Error Engine (PEE) — unchanged from Quad
# ============================================================

class QuintPEE:
    """
    Dopaminergic learning rate modulator.
    Reads expectations directly from the Bandit's Beta distribution priors.
    """
    def __init__(self,
                 min_weight: float = 1.0,
                 max_weight: float = 3.0,
                 surprise_threshold: float = 0.15,
                 confidence_weight: float = 0.7):
        self.min_weight = min_weight
        self.max_weight = max_weight
        self.surprise_threshold = surprise_threshold
        self.confidence_weight = confidence_weight
        self._calibration: deque = deque(maxlen=100)
        self._surprise_count = 0
        self._total_weight = 0.0
        self._update_count = 0

    def predict_from_beta(self, alpha: float, beta: float, total_prior: float = 2.0) -> Tuple[float, float]:
        prob = alpha / (alpha + beta)
        attempts = (alpha + beta) - total_prior
        if attempts <= 0:
            return prob, 0.0
        conf = min(1.0, math.log(1 + attempts) / math.log(1 + 50))
        return prob, conf

    def compute(self, prob: float, conf: float, success: bool) -> QuintSignal:
        actual = 1.0 if success else 0.0
        raw_error = actual - prob

        if abs(raw_error) < self.surprise_threshold:
            sign = 0
        elif raw_error > 0:
            sign = 1
        else:
            sign = -1

        mag = min(1.0, abs(raw_error))
        weighted_mag = mag * (self.confidence_weight * conf + (1.0 - self.confidence_weight))

        if sign == 0:
            weight = self.min_weight
        else:
            weight = self.min_weight + (self.max_weight - self.min_weight) * weighted_mag

        tfe_reset = weighted_mag > 0.5

        self._calibration.append(1.0 - mag)
        self._update_count += 1
        self._total_weight += weight
        if sign != 0:
            self._surprise_count += 1

        return QuintSignal(
            error_magnitude=round(weighted_mag, 4),
            error_sign=sign,
            encoding_weight=round(weight, 4),
            tfe_reset=tfe_reset,
            predicted_prob=prob,
            prediction_confidence=conf,
        )

    def get_calibration(self) -> float:
        if not self._calibration:
            return 0.5
        return round(sum(self._calibration) / len(self._calibration), 4)

    def get_stats(self) -> Dict[str, Any]:
        avg_w = self._total_weight / max(1, self._update_count)
        return {
            "surprise_events": self._surprise_count,
            "avg_encoding_weight": round(avg_w, 3),
            "calibration": self.get_calibration(),
        }


# ============================================================
# PILLAR 5: RAG (Retrieval-Augmented Guidance) — STUB
# ============================================================

class RAGInterface:
    """
    Semantic long-term memory retrieval interface.

    This is the integration point for a vector store (FAISS, Chroma, etc.).
    The stub returns neutral signals (all actions equally plausible).

    To activate:
      1. Override `retrieve(context, actions)` in a subclass.
      2. Return a PillarSignal with action_weights derived from
         semantic similarity to previously successful episodes.
      3. Pass your subclass instance into QuintHybridAgent(rag=YourRAG()).

    The confidence field controls how strongly the RAG signal
    influences the final Bandit sampling. 0.0 = fully ignored.
    """
    def retrieve(self, context: Dict[str, str], actions: List[str]) -> PillarSignal:
        """Return neutral equal weights. Subclasses override this."""
        return PillarSignal(
            action_weights={a: 1.0 for a in actions},
            confidence=0.0,   # 0 confidence = neutral, won't affect decision
            pillar_name="RAG-Stub",
        )

    def write_back(self, context: Dict[str, str], action: str, success: bool):
        """Store outcome. Subclasses override to persist to a vector store."""
        pass


class SimpleRAG(RAGInterface):
    """
    A simple in-memory RAG implementation using context feature-overlap
    as the similarity metric.

    How it works:
      - write_back(): stores every (context_features, action, success) event
      - retrieve(): when a new context arrives, it finds stored contexts that
        share at least `min_overlap` fraction of features, then computes a
        success rate per action from those matches. Actions with a higher
        historical success rate get boosted weights.

    This is purely local — no vector store required.
    Upgrade path: swap retrieve() to query FAISS/Chroma embeddings.

    Args:
      confidence_max : max confidence the RAG can assert (caps influence)
      min_visits     : minimum matching evidence before confidence is non-zero
      min_overlap    : fraction of context features that must match to count
    """
    def __init__(self,
                 confidence_max: float = 0.5,
                 min_visits: int = 3,
                 min_overlap: float = 0.5):
        self.confidence_max = confidence_max
        self.min_visits = min_visits
        self.min_overlap = min_overlap
        # memory: frozenset(context.items()) -> {action: [successes, total]}
        self._memory: Dict[frozenset, Dict[str, List[int]]] = {}

    def write_back(self, context: Dict[str, str], action: str, success: bool):
        key = frozenset(context.items())
        if key not in self._memory:
            self._memory[key] = {}
        if action not in self._memory[key]:
            self._memory[key][action] = [0, 0]
        self._memory[key][action][1] += 1
        if success:
            self._memory[key][action][0] += 1

    def retrieve(self, context: Dict[str, str], actions: List[str]) -> PillarSignal:
        ctx_features = set(context.items())
        action_scores: Dict[str, List[float]] = {a: [0.0, 0.0] for a in actions}
        match_count = 0

        for mem_key, action_data in self._memory.items():
            mem_features = set(mem_key)
            union = len(ctx_features | mem_features)
            if union == 0:
                continue
            overlap = len(ctx_features & mem_features) / union
            if overlap < self.min_overlap:
                continue
            match_count += 1
            for act, (succ, total) in action_data.items():
                if act in action_scores and total > 0:
                    action_scores[act][0] += succ * overlap
                    action_scores[act][1] += total * overlap

        if match_count == 0:
            return PillarSignal(
                action_weights={a: 1.0 for a in actions},
                confidence=0.0,
                pillar_name="SimpleRAG",
            )

        weights: Dict[str, float] = {}
        total_evidence = 0.0
        for act in actions:
            succ, total = action_scores[act]
            if total >= self.min_visits:
                weights[act] = max(0.05, succ / total)
                total_evidence += total
            else:
                weights[act] = 0.5   # neutral for unseen actions

        # Confidence scales with how much evidence we have, capped at max
        confidence = min(self.confidence_max, total_evidence / (total_evidence + 20))

        return PillarSignal(
            action_weights=weights,
            confidence=confidence,
            pillar_name="SimpleRAG",
        )


# ============================================================
# QUINT SIGNAL BUS — fuses all pillar signals into Bandit inputs
# ============================================================

class QuintSignalBus:
    """
    Fuses PillarSignals from all active pillars into a final
    set of action weights for the Bandit to sample from.

    Each pillar's confidence value gates its influence.
    A pillar with confidence=0 is completely ignored.
    A pillar with confidence=1 has full authority.

    The CME is now a soft bias here — no hard blocks.
    The system can tolerate noisy CME signals without being locked out.
    """
    def fuse(self, signals: List[PillarSignal], actions: List[str]) -> Dict[str, float]:
        """
        Returns fused_weights: action -> final weight scalar
        """
        if not signals:
            return {a: 1.0 for a in actions}

        # Accumulate confidence-weighted votes per action
        fused = {a: 0.0 for a in actions}
        total_confidence = sum(s.confidence for s in signals if s.confidence > 0)

        if total_confidence == 0:
            return {a: 1.0 for a in actions}

        for sig in signals:
            if sig.confidence <= 0:
                continue
            weight_frac = sig.confidence / total_confidence
            for a in actions:
                raw = sig.action_weights.get(a, 1.0)
                fused[a] += weight_frac * raw

        # Normalise to [0.05, 1.0] to prevent total veto
        mx = max(fused.values()) if fused else 1.0
        if mx > 0:
            fused = {a: max(0.05, v / mx) for a, v in fused.items()}
        return fused


# ============================================================
# QUINT-HYBRID AGENT
# ============================================================

class QuintHybridAgent(TriHybridAgentV3):
    """
    The 5th Hybrid: CME (Memory) + Bandit (Logic) + TFE (Physics)
                    + PEE (Dopamine) + RAG (Semantic Retrieval)

    Handoff flow:
      choose_action:
        TFE  -> temporal_signal  (staleness / urgency weights)
        CME  -> memory_signal    (soft bias from constraint memory)
        RAG  -> semantic_signal  (retrieved episode guidance)
        Bus  -> fused_weights    (confidence-weighted fusion)
        PEE  -> lock prediction  (before action is taken)
        Bandit -> sample action  (from fused posterior)

      update:
        PEE  -> compute surprise (magnitude + encoding_weight)
        Bandit -> scale update by encoding_weight
        CME  -> scale memory encoding by encoding_weight
        TFE  -> touch key / activate reset on high surprise
        RAG  -> [hook for future write-back to vector store]
    """

    def __init__(
        self,
        seed: int = 42,
        tfe_tau: float = 3600.0,
        pee_kwargs: Optional[dict] = None,
        rag: Optional[RAGInterface] = None,
        sham_pe: bool = False,
    ):
        super().__init__(seed=seed, tfe_tau=tfe_tau)
        self.pee = QuintPEE(**(pee_kwargs or {}))
        self.rag = rag or RAGInterface()
        self.bus = QuintSignalBus()
        self.sham_pe = sham_pe
        self._sham_rng = random.Random(seed + 77777)
        self._pending_predictions: Dict[str, Tuple[float, float]] = {}

    # ─────────────────────────────────────────────
    # ACTION SELECTION
    # ─────────────────────────────────────────────

    def choose(self, condition: Dict[str, str], actions: List[str]) -> str:
        """Convenience wrapper: returns just the action (no source tuple)."""
        action, _source = self.choose_action(condition, actions)
        return action

    def choose_action(self, condition: Dict[str, str], actions: List[str]) -> Tuple[str, str]:
        ctx_key = self._context_key(condition)

        # ── Pillar 3: TFE — open keys, collect temporal decay signal ──
        for act in actions:
            self.tfe.open_key(f"{ctx_key}|{act}")

        obs = self.last_tfe_observables
        tfe_weights: Dict[str, float] = {}
        tfe_confidence = 0.0

        for act in actions:
            tfe_key = f"{ctx_key}|{act}"
            w = 1.0
            if obs and tfe_key in obs.key_states:
                s = obs.key_states[tfe_key]
                if s == KeyStateClass.ORPHANED:
                    w = 0.1; tfe_confidence = max(tfe_confidence, 0.9)
                elif s == KeyStateClass.ABANDONED:
                    w = 0.5; tfe_confidence = max(tfe_confidence, 0.6)
                elif s == KeyStateClass.PENDING:
                    w = 0.8; tfe_confidence = max(tfe_confidence, 0.3)
            if tfe_key in self.tfe.state.duration_anomalies:
                if self.tfe.state.duration_anomalies[tfe_key].timeouts_fallback > 0:
                    w = 0.05; tfe_confidence = 0.95
            tfe_weights[act] = w

        tfe_signal = PillarSignal(
            action_weights=tfe_weights,
            confidence=tfe_confidence,
            pillar_name="TFE",
        )

        # ── Pillar 1: CME — soft bias from constraint memory ──
        bias = self.cme.emit_bias(condition, actions)
        cme_weights: Dict[str, float] = {}
        cme_confidence = 0.0

        for act in actions:
            w = bias.weights.get(act, 1.0)
            if bias.hard_blocks.get(act, False):
                # Hard block becomes a very strong soft penalty (0.05) not an absolute ban
                w = 0.05
                cme_confidence = max(cme_confidence, 0.8)
            elif w < 1.0:
                cme_confidence = max(cme_confidence, 0.4)
            cme_weights[act] = w

        cme_signal = PillarSignal(
            action_weights=cme_weights,
            confidence=cme_confidence,
            pillar_name="CME",
        )

        # ── Pillar 5: RAG — semantic long-term retrieval ──
        rag_signal = self.rag.retrieve(condition, actions)

        # ── Signal Bus — fuse all signals ──
        fused_weights = self.bus.fuse(
            [tfe_signal, cme_signal, rag_signal],
            actions
        )

        # ── Pillar 4: PEE — lock in prediction BEFORE action ──
        posteriors = self.bandit.state.posteriors.get(ctx_key, {})
        for act in actions:
            if act in posteriors:
                params = posteriors[act]
                prob, conf = self.pee.predict_from_beta(
                    params.alpha, params.beta,
                    total_prior=(self.bandit.config.prior_alpha + self.bandit.config.prior_beta)
                )
            else:
                prob, conf = 0.5, 0.0
            self._pending_predictions[f"{ctx_key}|{act}"] = (prob, conf)

        # ── Pillar 2: Bandit — sample action using fused weights ──
        # No hard_blocks in quint — CME's authority is through soft weights only
        action, source, _ = self.bandit.get_action(
            ctx_key, actions,
            cme_blocks=None,         # No hard veto — CME authority is via soft cme_weights only
            cme_weights=fused_weights,  # Signal bus output drives the Bandit
            tfe_decays={a: 1.0 for a in actions},  # TFE already baked into fused_weights
        )
        return action, source

    # ─────────────────────────────────────────────
    # UPDATE (Outcome Processing)
    # ─────────────────────────────────────────────

    def update(self, condition: Dict[str, str], action: str, success: bool, step: int):
        ctx_key = self._context_key(condition)
        tfe_key = f"{ctx_key}|{action}"

        # ── Pillar 4: PEE — compute surprise from locked prediction ──
        prob, conf = self._pending_predictions.pop(tfe_key, (0.5, 0.0))
        signal = self.pee.compute(prob, conf, success)

        if self.sham_pe:
            signal.encoding_weight = self._sham_rng.uniform(1.0, 3.0)
            signal.tfe_reset = self._sham_rng.random() < 0.15

        # ── Pillar 2: Bandit — scale update by PEE encoding weight ──
        if ctx_key not in self.bandit.state.posteriors:
            self.bandit.state.posteriors[ctx_key] = {}
        if action not in self.bandit.state.posteriors[ctx_key]:
            self.bandit.state.posteriors[ctx_key][action] = BetaParams(
                self.bandit.config.prior_alpha, self.bandit.config.prior_beta
            )

        current = self.bandit.state.posteriors[ctx_key][action]
        if success:
            updated = BetaParams(current.alpha + signal.encoding_weight, current.beta)
        else:
            updated = BetaParams(current.alpha, current.beta + signal.encoding_weight)

        self.bandit.state.posteriors[ctx_key][action] = updated
        self.bandit.state.total_updates += 1
        self.bandit.state.total_steps += 1

        # ── Pillar 1: CME — scale memory encoding by PEE surprise ──
        if not success:
            original_gain = self.cme.reinforce_gain
            self.cme.reinforce_gain = original_gain * signal.encoding_weight
            self.cme.reinforce_memory(
                mem_type="CONSTRAINT",
                condition_subset=condition,
                action=action,
                step=step,
            )
            self.cme.reinforce_gain = original_gain

        self.cme.counter_evidence(
            condition=condition, action=action, success=success, step=step
        )

        # ── Pillar 3: TFE — touch key, activate reset on paradigm shift ──
        if signal.tfe_reset:
            self.tfe.touch_key(tfe_key, magnitude=1.0)
        else:
            self.tfe.touch_key(tfe_key, magnitude=1.0 if success else 0.1)

        # ── Pillar 5: RAG — write outcome back into episode memory ──
        self.rag.write_back(condition, action, success)

    # ─────────────────────────────────────────────
    # DIAGNOSTICS
    # ─────────────────────────────────────────────

    def get_pe_stats(self) -> Dict[str, Any]:
        return self.pee.get_stats()

    def get_stats(self) -> Dict[str, Any]:
        pe = self.get_pe_stats()
        return {
            "surprise_events": pe["surprise_events"],
            "avg_encoding_weight": pe["avg_encoding_weight"],
            "calibration": pe["calibration"],
        }
