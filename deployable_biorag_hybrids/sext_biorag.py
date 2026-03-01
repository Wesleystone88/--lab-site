"""
Sext-BioRAG Agent — The 6th Generation (Prefrontal Cortex)
============================================================
Cognitive Architecture: 6 Pillars

  Pillar 1 — CME  (Constrained Memory Engine)   : Declarative Memory
  Pillar 2 — TS   (Thompson Sampling Bandit)     : Procedural Instinct
  Pillar 3 — TFE  (Temporal Field Engine)        : Temporal Awareness
  Pillar 4 — PEE  (Prediction Error Engine)      : Dopamine System
  Pillar 5 — BioRAG (Biological RAG)             : Episodic Memory
  Pillar 6 — PFC  (Prefrontal Cortex)            : Impulse Control +
                                                    Self-Calibration

Subclasses QuintBioRAGAgent unchanged — all 5-pillar logic preserved.
Overrides choose_action() and update() to wire in PFC.

Key wiring points:
  choose_action():
    [P1-P5 signals] → [MetacogAwareSignalBus.fuse()] → [PFC.evaluate()] → [Bandit samples]
                        ↑ trust multipliers                ↑ adjusted weights
                        from metacog                        fed to Bandit

  update():
    [P1-P5 learn] → [MetacognitiveMonitor.log_decision()]
"""

import sys
import os
import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

# ── Path setup so we can import from both sandbox_hybrid/ and 01_Core/ ──
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_SANDBOX  = os.path.join(os.path.dirname(_THIS_DIR), "sandbox_hybrid")
_PFC_DIR  = os.path.join(_SANDBOX, "pfc")

for _p in [_THIS_DIR, _SANDBOX, _PFC_DIR]:
    if _p not in sys.path:
        pass  # sys.path.insert block removed for deployability

# ── Core imports ──
from quint_biorag import (
    QuintBioRAGAgent, BioRAG, SparseEncoder, RAGInterface,
    InternalSignalBus,
)
from quint_hybrid import (
    PillarSignal, QuintSignalBus, QuintPEE,
    KeyStateClass,
)
from halcyon_research_demo import BiasSurface
from Bandit_engine.state import BetaParams

# ── PFC imports ──
from pfc_engine import (
    PFCEngine, PFCConfig, PFCSignal, PFCVerdict,
    DOMAIN_CONFIG_REGISTRY,
)
from metacognitive_monitor import (
    MetacognitiveMonitor, MetacogAwareSignalBus,
    DecisionRecord as MetacogDecisionRecord,
    MetacogConfig,
    METACOG_DOMAIN_REGISTRY,
)

# Phase 28 residue — optional
try:
    from metabolic_residue import ResidueConfig
except ImportError:
    ResidueConfig = None


# ============================================================
# SEXT-BIORAG AGENT (6 Pillars)
# ============================================================

