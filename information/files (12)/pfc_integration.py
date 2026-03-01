"""
QuintBioRAG + PFC Integration
==============================
How to wire Pillar 6 into QuintBioRAGAgent.

This is NOT a standalone file.
It shows the EXACT changes needed in quint_biorag.py.

Changes required:
  1. Import PFCEngine, PFCConfig, PFCSignal, PFCVerdict
  2. Add pfc to __init__
  3. Modify choose() to call pfc.evaluate() after signal bus fusion
  4. Expose pfc verdict in choose() return value
  5. Add get_pfc_stats() diagnostic
  6. Add load_domain() for domain differentiation

The PFC sits between the signal bus and the Bandit.
It reads. It adjusts weights. It attaches a verdict.
It never writes to memory.
"""

from pfc_engine import (
    PFCEngine, PFCConfig, PFCSignal, PFCVerdict,
    DOMAIN_CONFIG_REGISTRY
)
from typing import Dict, List, Optional, Tuple, Any


# ══════════════════════════════════════════════════════════════
# INTEGRATION DIFF — apply these changes to QuintBioRAGAgent
# ══════════════════════════════════════════════════════════════

class QuintBioRAGWithPFC:
    """
    Drop-in showing the PFC integration pattern.

    In production: apply these changes directly to QuintBioRAGAgent.
    The class below shows the exact method signatures and logic.
    """

    def __init__(
        self,
        seed: int = 42,
        tfe_tau: float = 3600.0,
        pee_kwargs: Optional[dict] = None,
        rag=None,
        sham_pe: bool = False,
        biorag_kwargs: Optional[dict] = None,
        # NEW: PFC config — defaults to base config
        # Swap at runtime for domain loading
        pfc_config: Optional[PFCConfig] = None,
    ):
        # ... existing __init__ ...

        # ── Pillar 6: PFC — Prefrontal Cortex ──
        self.pfc = PFCEngine(config=pfc_config)

    # ─────────────────────────────────────────────
    # MODIFIED choose() — adds PFC evaluation
    # ─────────────────────────────────────────────

    def choose(
        self,
        condition: Dict[str, str],
        actions: List[str],
    ) -> Tuple[str, PFCSignal]:
        """
        Returns: (action, pfc_signal)

        The caller (Witch Bridge Executive loop) receives both:
          - the action to take
          - the PFC's verdict (PROCEED / SLOW / ESCALATE)

        The Executive loop decides what to do with ESCALATE.
        The agent always returns a best-guess action.
        """
        ctx_key = self._context_key(condition)

        # ── Pillars 1,3,5: existing signal collection ──
        tfe_signal  = self._get_tfe_signal(condition, actions, ctx_key)
        cme_signal  = self._get_cme_signal(condition, actions)
        rag_signal  = self.rag.retrieve(condition, actions)

        # ── Signal Bus: fuse ──
        fused_weights = self.bus.fuse(
            [tfe_signal, cme_signal, rag_signal],
            actions
        )

        # ── TFE novelty hint for PFC ──
        # Fraction of action keys that are ORPHANED (never seen or very stale)
        tfe_novelty_hint = self._compute_tfe_novelty(condition, actions, ctx_key)

        # ── Pillar 4: PEE — lock prediction BEFORE PFC and Bandit ──
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

        # ── NEW: Pillar 6: PFC — evaluate BEFORE Bandit samples ──
        from halcyon_research_demo import BiasSurface
        cme_bias = self.cme.emit_bias(condition, actions)

        pfc_signal = self.pfc.evaluate(
            context=condition,
            actions=actions,
            fused_weights=fused_weights,
            bandit_posteriors=posteriors,
            cme_hard_blocks=cme_bias.hard_blocks,
            tfe_novelty_hint=tfe_novelty_hint,
        )

        # ── Pillar 2: Bandit — samples from PFC-ADJUSTED weights ──
        # Key change: Bandit now sees pfc_signal.adjusted_weights
        # not raw fused_weights
        action, source, _ = self.bandit.get_action(
            ctx_key, actions,
            cme_blocks=None,
            cme_weights=pfc_signal.adjusted_weights,  # ← PFC output
            tfe_decays={a: 1.0 for a in actions},
        )

        return action, pfc_signal

    # ─────────────────────────────────────────────
    # TFE NOVELTY HELPER
    # ─────────────────────────────────────────────

    def _compute_tfe_novelty(
        self,
        condition: Dict[str, str],
        actions: List[str],
        ctx_key: str,
    ) -> float:
        """
        Compute novelty hint from TFE state.

        Returns fraction of action keys that are ORPHANED or missing.
        0.0 = all keys are well-established (familiar territory)
        1.0 = all keys are orphaned/unseen (totally novel)
        """
        from Time_engine.state import KeyStateClass
        obs = self.last_tfe_observables
        if not obs:
            return 1.0  # no TFE data = treat as novel

        orphaned = 0
        for act in actions:
            tfe_key = f"{ctx_key}|{act}"
            if tfe_key not in obs.key_states:
                orphaned += 1
            elif obs.key_states[tfe_key] == KeyStateClass.ORPHANED:
                orphaned += 1

        return orphaned / max(1, len(actions))

    # ─────────────────────────────────────────────
    # DOMAIN LOADING — the differentiation hook
    # ─────────────────────────────────────────────

    def load_domain(
        self,
        domain: str,
        reset_context_memory: bool = False,
    ) -> None:
        """
        Load a domain configuration into the PFC.

        This is the stem cell differentiation trigger.
        Same agent, different governance topology.

        Args:
            domain: one of "coding", "medical", "legal", "financial", "default"
                    or pass a custom PFCConfig via load_domain_config()
            reset_context_memory: True = wipe novelty history
                                  False = preserve learned familiarity

        Usage:
            agent.load_domain("medical")   # now operating as medical agent
            agent.load_domain("legal")     # now operating as legal agent
            agent.load_domain("coding")    # back to coding mode

        Note: load_domain does NOT reset:
            - Bandit posteriors (learned action preferences)
            - CME constraints (learned rules)
            - BioRAG hippocampus (episodic memory)

        It ONLY changes PFC thresholds — the governance envelope.
        The brain's knowledge persists. The oversight calibration changes.
        """
        config = DOMAIN_CONFIG_REGISTRY.get(domain, DOMAIN_CONFIG_REGISTRY["default"])
        self.pfc.load_domain_config(config)

        if reset_context_memory:
            self.pfc.reset_context_memory()

    def load_domain_config(self, config: PFCConfig) -> None:
        """Load a custom PFCConfig directly (for fine-tuned domains)."""
        self.pfc.load_domain_config(config)

    # ─────────────────────────────────────────────
    # DIAGNOSTICS
    # ─────────────────────────────────────────────

    def get_pfc_stats(self) -> Dict[str, Any]:
        """
        Telemetry for Witch Bridge Cortex panel.

        Feed this to the Neural Telemetry section.
        ESCALATE rate is your key production health metric.
        """
        return self.pfc.get_stats()

    def get_pfc_escalations(self) -> list:
        """
        Full escalation log for NoesisCards audit trail.

        Each ESCALATE event should become a card in the ledger.
        This is the bridge between the agent and NoesisCards.
        """
        return self.pfc.get_escalation_log()


