"""
Pillar 6 — Complete Integration Guide
======================================
Shows how pfc_engine.py + metacognitive_monitor.py wire into
QuintBioRAGAgent as a unified Pillar 6.

Pillar 6a: PFCEngine          → impulse control (should I act NOW?)
Pillar 6b: MetacognitiveMonitor → self-calibration (are my pillars trustworthy?)

Together they are the Prefrontal Cortex.
Neither half works without the other.

Changes to QuintBioRAGAgent:
  __init__   : add pfc, metacog, replace bus with MetacogAwareSignalBus
  choose()   : add pfc.evaluate(), log biorag quality, log explore
  update()   : add metacog.log_decision()
  new methods: load_domain(), get_pfc_stats(), get_metacog_stats()
"""

from pfc_engine import (
    PFCEngine, PFCConfig, PFCSignal, PFCVerdict,
    DOMAIN_CONFIG_REGISTRY,
)
from metacognitive_monitor import (
    MetacognitiveMonitor, MetacogAwareSignalBus,
    DecisionRecord, MetacogConfig,
    METACOG_DOMAIN_REGISTRY,
)
from typing import Dict, List, Optional, Tuple, Any


# ══════════════════════════════════════════════════════════════
# __init__ CHANGES
# ══════════════════════════════════════════════════════════════

INIT_DIFF = """
# ADD to QuintBioRAGAgent.__init__() after existing setup:

# ── Pillar 6a: PFC — Impulse Control ──
self.pfc = PFCEngine(config=pfc_config)

# ── Pillar 6b: Metacognitive Monitor — Self-Calibration ──
self.metacog = MetacognitiveMonitor(config=metacog_config)

# ── Replace static bus with metacog-aware bus ──
# Was:  self.bus = QuintSignalBus()
# Now:
self.bus = MetacogAwareSignalBus(self.metacog)

# ── New __init__ signature additions ──
# pfc_config:     Optional[PFCConfig]     = None
# metacog_config: Optional[MetacogConfig] = None
"""


# ══════════════════════════════════════════════════════════════
# choose() CHANGES
# ══════════════════════════════════════════════════════════════

CHOOSE_DIFF = """
# MODIFIED choose() flow:

def choose(self, condition, actions) -> Tuple[str, PFCSignal]:

    ctx_key = self._context_key(condition)

    # [existing] TFE, CME, RAG signals
    tfe_signal = self._get_tfe_signal(condition, actions, ctx_key)
    cme_signal = self._get_cme_signal(condition, actions)
    rag_signal = self.rag.retrieve(condition, actions)

    # [NEW] Log BioRAG retrieval quality to metacog
    self.metacog.log_biorag_quality(rag_signal.confidence)

    # [existing] Signal bus fuse — NOW uses MetacogAwareSignalBus
    # Trust multipliers are applied automatically inside fuse()
    fused_weights = self.bus.fuse([tfe_signal, cme_signal, rag_signal], actions)

    # [existing] PEE prediction lock
    posteriors = self.bandit.state.posteriors.get(ctx_key, {})
    # ... lock predictions ...

    # [NEW] TFE novelty hint for PFC
    tfe_novelty_hint = self._compute_tfe_novelty(condition, actions, ctx_key)

    # [NEW] Pillar 6a: PFC — impulse control gate
    cme_bias = self.cme.emit_bias(condition, actions)
    pfc_signal = self.pfc.evaluate(
        context=condition,
        actions=actions,
        fused_weights=fused_weights,
        bandit_posteriors=posteriors,
        cme_hard_blocks=cme_bias.hard_blocks,
        tfe_novelty_hint=tfe_novelty_hint,
    )

    # [existing] Bandit samples — NOW from PFC-adjusted weights
    action, source, did_explore = self.bandit.get_action(
        ctx_key, actions,
        cme_blocks=None,
        cme_weights=pfc_signal.adjusted_weights,  # ← PFC output
        tfe_decays={a: 1.0 for a in actions},
    )

    # [NEW] Log explore event to metacog
    self.metacog.log_bandit_explore(source == "explore")

    # [NEW] Store pillar signals for attribution in update()
    self._last_pillar_signals = {
        "CME":    cme_signal.confidence,
        "TFE":    tfe_signal.confidence,
        "BioRAG": rag_signal.confidence,
    }
    self._last_pfc_signal = pfc_signal

    return action, pfc_signal
"""


# ══════════════════════════════════════════════════════════════
# update() CHANGES
# ══════════════════════════════════════════════════════════════

UPDATE_DIFF = """
# ADD at the END of update(), after existing logic:

# [NEW] Pillar 6b: Metacog — log decision outcome for self-calibration
pfc_sig = getattr(self, '_last_pfc_signal', None)
record = DecisionRecord(
    step=step,
    context_key=self._context_key(condition),
    action=action,
    success=success,
    pillar_signals=getattr(self, '_last_pillar_signals', {}),
    pfc_verdict=pfc_sig.verdict.value if pfc_sig else 'PROCEED',
    novelty_score=pfc_sig.novelty_score if pfc_sig else 0.0,
    uncertainty_score=pfc_sig.uncertainty_score if pfc_sig else 0.0,
)
adjustment_report = self.metacog.log_decision(record)

# If metacog ran a review cycle, log to NoesisCards
if adjustment_report and adjustment_report.get('adjustments'):
    # Hook point: create an evidence card in NoesisCards
    # self._emit_metacog_card(adjustment_report)
    pass
"""