class SextBioRAGAgent(QuintBioRAGAgent):
    """
    6-pillar agent. Drop-in replacement for QuintBioRAGAgent.

    Adds:
      Pillar 6a: PFCEngine          — impulse control (PROCEED / SLOW / ESCALATE)
      Pillar 6b: MetacognitiveMonitor — self-calibration (per-pillar trust adjustment)

    The signal bus is replaced with MetacogAwareSignalBus which applies
    trust multipliers from the metacog monitor during fusion.

    New methods:
      load_domain(domain)     — swap PFC + metacog configs for a domain
      get_pillar6_stats()     — combined PFC telemetry
    """

    def __init__(
        self,
        seed: int = 42,
        tfe_tau: float = 3600.0,
        pee_kwargs: Optional[dict] = None,
        rag: Optional[RAGInterface] = None,
        sham_pe: bool = False,
        biorag_kwargs: Optional[dict] = None,
        residue_config=None,
        adaptive_encoding_enabled: bool = False,
        # Pillar 6 config
        pfc_config: Optional[PFCConfig] = None,
        metacog_config: Optional[MetacogConfig] = None,
    ):
        # Initialize the 5-pillar base
        super().__init__(
            seed=seed,
            tfe_tau=tfe_tau,
            pee_kwargs=pee_kwargs,
            rag=rag,
            sham_pe=sham_pe,
            biorag_kwargs=biorag_kwargs,
            residue_config=residue_config,
            adaptive_encoding_enabled=adaptive_encoding_enabled,
        )

        # ── Pillar 6a: PFC — Impulse Control ──
        self.pfc = PFCEngine(config=pfc_config)

        # ── Pillar 6b: Metacognitive Monitor — Self-Calibration ──
        self.metacog = MetacognitiveMonitor(config=metacog_config)

        # ── Replace signal bus with metacog-aware version ──
        # Trust multipliers are now applied during fusion automatically
        self.bus = MetacogAwareSignalBus(self.metacog)

        # ── State for pillar attribution in update() ──
        self._last_pillar_signals: Dict[str, float] = {}
        self._last_pfc_signal: Optional[PFCSignal] = None

    # ─────────────────────────────────────────────
    # ACTION SELECTION — overrides QuintBioRAGAgent
    # ─────────────────────────────────────────────

    def choose(self, condition: Dict[str, str], actions: List[str]) -> str:
        """Convenience wrapper: returns just the action string."""
        result = self.choose_action(condition, actions)
        if isinstance(result, tuple):
            return result[0]
        return result

    def choose_action(
        self, condition: Dict[str, str], actions: List[str]
    ) -> Tuple[str, str]:
        """
        6-pillar flow: inherits the Phase 28 intake gate from QuintBioRAG,
        then injects PFC evaluation between fusion and Bandit sampling.

        Returns (action, source) where source indicates which pillar drove
        the decision.
        """
        # ── Phase 28: Metabolic Residue Gate (from parent) ──
        is_intake_decision = set(actions) == {'ACCEPT', 'REJECT'}
        if is_intake_decision:
            from metabolic_residue import sha256_hex, normalize_text
            candidate_text = str(condition)
            c_hash_val = sha256_hex(normalize_text(candidate_text))
            c_hash = self.residue_reservoir._by_hash.get(c_hash_val)
            if c_hash:
                return 'REJECT', 'Gate_Duplicate'

            alert = self.residue_reservoir.pressure.alert_level()
            if alert == "CRITICAL" and len(candidate_text) < 40:
                return 'REJECT', 'Gate_LowQuality'

        ctx_key = self._context_key(condition)

        # ── Pillar 3: TFE — temporal decay signals ──
        for act in actions:
            self.tfe.open_key(f"{ctx_key}|{act}")

        obs = self.last_tfe_observables
        tfe_weights: Dict[str, float] = {}
        tfe_confidence = 0.0

        for act in actions:
            tfe_key_act = f"{ctx_key}|{act}"
            w = 1.0
            if obs and tfe_key_act in obs.key_states:
                s = obs.key_states[tfe_key_act]
                if s == KeyStateClass.ORPHANED:
                    w = 0.1; tfe_confidence = max(tfe_confidence, 0.9)
                elif s == KeyStateClass.ABANDONED:
                    w = 0.5; tfe_confidence = max(tfe_confidence, 0.6)
                elif s == KeyStateClass.PENDING:
                    w = 0.8; tfe_confidence = max(tfe_confidence, 0.3)
            if tfe_key_act in self.tfe.state.duration_anomalies:
                if self.tfe.state.duration_anomalies[tfe_key_act].timeouts_fallback > 0:
                    w = 0.05; tfe_confidence = 0.95
            tfe_weights[act] = w

        tfe_signal = PillarSignal(
            action_weights=tfe_weights,
            confidence=tfe_confidence,
            pillar_name="TFE",
        )

        # ── Pillar 1: CME — constraint memory bias ──
        bias = self.cme.emit_bias(condition, actions)
        cme_weights: Dict[str, float] = {}
        cme_confidence = 0.0

        for act in actions:
            w = bias.weights.get(act, 1.0)
            if bias.hard_blocks.get(act, False):
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

        # ── Pillar 5: BioRAG — episodic retrieval ──
        rag_signal = self.rag.retrieve(condition, actions)

        # [P6b] Log BioRAG retrieval quality for metacog
        self.metacog.log_biorag_quality(rag_signal.confidence)

        # ── Signal Bus — fuse with metacog trust multipliers ──
        fused_weights = self.bus.fuse(
            [tfe_signal, cme_signal, rag_signal],
            actions
        )

        # ── Pillar 4: PEE — lock prediction BEFORE action ──
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

        # ── Pillar 6a: PFC — impulse control gate ──
        # Compute TFE novelty hint (fraction of orphaned keys in this context)
        n_orphaned = sum(
            1 for a in actions
            if obs and f"{ctx_key}|{a}" in obs.key_states
            and obs.key_states[f"{ctx_key}|{a}"] == KeyStateClass.ORPHANED
        )
        tfe_novelty_hint = n_orphaned / max(1, len(actions))

        pfc_signal = self.pfc.evaluate(
            context=condition,
            actions=actions,
            fused_weights=fused_weights,
            bandit_posteriors=posteriors,
            cme_hard_blocks=bias.hard_blocks,
            tfe_novelty_hint=tfe_novelty_hint,
        )

        # ── Pillar 2: Bandit — sample from PFC-adjusted weights ──
        action, source, did_explore = self.bandit.get_action(
            ctx_key, actions,
            cme_blocks=None,
            cme_weights=pfc_signal.adjusted_weights,  # PFC output
            tfe_decays={a: 1.0 for a in actions},
        )

        # [P6b] Log explore events for metacog
        self.metacog.log_bandit_explore(source == "explore")

        # Store pillar confidences for attribution in update()
        self._last_pillar_signals = {
            "CME":    cme_signal.confidence,
            "TFE":    tfe_signal.confidence,
            "BioRAG": rag_signal.confidence,
        }
        self._last_pfc_signal = pfc_signal

        # ── Decision log (Phase 28 A1) ──
        cme_blocked = [a for a, v in bias.hard_blocks.items() if v]
        cme_softened = {a: round(w, 3) for a, w in bias.weights.items() if w < 1.0}
        q_values = {}
        for act in actions:
            if act in posteriors:
                p = posteriors[act]
                q_values[act] = round(p.alpha / (p.alpha + p.beta), 3)
            else:
                q_values[act] = 0.5

        trace_entry = {
            "step": None,
            "context": dict(condition),
            "chosen_action": action,
            "source": source,
            "pillars": {
                "CME": {"blocked": cme_blocked, "softened": cme_softened},
                "Bandit": {"Q_values": q_values},
                "TFE": {"novelty_hint": round(tfe_novelty_hint, 3)},
                "PEE": {},
                "BioRAG": {"confidence": round(rag_signal.confidence, 3)},
                "PFC": {
                    "verdict": pfc_signal.verdict.value,
                    "novelty": round(pfc_signal.novelty_score, 3),
                    "uncertainty": round(pfc_signal.uncertainty_score, 3),
                    "consequence": round(pfc_signal.consequence_risk, 3),
                    "rationale": pfc_signal.rationale,
                },
            },
            "pfc_adjusted_weights": {a: round(w, 3) for a, w in pfc_signal.adjusted_weights.items()},
        }
        self.decision_log.append(trace_entry)

        return action, source

    # ─────────────────────────────────────────────
    # UPDATE — overrides QuintBioRAGAgent
    # ─────────────────────────────────────────────

    def update(self, condition: Dict[str, str], action: str, success: bool, step: int):
        """
        6-pillar update. Runs the full 5-pillar update from parent,
        then logs the decision to the metacog monitor for attribution
        and periodic self-calibration review.
        """
        # Run the full 5-pillar update (CME, Bandit, TFE, PEE, BioRAG)
        super().update(condition, action, success, step)

        # ── Pillar 6b: Metacog — log decision for self-calibration ──
        pfc_sig = self._last_pfc_signal
        record = MetacogDecisionRecord(
            step=step,
            context_key=self._context_key(condition),
            action=action,
            success=success,
            pillar_signals=self._last_pillar_signals,
            pfc_verdict=pfc_sig.verdict.value if pfc_sig else "PROCEED",
            novelty_score=pfc_sig.novelty_score if pfc_sig else 0.0,
            uncertainty_score=pfc_sig.uncertainty_score if pfc_sig else 0.0,
        )
        adjustment_report = self.metacog.log_decision(record)

        # If metacog ran a review and made adjustments, log it
        if adjustment_report and adjustment_report.get('adjustments'):
            self.decision_log.append({
                "step": step,
                "event": "metacog_adjustment",
                "adjustments": adjustment_report['adjustments'],
                "trust_scores": self.metacog.get_all_trust(),
            })

    # ─────────────────────────────────────────────
    # DOMAIN LOADING
    # ─────────────────────────────────────────────

    def load_domain(self, domain: str, reset_context_memory: bool = False) -> None:
        """
        Load domain config into both PFC halves simultaneously.
        Same brain, different governance envelope.

        Medical → tight thresholds, fast ESCALATE
        Coding  → loose thresholds, more exploration
        Legal   → moderate, heavy dampening
        """
        pfc_config = DOMAIN_CONFIG_REGISTRY.get(
            domain, DOMAIN_CONFIG_REGISTRY['default']
        )
        metacog_config = METACOG_DOMAIN_REGISTRY.get(
            domain, METACOG_DOMAIN_REGISTRY['default']
        )

        self.pfc.load_domain_config(pfc_config)
        self.metacog.load_domain_config(metacog_config)

        if reset_context_memory:
            self.pfc.reset_context_memory()

    # ─────────────────────────────────────────────
    # DIAGNOSTICS
    # ─────────────────────────────────────────────

    def get_pfc_stats(self) -> Dict[str, Any]:
        """Impulse control telemetry."""
        return self.pfc.get_stats()

    def get_metacog_stats(self) -> Dict[str, Any]:
        """Self-calibration telemetry."""
        return self.metacog.get_stats()

    def get_pillar6_stats(self) -> Dict[str, Any]:
        """Combined Pillar 6 telemetry."""
        return {
            'pfc':     self.pfc.get_stats(),
            'metacog': self.metacog.get_stats(),
            'trust':   self.metacog.get_all_trust(),
        }

    def diagnose_last_decision(self) -> Dict[str, Any]:
        """Extended diagnostics including PFC verdict."""
        base = super().diagnose_last_decision() if hasattr(super(), 'diagnose_last_decision') else {}

        if self._last_pfc_signal:
            sig = self._last_pfc_signal
            base['pfc'] = {
                'verdict': sig.verdict.value,
                'novelty': round(sig.novelty_score, 3),
                'uncertainty': round(sig.uncertainty_score, 3),
                'consequence_risk': round(sig.consequence_risk, 3),
                'rationale': sig.rationale,
                'stakes': sig.stakes,
            }

        base['pillar_trust'] = self.metacog.get_all_trust()
        return base