# ══════════════════════════════════════════════════════════════
# HOW THE EXECUTIVE LOOP HANDLES PFC VERDICTS
# (Witch Bridge side — pseudocode)
# ══════════════════════════════════════════════════════════════

EXECUTIVE_LOOP_PSEUDOCODE = """
# In Witch Bridge Executive Console (TRI-LOBE AUTONOMOUS LOOP):

action, pfc_signal = agent.choose(condition, actions)

if pfc_signal.verdict == PFCVerdict.PROCEED:
    # Normal path — execute action
    execute(action)

elif pfc_signal.verdict == PFCVerdict.SLOW:
    # Cautious path — execute but log the slow signal
    execute(action)
    log_to_cortex(pfc_signal)  # shows in Neural Telemetry

elif pfc_signal.verdict == PFCVerdict.ESCALATE:
    # Oversight path — three options depending on config:
    
    # Option A: Auto-escalate (surface to human, pause loop)
    pause_executive_loop()
    create_noesis_card(
        type="escalation",
        data={
            "action": action,
            "rationale": pfc_signal.rationale,
            "novelty": pfc_signal.novelty_score,
            "uncertainty": pfc_signal.uncertainty_score,
            "consequence_risk": pfc_signal.consequence_risk,
        }
    )
    await_human_decision()
    
    # Option B: Auto-proceed with escalation logged (auditable)
    execute(action)
    create_noesis_card(type="escalation_logged", ...)
    
    # Option C: Route to Advisor lobe for additional reasoning
    advisor_review = advisor_lobe.review(condition, action, pfc_signal)
    execute(advisor_review.approved_action)

# After execution, normal update cycle
agent.update(condition, action, success, step)
"""
