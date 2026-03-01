"""
Phase 03: Staleness Decay Mechanics
Tests S1-S10 from testing_needed.txt
"""
from .framework import ResearchSuite
from Time_engine.engine import TimeFieldEngine
from Time_engine.config import TFEConfig
from Time_engine import dynamics
import math

def run_phase_03(suite: ResearchSuite):
    phase = "03_Staleness"
    
    def test_s1_formula_tau150(rng, seed):
        tau = 150.0
        cfg = TFEConfig(tau_staleness=tau)
        eng = TimeFieldEngine(config=cfg)
        key = "s1"
        eng.open_key(key)
        # Set manual start
        eng.state.keys[key].staleness = 0.0
        
        # Evolve 300 steps
        for i in range(300):
            eng.update(dt_override=1.0)
            
            # Check formula
            # s(t) = 1 + (s(0)-1)*exp(-t/tau)
            # here s(0)=0.0, so s(t) = 1 - exp(-t/tau)
            t = i + 1
            expected = 1.0 - math.exp(-t / tau)
            actual = eng.state.keys[key].staleness
            
            assert abs(actual - expected) < 1e-3, f"Step {i}: Got {actual}, want {expected}"

    def test_s4_bounded(rng, seed):
        eng = TimeFieldEngine()
        key = "s4"
        eng.open_key(key)
        
        for _ in range(1000):
            dt = rng.uniform(0.1, 10.0)
            eng.update(dt_override=dt)
            s = eng.state.keys[key].staleness
            assert 0.0 <= s <= 1.0, f"Staleness out of bounds: {s}"

    def test_s5_reinforcement(rng, seed):
        cfg = TFEConfig(r_s=1.0) # Full reset power
        eng = TimeFieldEngine(config=cfg)
        key = "s5"
        eng.open_key(key)
        eng.state.keys[key].staleness = 0.8
        
        # Touch with magnitude 1.0
        eng.touch_key(key, magnitude=1.0)
        
        # Formula: s_new = max(0, s_old - r_s * magnitude)
        # 0.8 - 1.0*1.0 = -0.2 -> 0.0
        assert eng.state.keys[key].staleness == 0.0, "Should reset to 0"

    def test_s6_partial_reinforcement(rng, seed):
        cfg = TFEConfig(r_s=1.0)
        eng = TimeFieldEngine(config=cfg)
        key = "s6"
        eng.open_key(key)
        eng.state.keys[key].staleness = 0.8
        
        # Partial
        eng.touch_key(key, magnitude=0.5)
        # 0.8 - 0.5 = 0.3
        assert abs(eng.state.keys[key].staleness - 0.3) < 1e-6
        
    suite.run_seeded(test_s1_formula_tau150, "S1", phase)
    suite.run_seeded(test_s4_bounded, "S4", phase)
    suite.run_seeded(test_s5_reinforcement, "S5", phase)
    suite.run_seeded(test_s6_partial_reinforcement, "S6", phase)