# ══════════════════════════════════════════════════════════════
# NEW METHODS ON QuintBioRAGAgent
# ══════════════════════════════════════════════════════════════

NEW_METHODS = """
def load_domain(self, domain: str, reset_context_memory: bool = False) -> None:
    '''
    Load domain configuration into both PFC halves simultaneously.
    This is the stem cell differentiation trigger.
    
    Same brain. Different governance envelope.
    '''
    pfc_config    = DOMAIN_CONFIG_REGISTRY.get(domain, DOMAIN_CONFIG_REGISTRY['default'])
    metacog_config = METACOG_DOMAIN_REGISTRY.get(domain, METACOG_DOMAIN_REGISTRY['default'])

    self.pfc.load_domain_config(pfc_config)
    self.metacog.load_domain_config(metacog_config)

    if reset_context_memory:
        self.pfc.reset_context_memory()

def get_pfc_stats(self) -> Dict[str, Any]:
    '''Impulse control telemetry → Witch Bridge Cortex panel.'''
    return self.pfc.get_stats()

def get_metacog_stats(self) -> Dict[str, Any]:
    '''Self-calibration telemetry → Witch Bridge Cortex panel.'''
    return self.metacog.get_stats()

def get_pillar6_stats(self) -> Dict[str, Any]:
    '''Combined Pillar 6 telemetry.'''
    return {
        'pfc':     self.pfc.get_stats(),
        'metacog': self.metacog.get_stats(),
        'trust':   self.metacog.get_all_trust(),
    }
"""


# ══════════════════════════════════════════════════════════════
# WHAT THE CORTEX PANEL SEES
# (Witch Bridge Neural Telemetry feed)
# ══════════════════════════════════════════════════════════════

CORTEX_TELEMETRY_SHAPE = {
    # From PFCEngine
    "pfc_verdict_distribution": {
        "proceed_pct":  "float — % of decisions that proceeded normally",
        "slow_pct":     "float — % of decisions that were dampened",
        "escalate_pct": "float — float — KEY METRIC for production health",
    },
    "pfc_last_signal": {
        "verdict":           "PROCEED | SLOW | ESCALATE",
        "novelty_score":     "0.0–1.0",
        "uncertainty_score": "0.0–1.0",
        "consequence_risk":  "0.0–1.0",
        "rationale":         "human-readable string",
        "stakes":            "standard | high",
    },

    # From MetacognitiveMonitor
    "pillar_trust": {
        "CME":    "float ∈ [0.1, 1.5] — constraint memory trust",
        "TFE":    "float ∈ [0.1, 1.5] — temporal physics trust",
        "BioRAG": "float ∈ [0.1, 1.5] — episodic memory trust",
    },
    "env_stability":       "0.0–1.0 — how stable is the environment",
    "bandit_explore_rate": "0.0–1.0 — how often Bandit is exploring",
    "recent_adjustments":  "int — trust adjustments in last window",

    # NoesisCards hooks
    "escalation_log": "List[dict] — every ESCALATE event with full context",
    "adjustment_log": "List[dict] — every trust adjustment with reasoning",
}


# ══════════════════════════════════════════════════════════════
# THE COMPLETE FLOW — Pillar 6 integrated
# ══════════════════════════════════════════════════════════════

COMPLETE_FLOW = """
choose(condition, actions):

  [Pillars 1,3,5] → raw signals
        ↓
  [MetacogAwareSignalBus.fuse()]
    → applies metacog.trust multipliers to each pillar's confidence
    → CME trust=0.7? CME's confidence is dampened 30% in the fusion
    → BioRAG trust=1.3? BioRAG gets amplified 30% in the fusion
        ↓
  [PEE] → lock predictions
        ↓
  [PFCEngine.evaluate()]
    → reads fused weights, posteriors, TFE novelty, CME blocks
    → computes novelty_score, uncertainty_score, consequence_risk
    → emits verdict: PROCEED / SLOW / ESCALATE
    → adjusts weights based on verdict
        ↓
  [Bandit.get_action()]
    → samples from PFC-adjusted weights
    → SLOW weights push toward conservative actions
    → ESCALATE weights collapse toward single safest known action
        ↓
  returns (action, pfc_signal)

update(condition, action, success, step):

  [existing pillars update]
        ↓
  [MetacognitiveMonitor.log_decision()]
    → attributes outcome to active pillars by confidence weight
    → every N steps: runs review cycle
      → computes rolling win/loss rate per pillar
      → if CME loss_rate > threshold → reduce CME trust
      → if BioRAG retrievals poor → reduce BioRAG trust
      → if Bandit exploring too much in stable env → flag
      → adjust trust scores: slow, bounded, decay-toward-neutral
    → if adjustments made → returns report for NoesisCards card

load_domain("medical"):
  → swaps PFCConfig (tighter thresholds)
  → swaps MetacogConfig (tighter review, faster adjustment)
  → same brain, different governance envelope
  → Bandit posteriors, CME rules, BioRAG hippocampus ALL preserved
"""
