"""
Tri-Hybrid Agent v0.3 (Integration)
===================================
The unified agent that orchestrates the three systems:
1. Brain (CME): Cognitive Model limits scope and bias.
2. Nervous System (TFE): Time Field Engine perceives temporal context.
3. Hands (Bandit): Thompson Sampling executes actions with guided priors.

This version uses the fully decoupled modules:
- Time_engine (v0.2 Verified)
- Bandit_engine (v0.1 Verified)
- CME (Core Implementation)
"""

import sys
import os
from typing import Dict, List, Tuple, Optional

# Add paths for Sandbox interaction
SYSPATH_UPDATED = False
def ensure_syspath():
    global SYSPATH_UPDATED
    if SYSPATH_UPDATED: return
    
    # Add Sandbox Root (for local packages)
    sandbox_root = os.path.dirname(os.path.abspath(__file__))
    if sandbox_root not in sys.path:
        sys.path.insert(0, sandbox_root)
        
    # Add Core Implementation (for CME)
    core_path = os.path.join(sandbox_root, "..", "01_Core_Implementation")
    if os.path.exists(core_path) and core_path not in sys.path:
        sys.path.insert(0, core_path)
    
    SYSPATH_UPDATED = True

ensure_syspath()

# Imports
try:
    from halcyon_research_demo import CME, BiasSurface
    from Time_engine.engine import TimeFieldEngine
    from Time_engine.config import TFEConfig
    from Time_engine.state import KeyStatus
    from Bandit_engine.engine import BanditEngine
    from Bandit_engine.config import BanditConfig
except ImportError as e:
    print(f"CRITICAL IMPORT ERROR: {e}")
    print("Please ensure you are running from the 'sandbox_hybrid' directory.")
    sys.exit(1)


class TriHybridAgentV3:
    def __init__(
        self, 
        seed: int = 42,
        cme_explore_rate: float = 0.02,
        tfe_tau: float = 150.0,
        bandit_prior_scale: float = 1.0
    ):
        self.seed = seed
        
        # 1. BRAIN (CME)
        self.cme = CME(seed=seed, explore_rate=cme_explore_rate)
        
        # 2. NERVOUS SYSTEM (TFE)
        tfe_cfg = TFEConfig(tau_staleness=tfe_tau)
        self.tfe = TimeFieldEngine(config=tfe_cfg)
        
        # 3. HANDS (Bandit)
        bandit_cfg = BanditConfig(soft_weight_scale=1.5, hard_block_penalty=3.0)
        self.bandit = BanditEngine(seed=seed, config=bandit_cfg)
        
        # Metrics / State tracking
        self.last_decision_source = "none"
        self.last_tfe_observables = None

    def _context_key(self, condition: Dict[str, str]) -> str:
        """Create hashable context key from condition dict."""
        return "|".join(f"{k}={v}" for k, v in sorted(condition.items()))

    def step_decay(self, step: int):
        """
        Advance global clock and decay systems.
        Called once per environment step.
        """
        # A. CME logic decay
        self.cme.step_decay(step)
        
        # B. TFE Time update (Assume 1 step = 1 second for simulation)
        # In real app, this would be real-time.
        obs = self.tfe.update(dt_override=1.0)
        self.last_tfe_observables = obs

    def choose_action(self, condition: Dict[str, str], actions: List[str]) -> Tuple[str, str]:
        """
        Select action using the Tri-Hybrid Architecture.
        """
        ctx_key = self._context_key(condition)
        
        # --- 1. NERVOUS SYSTEM (Prepare Keys) ---
        # Ensure TFE tracks these action-contexts
        for act in actions:
            tfe_key = f"{ctx_key}|{act}"
            self.tfe.open_key(tfe_key)
            
        # --- 2. BRAIN (Get Bias) ---
        # CME analyzes the 'condition' (logical context)
        bias: BiasSurface = self.cme.emit_bias(condition, actions)
        
        # --- 3. NERVOUS SYSTEM (Get Decay/Doubt) ---
        # TFE analyzes temporal health of each action
        tfe_decays = {}
        for act in actions:
            tfe_key = f"{ctx_key}|{act}"
            # Access internal state directly for efficiency, or via observables map
            # We'll peek at state directly as TFE is local.
            kstate = self.tfe.state.keys.get(tfe_key)
            if kstate and kstate.status == KeyStatus.OPEN:
                # If stale (high staleness), guided decay factor < 1.0 (reduce confidence)
                # Staleness varies 0..1. 
                # Let's map Staleness 1.0 -> Decay 0.5 (Strong doubt)
                # Staleness 0.0 -> Decay 1.0 (Full confidence)
                decay_factor = 1.0 - (kstate.staleness * 0.5) 
                
                # If 'orphaned' (stale + low urgency), maybe decay more?
                # For v0.3 we stick to simple linear staleness mapping.
                tfe_decays[act] = decay_factor
            else:
                tfe_decays[act] = 1.0

        # --- 4. HANDS (Execute) ---
        # Bandit combines Priors (from CME) + Decay (from TFE) + History (Beta)
        action, source, debug_scores = self.bandit.get_action(
            context_key=ctx_key,
            actions=actions,
            cme_blocks=bias.hard_blocks,
            cme_weights=bias.weights,
            tfe_decays=tfe_decays
        )
        
        # Logic to determine high-level attribution for logging
        # If CME blocked or strongly weighted, we credit 'hybrid'
        # If TFE decayed significantly, we credit 'hybrid'
        # For now, return what the bandit engine says ("cme_block", "tfe_decay", etc.)
        self.last_decision_source = source
        return action, source

    def update(self, condition: Dict[str, str], action: str, success: bool, step: int):
        """
        Learn from outcome.
        """
        ctx_key = self._context_key(condition)
        
        # 1. Update HANDS (Bandit Posteriors)
        self.bandit.update(ctx_key, action, success)
        
        # 2. Update BRAIN (CME Memory)
        # Logic copied from cme_thompson_hybrid
        if not success:
            self.cme.reinforce_memory(
                mem_type="CONSTRAINT",
                condition_subset=condition,
                action=action,
                step=step
            )
        self.cme.counter_evidence(
            condition=condition, 
            action=action, 
            success=success, 
            step=step
        )
        
        # 3. Update NERVOUS SYSTEM (TFE)
        tfe_key = f"{ctx_key}|{action}"
        # Touch key: magnitude depends on success?
        # Blueprint says: reinforcement. 
        # Success = Strong reinforcement (reset staleness)
        # Failure = Weak reinforcement? Or none?
        # Typically any interaction resets staleness (it's "freshly tried").
        # We'll reinforce fully to say "this path is active".
        self.tfe.touch_key(tfe_key, magnitude=1.0)
