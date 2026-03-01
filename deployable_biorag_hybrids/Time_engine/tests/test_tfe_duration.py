"""
TFE Duration Verification Tests (§11 Blueprint v0.2)
Implements TST12 and verification of Duration Model.
"""

import unittest
from ..config import TFEConfig, DurationModelConfig
from ..engine import TimeFieldEngine

class TestTFEDuration(unittest.TestCase):
    
    def setUp(self):
        # Config for fast calibration
        dur_cfg = DurationModelConfig(
            beta=0.5, # Fast learning
            n_ref=5.0, # Low confidence threshold
            conf_min_for_stall=0.5,
            t_stall_fallback=100.0
        )
        self.cfg = TFEConfig(duration=dur_cfg)
        self.eng = TimeFieldEngine(self.cfg)
        self.eng.state.t_last = 0.0

    def test_duration_learning_and_stall(self):
        """TST12: Learn duration -> Calibrate -> Detect Stall."""
        from unittest.mock import patch
        
        sig = "task_A"
        
        # We need to control time.monotonic()
        # Initial time 1000.0
        current_time = 1000.0
        
        with patch('time.monotonic', side_effect=lambda: current_time):
            # 1. Train (6 samples of 1.0s)
            for _ in range(6):
                # Start at t
                self.eng.start_task(sig)
                
                # Advance 1.0s
                current_time += 1.0
                # Update engine (dt=1.0)
                self.eng.update(dt_override=1.0) # Engine uses its own dt, but check_stall uses monotonic now
                
                # End at t+1.0
                self.eng.end_task(sig)
                
            stats = self.eng.state.duration_stats[sig]
            self.assertTrue(stats.calibrated)
            self.assertAlmostEqual(stats.p50, 1.0, delta=0.1)
            
            # 2. Test Stall
            # Start at t
            self.eng.start_task(sig)
            
            # Run for 0.5s (No stall)
            current_time += 0.5
            obs = self.eng.update(dt_override=0.5)
            self.assertFalse(obs.stall_detected)
            
            # Run for 1.5s more (Total 2.0s)
            # p90 is approx 1.1s
            current_time += 1.5
            obs = self.eng.update(dt_override=1.5)
            self.assertTrue(obs.stall_detected)
            self.assertIn(sig, obs.stall_signatures)

    def test_duration_logic_direct(self):
        """Verify duration.py logic directly since engine methods might be missing."""
        from .. import duration
        from ..state import DurationStats, DurationAnomalies
        
        stats = DurationStats()
        anoms = DurationAnomalies()
        cfg = self.cfg.duration
        
        # Feed 10 samples of 1.0s
        for _ in range(10):
            stats = duration.update_stats(stats, 1.0, cfg, anoms)
            
        self.assertAlmostEqual(stats.ema_mean, 1.0, places=2)
        self.assertAlmostEqual(stats.ema_var, 0.01, places=2) # Var floor 0.1*1.0 ^2
        self.assertTrue(stats.calibrated)
        
        # Check Stall
        # p90 = 1.0 + 1.28 * 0.1 = 1.128
        
        # Run for 0.5s (No stall)
        stall, fallback = duration.check_stall(0.0, 0.5, stats, cfg)
        self.assertFalse(stall)
        
        # Run for 2.0s (Stall)
        stall, fallback = duration.check_stall(0.0, 2.0, stats, cfg)
        self.assertTrue(stall)
        self.assertFalse(fallback) # Calibrated
