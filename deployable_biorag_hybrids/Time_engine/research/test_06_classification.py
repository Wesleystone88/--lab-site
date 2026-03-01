"""
Phase 06: State Classification Grid
Tests G1-G6 from testing_needed.txt
"""
from .framework import ResearchSuite
from Time_engine import dynamics
from Time_engine.config import TFEConfig

def run_phase_06(suite: ResearchSuite):
    phase = "06_Classify"
    
    def test_g1_full_grid(rng, seed):
        # Sweep the grid directly against expectations
        cfg = TFEConfig(s_high=0.6, u_high=0.5)
        
        # Grid steps 0.05
        steps = [i * 0.05 for i in range(21)]
        
        for s in steps:
            for u in steps:
                # dynamics.classify_key_state(s, u, s_high, u_high)
                cls = dynamics.classify_key_state(s, u, cfg.s_high, cfg.u_high)
                
                # Logic
                # s < 0.6, u < 0.5 -> HEALTHY
                # s < 0.6, u >= 0.5 -> PENDING
                # s >= 0.6, u < 0.5 -> ABANDONED
                # s >= 0.6, u >= 0.5 -> ORPHANED
                
                # Use strict inequality for <, but floating point can be tricky.
                # dynamics.py uses >= for threshold.
                
                is_high_s = s >= (cfg.s_high - 1e-9)
                is_high_u = u >= (cfg.u_high - 1e-9)
                
                expected = ""
                if not is_high_s and not is_high_u:
                    expected = "healthy"
                elif not is_high_s and is_high_u:
                    expected = "pending"
                elif is_high_s and not is_high_u:
                    expected = "abandoned"
                else:
                    expected = "orphaned"
                    
                assert cls.value == expected, f"Failed at s={s:.2f}, u={u:.2f}: Got {cls}, Want {expected}"

    suite.run_seeded(test_g1_full_grid, "G1", phase)
