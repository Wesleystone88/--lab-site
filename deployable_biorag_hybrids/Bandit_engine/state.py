"""
Bandit Engine State
Mutable state definitions for the bandit.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class BetaParams:
    alpha: float
    beta: float
    
@dataclass
class BanditState:
    # {context_key: {action: BetaParams}}
    posteriors: Dict[str, Dict[str, BetaParams]] = field(default_factory=dict)
    
    # Metadata
    total_steps: int = 0
    total_updates: int = 0
    
    # Last guidance applied (transient/debug)
    last_guidance_source: str = "none"
