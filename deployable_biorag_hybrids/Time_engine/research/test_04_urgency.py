"""
Phase 04: Urgency Accumulation Mechanics
Tests U1-U8 from testing_needed.txt
"""
from .framework import ResearchSuite
from Time_engine.engine import TimeFieldEngine
from Time_engine.config import TFEConfig
from Time_engine.state import KeyStatus

def run_phase_04(suite: ResearchSuite):
    phase = "04_Urgency"
    
    def test_u1_linear_accum(rng, seed):
        gain = 0.001
        cfg = TFEConfig(urgency_gain=gain)
        eng = TimeFieldEngine(config=cfg)
        key = "u1"
        eng.open_key(key)
        
        # Run 500 steps
        for i in range(500):
            eng.update(dt_override=1.0)
            t = i + 1
            expected = min(1.0, t * gain)
            actual = eng.state.keys[key].urgency
            assert abs(actual - expected) < 1e-6, f"Step {t}: {actual} != {expected}"

    def test_u2_saturation(rng, seed):
        gain = 0.1
        cfg = TFEConfig(urgency_gain=gain)
        eng = TimeFieldEngine(config=cfg)
        key = "u2"
        eng.open_key(key)
        
        # Run until saturated (10 steps -> 1.0) + extra
        for _ in range(20):
            eng.update(dt_override=1.0)
            
        assert eng.state.keys[key].urgency == 1.0, "Should saturate at 1.0"

    def test_u4_reinforcement(rng, seed):
        cfg = TFEConfig(r_u=1.0)
        eng = TimeFieldEngine(config=cfg)
        key = "u4"
        eng.open_key(key)
        eng.state.keys[key].urgency = 0.8
        
        eng.touch_key(key, magnitude=1.0)
        assert eng.state.keys[key].urgency == 0.0, "Should reset to 0.0"

    def test_u7_reopen_reset(rng, seed):
        eng = TimeFieldEngine()
        key = "u7"
        eng.open_key(key)
        eng.state.keys[key].urgency = 0.9
        
        eng.close_key(key)
        eng.open_key(key) # Reopen
        
        assert eng.state.keys[key].urgency == 0.0, "Reopen should reset urgency"

    def test_u8_closed_no_accum(rng, seed):
        cfg = TFEConfig(urgency_gain=0.1)
        eng = TimeFieldEngine(config=cfg)
        key = "u8"
        eng.open_key(key)
        eng.close_key(key)
        
        # Run 100 steps
        for _ in range(100):
            eng.update(dt_override=1.0)
            
        assert eng.state.keys[key].urgency == 0.0, "Closed keys should not accumulate"

    suite.run_seeded(test_u1_linear_accum, "U1", phase)
    suite.run_seeded(test_u2_saturation, "U2", phase)
    suite.run_seeded(test_u4_reinforcement, "U4", phase)
    suite.run_seeded(test_u7_reopen_reset, "U7", phase)
    suite.run_seeded(test_u8_closed_no_accum, "U8", phase)
