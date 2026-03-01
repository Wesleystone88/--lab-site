"""
Bandit Engine (Main)
Contextual Bandit with "Memory-Guided Exploration".
"""
import random
from typing import List, Dict, Tuple, Optional
from .config import BanditConfig
from .state import BanditState, BetaParams
from . import distribution, guidance

class BanditEngine:
    def __init__(self, seed: int = 7, config: Optional[BanditConfig] = None):
        if config is None:
            config = BanditConfig()
        self.config = config
        self.state = BanditState()
        self.rng = random.Random(seed)
        
    def get_action(
        self, 
        context_key: str, 
        actions: List[str],
        cme_blocks: Optional[Dict[str, bool]] = None,
        cme_weights: Optional[Dict[str, float]] = None,
        tfe_decays: Optional[Dict[str, float]] = None
    ) -> Tuple[str, str, Dict[str, float]]:
        """
        Sample an action using Thompson Sampling, guided by CME and TFE.
        
        Returns:
            - selected_action
            - decision_source (provenance string)
            - debug_scores (sampled values)
        """
        # Ensure context exists
        if context_key not in self.state.posteriors:
            self.state.posteriors[context_key] = {}
        
        ctx_posteriors = self.state.posteriors[context_key]
        
        samples = {}
        sources = {}
        
        for action in actions:
            # Initialize if new
            if action not in ctx_posteriors:
                ctx_posteriors[action] = BetaParams(
                    self.config.prior_alpha, 
                    self.config.prior_beta
                )
            
            # Get raw posterior
            params = ctx_posteriors[action]
            
            # Extract guidance
            is_blocked = cme_blocks.get(action, False) if cme_blocks else False
            weight = cme_weights.get(action, 1.0) if cme_weights else 1.0
            decay = tfe_decays.get(action, 1.0) if tfe_decays else 1.0
            
            # Apply Guidance
            eff_params, src = guidance.apply_guidance(
                params, is_blocked, weight, decay, self.config
            )
            
            # Sample
            val = distribution.sample(eff_params, self.rng)
            
            samples[action] = val
            sources[action] = src
            
        # Select best
        best_action = max(samples, key=samples.get)
        best_source = sources[best_action]
        
        # Store metadata for debug
        self.state.last_guidance_source = best_source
        
        return best_action, best_source, samples
        
    def update(self, context_key: str, action: str, success: bool):
        """Update posterior belief."""
        if context_key not in self.state.posteriors:
            return  # Should not happen if get_action called first
            
        if action not in self.state.posteriors[context_key]:
            return
            
        current = self.state.posteriors[context_key][action]
        updated = distribution.update(current, success)
        
        self.state.posteriors[context_key][action] = updated
        self.state.total_updates += 1
        self.state.total_steps += 1
