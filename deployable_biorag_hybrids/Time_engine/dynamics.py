"""
TFE Dynamics Module (§6.2 - §6.4 Blueprint v0.2)
Implements physical laws for Gaps, Decay, and Urgency.
"""

import math
from typing import Tuple
from .state import GapClass, KeyStateClass

def classify_gap(dt_raw: float, theta: Tuple[float, float, float, float]) -> GapClass:
    """
    §6.2 Episode gap classification.
    theta = (theta0, theta1, theta2, theta3)
    """
    t0, t1, t2, t3 = theta
    
    if dt_raw < t0:
        return GapClass.IMMEDIATE
    elif dt_raw < t1:
        return GapClass.SHORT
    elif dt_raw < t2:
        return GapClass.MEDIUM
    elif dt_raw < t3:
        return GapClass.LONG
    else:
        return GapClass.RESET

def evolve_staleness(s: float, dt: float, tau: float) -> float:
    """
    §6.3 Decay (Thermodynamics)
    S_new = 1 - (1 - S_old) * exp(-dt / tau)
    """
    if tau <= 0: return 1.0 # Immediate decay if tau invalid
    decay_factor = math.exp(-dt / tau)
    return 1.0 - (1.0 - s) * decay_factor

def evolve_urgency(u: float, dt: float, gain: float) -> float:
    """
    §6.4 Pressure (Control Theory)
    U_new = U_old + k * dt (Clamped [0,1])
    """
    return min(1.0, u + gain * dt)

def reinforce(value: float, magnitude: float, coeff: float) -> float:
    """
    Generic reinforcement update.
    v_new = v_old - r * m (Clamped [0,1])
    """
    return max(0.0, value - coeff * magnitude)

def classify_key_state(s: float, u: float, s_high: float = 0.6, u_high: float = 0.5) -> KeyStateClass:
    """
    §7 O13 Key State Classification
    """
    is_stale = s >= s_high
    is_urgent = u >= u_high
    
    if not is_stale and not is_urgent:
        return KeyStateClass.HEALTHY
    elif not is_stale and is_urgent:
        return KeyStateClass.PENDING
    elif is_stale and not is_urgent:
        return KeyStateClass.ABANDONED
    else:
        return KeyStateClass.ORPHANED

def update_tempo(current_ema: float, dt: float, alpha: float, limits: Tuple[float, float]) -> Tuple[float, any]:
    """
    §6.5 Tempo Tracking (Event Rate EMA)
    rate ~ 1/dt
    """
    # Instantaneous rate
    if dt <= 0: return current_ema, None # Ignore zero-time events
    
    inst_rate = 1.0 / dt
    new_ema = (1.0 - alpha) * current_ema + alpha * inst_rate
    
    # Classify bucket
    # limits = (slow_limit, fast_limit)
    # Using a string or enum return type requires import. 
    # Let's return the enum from the caller or move enum here? 
    # For now, just return the value so engine can classify.
    return new_ema, None
