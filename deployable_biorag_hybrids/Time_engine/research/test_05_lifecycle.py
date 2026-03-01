"""
Phase 05: Key Lifecycle Exhaustive
Tests L1-L11 from testing_needed.txt
"""
from .framework import ResearchSuite
from Time_engine.engine import TimeFieldEngine
from Time_engine.config import TFEConfig
from Time_engine.state import KeyStatus

def run_phase_05(suite: ResearchSuite):
    phase = "05_Lifecycle"
    
    def test_l1_new_key_open(rng, seed):
        eng = TimeFieldEngine()
        eng.open_key("k1")
        k = eng.state.keys["k1"]
        assert k.status == KeyStatus.OPEN
        assert k.staleness == 0.0
        assert k.urgency == 0.0

    def test_l2_manual_close(rng, seed):
        eng = TimeFieldEngine()
        eng.open_key("k1")
        eng.close_key("k1")
        assert eng.state.keys["k1"].status == KeyStatus.CLOSED
        
    def test_l3_auto_expiry(rng, seed):
        T_exp = 100.0
        cfg = TFEConfig(t_expire=T_exp)
        eng = TimeFieldEngine(config=cfg)
        eng.open_key("k1")
        
        # Run until expiry
        # Condition: idle_time > T_expire
        # idle_time = last_event_elapsed
        eng.update(dt_override=T_exp + 1.0)
        
        # Check engine processed expiry
        k = eng.state.keys["k1"]
        assert k.status == KeyStatus.EXPIRED, f"Should be EXPIRED, got {k.status}"
        assert eng.state.key_expired_count == 1

    def test_l4_expire_timing(rng, seed):
        T_exp = 50.0
        cfg = TFEConfig(t_expire=T_exp)
        eng = TimeFieldEngine(config=cfg)
        eng.open_key("k1")
        
        # Just before
        eng.update(dt_override=T_exp - 0.1)
        assert eng.state.keys["k1"].status == KeyStatus.OPEN
        
        # Push over
        eng.update(dt_override=0.2)
        assert eng.state.keys["k1"].status == KeyStatus.EXPIRED
        
    def test_l7_touch_closed(rng, seed):
        eng = TimeFieldEngine()
        eng.open_key("k1")
        eng.close_key("k1")
        
        # Touch
        eng.touch_key("k1")
        assert eng.state.keys["k1"].status == KeyStatus.CLOSED, "Touching closed key should not re-open or change it"

    def test_l10_multi_expiry(rng, seed):
        # 10 keys, varying creation/taps
        eng = TimeFieldEngine(config=TFEConfig(t_expire=100.0))
        for i in range(10):
            eng.open_key(f"k{i}")
            
        # Tap even keys to reset their idle timer
        eng.update(dt_override=50.0)
        for i in range(0, 10, 2): # 0, 2, 4...
            eng.touch_key(f"k{i}")
            
        # Run another 60s
        # Total time: 110s.
        # Odd keys: Idle 110s > 100 -> Expire
        # Even keys: Idle 60s < 100 -> Open
        eng.update(dt_override=60.0)
        
        for i in range(10):
            status = eng.state.keys[f"k{i}"].status
            if i % 2 == 0:
                assert status == KeyStatus.OPEN, f"Key k{i} (even) should be OPEN"
            else:
                assert status == KeyStatus.EXPIRED, f"Key k{i} (odd) should be EXPIRED"

    suite.run_seeded(test_l1_new_key_open, "L1", phase)
    suite.run_seeded(test_l2_manual_close, "L2", phase)
    suite.run_seeded(test_l3_auto_expiry, "L3", phase)
    suite.run_seeded(test_l4_expire_timing, "L4", phase)
    suite.run_seeded(test_l7_touch_closed, "L7", phase)
    suite.run_seeded(test_l10_multi_expiry, "L10", phase)
