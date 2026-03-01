"""
Bandit Engine Configuration
Immutable parameters for the Thompson Sampling bandit.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class BanditConfig:
    # Prior Hyperparameters
    prior_alpha: float = 1.0
    prior_beta: float = 1.0
    
    # Safety
    min_variance: float = 0.001 # Prevent collapse
    max_steps_history: int = 10000 
    
    # Guidance Scaling
    # Measurements of how strongly guidance signals affect the priors
    hard_block_penalty: float = 3.0 # Added to beta for 'avoid'
    soft_weight_scale: float = 1.5  # Multiplier for soft weights
