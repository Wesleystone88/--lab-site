"""
TFE Configuration (§10 Blueprint v0.2)
Immutable configuration parameters for the Time Field Engine.
"""

from dataclasses import dataclass, field
from typing import Dict

@dataclass(frozen=True)
class DurationModelConfig:
    beta: float = 0.1             # C6: EMA smoothing factor
    outlier_mult: float = 3.0     # C6: Winsorization threshold (mult of p90)
    n_ref: float = 10.0           # C6: Reference count for confidence scaling
    z90: float = 1.28             # C6: Sigma multiplier for p90 approx (Normal assumption)
    var_floor_mult: float = 0.1   # C6b: Minimum variance as fraction of mean
    conf_min_for_stall: float = 0.5 # C6c: Minimum confidence to trigger stall detection
    t_stall_fallback: float = 300.0 # C6d: Fallback stall timeout if uncalibrated (seconds)

@dataclass(frozen=True)
class TFEConfig:
    # C0: Gap thresholds (seconds) [immediate, short, medium, long]
    # "reset" if >= theta_long
    theta: tuple = (1.0, 60.0, 300.0, 3600.0) 
    
    # Optional explicit overrides for tests (mapped in __post_init__ or property)
    theta_short: float = 5.0
    theta_long: float = 3600.0
    
    # Classification Thresholds
    s_high: float = 0.6
    u_high: float = 0.5 
    
    # C1: Global Staleness Tau (seconds)
    tau_staleness: float = 3600.0 
    
    # C2: Global Urgency Gain (per second)
    urgency_gain: float = 0.001 
    
    # C3: Reinforcement Coefficients
    r_s: float = 1.0 # Staleness reduction per max progress
    r_u: float = 1.0 # Urgency reduction per max progress
    
    # C4: Heartbeat Interval (seconds) - mainly for run_forever loops
    tick_interval: float = 1.0
    
    # C5: dt_eff clamp (seconds) - max dt for dynamics updates
    dt_max: float = 60.0
    
    # C6: Duration Model
    duration: DurationModelConfig = field(default_factory=DurationModelConfig)
    
    # C8: Tempo Config
    alpha_tempo: float = 0.1 # Smoothing factor for event rate
    tempo_limits: tuple = (0.1, 10.0) # (slow_limit, fast_limit) Hz
    
    # C7: Bucket Thresholds (optional, implemented in dynamics/observables if needed)
    
    # C9: Key Auto-Expiry (seconds)
    t_expire: float = 86400.0 # 24 hours default
    
    # Persistence
    save_path: str = "tfe_snapshot.json"
    
    def __post_init__(self):
        # Sync theta tuple with explicit fields
        # theta = (1.0, self.theta_short, 300.0, self.theta_long)
        # Using object.__setattr__ to bypass frozen check
        t = (1.0, self.theta_short, 300.0, self.theta_long)
        object.__setattr__(self, 'theta', t)
