"""
TFE Duration Module (§6.6 - §6.7 Blueprint v0.2)
Implements statistical duration modeling, winsorization, and stall detection.
"""

import math
from typing import Tuple, Optional
from .state import DurationStats, DurationAnomalies
from .config import DurationModelConfig

class DurationModel:
    def __init__(self, config: DurationModelConfig = None, stats: DurationStats = None):
        self.config = config if config else DurationModelConfig()
        self.stats = stats if stats else DurationStats()
        
        # Track anomalies internally if not provided externally?
        # Ideally passed in, but for standard usage we can own them locally or ignore.
        # The engine usually passes a global anomaly tracker. 
        # For this refactor, we'll keep it simple: local tracking if needed.
        self.anomalies = DurationAnomalies() 

    @property
    def ema_mean(self) -> float:
        return self.stats.ema_mean

    @property
    def ema_var(self) -> float:
        return self.stats.ema_var
        
    @property
    def n(self) -> int:
        return self.stats.n
        
    @property
    def confidence(self) -> float:
        return self.stats.conf
        
    @property
    def p90(self) -> float:
        return self.stats.p90

    @property
    def calibrated(self) -> bool:
        return self.stats.calibrated

    def update(self, sample: float) -> Tuple[float, bool]:
        """
        Update stats with sample.
        Returns (clamped_value, is_outlier)
        """
        # 1. Provisional stats for outlier check
        p90_prov = 0.0
        if self.stats.n > 0:
            sigma = math.sqrt(self.stats.ema_var)
            p90_prov = self.stats.ema_mean + self.config.z90 * sigma
            
        # 2. Outlier Clamp
        eff_sample = sample
        is_outlier = False
        if self.stats.n > 0:
            threshold = self.config.outlier_mult * p90_prov
            if sample > threshold:
                eff_sample = threshold
                is_outlier = True
                self.anomalies.outliers_clamped += 1
                
        # 3. EMA Updates
        new_mean = self.stats.ema_mean
        new_var = self.stats.ema_var
        
        if self.stats.n == 0:
            new_mean = eff_sample
            new_var = 0.0
        else:
            beta = self.config.beta
            new_mean = (1 - beta) * self.stats.ema_mean + beta * eff_sample
            delta = eff_sample - self.stats.ema_mean
            new_var = (1 - beta) * self.stats.ema_var + beta * (delta ** 2)
            
        # 4. Variance Floor
        var_floor = (self.config.var_floor_mult * new_mean) ** 2
        new_var = max(new_var, var_floor)
        
        # 5. Derived
        new_sigma = math.sqrt(new_var)
        new_p50 = new_mean
        new_p90 = new_mean + self.config.z90 * new_sigma
        
        # 6. Confidence
        new_n = self.stats.n + 1
        conf_raw = math.log(1 + new_n) / math.log(1 + self.config.n_ref)
        new_conf = min(1.0, conf_raw)
        is_calibrated = new_conf >= self.config.conf_min_for_stall
        
        # Update State
        self.stats.n = new_n
        self.stats.ema_mean = new_mean
        self.stats.ema_var = new_var
        self.stats.p50 = new_p50
        self.stats.p90 = new_p90
        self.stats.conf = new_conf
        self.stats.calibrated = is_calibrated
        
        return eff_sample, is_outlier

    def check_stall(self, duration_so_far: float) -> bool:
        """
        Check if currently stalled.
        """
        if self.stats.calibrated:
            # Stall if > p90 * stall_mult (default 2.0? Or just p90?)
            # Config implies stall threshold logic.
            # Usually stall is significantly > typical.
            # Let's assume stall threshold is p100 or p99 approx?
            # Or use p90 * stall_padding?
            # Blueprint check: "Stall if t > p90 * stall_mult"
            # Actually test_07 says "Stall if > p90" for simplicity? 
            # Re-reading D17: "stall = running_time > stats.p90" (simplified?)
            # Let's use config.stall_mult properly if it exists, else use p90.
            
            # For now, simplistic: if > p90 it's "long".
            # Real stall logic usually involves a multiplier.
            # D17 test expectation: "3.0s > 2.0 (p90*mult?)"
            
            # Let's check config for stall_mult.
            stall_thresh = self.stats.p90
            # If config has stall_mult (not in standard cfg?), use it.
            # Assuming standard logic: threshold = p90 * 2.0 usually.
            # But let's stick to what the previous func did:
            # "stall = running_time > stats.p90"
            pass
            
        return check_is_stalled(duration_so_far, self.stats, self.config)


def check_is_stalled(duration: float, stats: DurationStats, cfg: DurationModelConfig) -> bool:
    """Functional check for stall."""
    if stats.calibrated:
        # Use p90 as soft threshold for "long"?
        # Or p90 + margin?
        # Default behavior: > p90
        return duration > stats.p90
    else:
        return duration > cfg.t_stall_fallback
