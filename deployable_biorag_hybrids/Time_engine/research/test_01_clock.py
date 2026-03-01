"""
Phase 01: Clock & dt Sanitization
Tests C1-C6 from testing_needed.txt
"""
from .framework import ResearchSuite
from Time_engine.clock import EngineClock, ClockConfig

def run_phase_01(suite: ResearchSuite):
    phase = "01_Clock"
    
    def test_c1_negative_dt(rng, seed):
        clk = EngineClock()
        clk.update(100.0)
        # Time goes backwards
        raw, eff, _ = clk.update(90.0)
        assert raw == 0.0, f"Negative dt should be clamped to 0.0, got {raw}"
        
    def test_c2_zero_dt(rng, seed):
        clk = EngineClock()
        clk.update(100.0)
        raw, eff, _ = clk.update(100.0)
        assert raw == 0.0, f"Zero dt should be 0.0, got {raw}"

    def test_c3_normal_dt(rng, seed):
        clk = EngineClock()
        t0 = 100.0
        clk.update(t0)
        dt = rng.uniform(0.1, 50.0)
        raw, eff, _ = clk.update(t0 + dt)
        assert abs(raw - dt) < 1e-9, f"Normal dt mismatch: {raw} vs {dt}"

    def test_c4_clamping(rng, seed):
        cfg = ClockConfig(dt_max=60.0)
        clk = EngineClock(config=cfg)
        clk.update(100.0)
        
        dt_huge = 3600.0
        raw, eff, overflow = clk.update(100.0 + dt_huge)
        
        assert abs(raw - dt_huge) < 1e-9, "dt_raw should be truthful"
        assert abs(eff - 60.0) < 1e-9, f"dt_eff should be clamped to 60.0, got {eff}"
        assert abs(overflow - (dt_huge - 60.0)) < 1e-9, "Overflow calculation wrong"

    def test_c5_overflow_accum(rng, seed):
        cfg = ClockConfig(dt_max=10.0)
        clk = EngineClock(config=cfg)
        clk.update(0.0)
        
        total_overflow = 0.0
        t = 0.0
        for _ in range(100):
            dt = rng.uniform(11.0, 20.0) # Always overflow
            t += dt
            _, _, ov = clk.update(t)
            total_overflow += ov
            
        assert total_overflow > 0, "Overflow should accumulate"

    def test_c6_no_clamping_under(rng, seed):
        cfg = ClockConfig(dt_max=60.0)
        clk = EngineClock(config=cfg)
        clk.update(100.0)
        
        dt = 59.9
        raw, eff, ov = clk.update(100.0 + dt)
        assert abs(raw - eff) < 1e-9, "dt_eff should equal dt_raw when under limit"
        assert ov == 0.0, "Overflow should be 0"

    suite.run_seeded(test_c1_negative_dt, "C1", phase)
    suite.run_seeded(test_c2_zero_dt, "C2", phase)
    suite.run_seeded(test_c3_normal_dt, "C3", phase)
    suite.run_seeded(test_c4_clamping, "C4", phase)
    suite.run_seeded(test_c5_overflow_accum, "C5", phase)
    suite.run_seeded(test_c6_no_clamping_under, "C6", phase)
