"""
TFE Persistence Verification Tests (§11 Blueprint v0.2)
Implements TST9 (Persistence).
"""

import unittest
from ..config import TFEConfig
from ..engine import TimeFieldEngine
from ..state import KeyStatus

class TestTFEPersistence(unittest.TestCase):
    
    def setUp(self):
        self.cfg = TFEConfig()
        self.eng = TimeFieldEngine(self.cfg)
        self.eng.state.t_last = 1000.0

    def test_tst9_persistence(self):
        """TST9: Save -> Load -> Verify State & Task Drop."""
        # 1. Setup State
        self.eng.open_key("save_me")
        self.eng.touch_key("save_me")
        self.eng.start_task("proc_X")
        
        # Advance time slightly
        self.eng.update(dt_override=1.0)
        
        # Verify Pre-Save
        self.assertIn("proc_X", self.eng.state.running_tasks)
        self.assertEqual(self.eng.state.keys["save_me"].status, KeyStatus.OPEN)
        
        # 2. Save
        snapshot = self.eng.save_snapshot()
        
        # 3. Create Fresh Engine & Load
        eng2 = TimeFieldEngine(self.cfg)
        eng2.load_snapshot(snapshot)
        
        # 4. Verify Restoration
        # Keys should be preserved
        self.assertIn("save_me", eng2.state.keys)
        self.assertEqual(eng2.state.keys["save_me"].status, KeyStatus.OPEN)
        self.assertEqual(eng2.state.dt_overflow_total, self.eng.state.dt_overflow_total)
        
        # 5. Verify Restart Logic (Task Drop)
        # Running tasks should be CLEARED
        self.assertNotIn("proc_X", eng2.state.running_tasks)
        # Counted in drops
        self.assertEqual(eng2.state.tasks_dropped_on_restart, 1)
        # Restart count incremented
        self.assertEqual(eng2.state.restart_count, self.eng.state.restart_count + 1)
        
        # Check Anomaly Record
        self.assertIn("proc_X", eng2.state.duration_anomalies)
        self.assertEqual(eng2.state.duration_anomalies["proc_X"].interrupted_on_load, 1)

if __name__ == "__main__":
    unittest.main()
