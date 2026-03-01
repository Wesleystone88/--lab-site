"""
Bandit Distribution Math
Beta distribution logic: sampling, updating, and decay.
"""
import random
from .state import BetaParams

def sample(params: BetaParams, rng: random.Random) -> float:
    """Sample from Beta(alpha, beta)."""
    # math.domain_error protection
    a = max(0.1, params.alpha)
    b = max(0.1, params.beta)
    return rng.betavariate(a, b)

def update(params: BetaParams, success: bool) -> BetaParams:
    """Return NEW params after observation."""
    if success:
        return BetaParams(params.alpha + 1.0, params.beta)
    else:
        return BetaParams(params.alpha, params.beta + 1.0)

def apply_decay(params: BetaParams, decay_factor: float) -> BetaParams:
    """
    Decay towards Prior(1,1).
    new = 1 + (old - 1) * decay
    decay_factor < 1.0 means "forgetting".
    """
    if decay_factor >= 1.0:
        return params
        
    new_a = 1.0 + (params.alpha - 1.0) * decay_factor
    new_b = 1.0 + (params.beta - 1.0) * decay_factor
    
    return BetaParams(max(1.0, new_a), max(1.0, new_b))
