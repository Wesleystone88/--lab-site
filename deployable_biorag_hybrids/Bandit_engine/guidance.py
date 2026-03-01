"""
Bandit Engine Guidance
Logic for translating external signals (CME bias, TFE state) into
modifications of the Beta distribution priors.
"""
from typing import Dict, Optional, Tuple
from .config import BanditConfig
from .state import BetaParams

def apply_guidance(
    params: BetaParams, 
    cme_hard_block: bool,
    cme_weight: float,
    tfe_decay: float,
    config: BanditConfig
) -> Tuple[BetaParams, str]:
    """
    Apply external guidance to shape the effective distribution.
    Returns (EffectiveParams, SourceDescription)
    """
    alpha = params.alpha
    beta = params.beta
    source_flags = []
    
    # 1. TFE Decay (Doubt)
    # If state is stale/orphaned, we decay belief towards prior (1,1)
    if tfe_decay < 1.0:
        # distribution.apply_decay logic inlined for clarity/access
        new_a = 1.0 + (alpha - 1.0) * tfe_decay
        new_b = 1.0 + (beta - 1.0) * tfe_decay
        alpha, beta = max(1.0, new_a), max(1.0, new_b)
        source_flags.append("tfe_decay")
        
    # 2. CME Hard Block (Constraint)
    # "Don't do this" -> Massive boost to Beta (failure count)
    if cme_hard_block:
        beta += config.hard_block_penalty
        source_flags.append("cme_block")
        
    # 3. CME Soft Weight (Preference)
    # < 1.0: Pessimism (add to beta)
    # > 1.0: Optimism (add to alpha) - rare in current logic but supported
    if cme_weight < 0.8:
        # Penalty proportional to strength
        penalty = (1.0 - cme_weight) * config.soft_weight_scale
        beta += penalty
        source_flags.append("cme_weight_neg")
    elif cme_weight > 1.2:
        bonus = (cme_weight - 1.0) * config.soft_weight_scale
        alpha += bonus
        source_flags.append("cme_weight_pos")
        
    return BetaParams(alpha, beta), "+".join(source_flags) if source_flags else "unbiased"
