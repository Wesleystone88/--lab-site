"""
TFE Clock Module (§6.1 Blueprint v0.2)
Handles monotonic time measurement and sanitization.
"""

import time
from dataclasses import dataclass
from typing import Tuple

@dataclass
class ClockConfig:
    dt_max: float = 60.0

class EngineClock:
    def __init__(self, config: ClockConfig = None):
        self.config = config if config else ClockConfig()
        self.last_time = 0.0
        
    def update(self, now: float) -> Tuple[float, float, float]:
        """
        Update clock with new time.
        Returns (dt_raw, dt_eff, overflow)
        """
        if self.last_time == 0.0:
            self.last_time = now
            return 0.0, 0.0, 0.0
            
        dt_raw = now - self.last_time
        
        # 1. Sanitize negative dt
        if dt_raw < 0:
            dt_raw = 0.0
            
        # 2. Clamp (dt_eff)
        dt_eff, overflow = self.clamp_dt(dt_raw, self.config.dt_max)
        
        self.last_time = now
        return dt_raw, dt_eff, overflow

    @staticmethod
    def clamp_dt(dt_raw: float, dt_max: float) -> Tuple[float, float]:
        """
        Clamp dt for stability (dt_eff).
        Returns (dt_eff, overflow).
        """
        dt_eff = min(dt_raw, dt_max)
        overflow = dt_raw - dt_eff if dt_raw > dt_eff else 0.0
        return dt_eff, overflow
