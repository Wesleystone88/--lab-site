"""
Phase 08: Persistence Under Stress
Tests P1-P10 from testing_needed.txt
"""
from .framework import ResearchSuite
from Time_engine.engine import TimeFieldEngine
from Time_engine import persistence
from Time_engine.state import KeyStatus as KS
import tempfile
import os
import shutil

def run_phase_08(suite: ResearchSuite):
    phase = "08_Persistence"
    
    def test_p1_save_load_fidelity(rng, seed):
        # Create unique temp dir for this test/seed
        tmp_dir = tempfile.mkdtemp()
        try:
            snap_path = os.path.join(tmp_dir, "snap.json")
            
            # Setup complex state
            eng = TimeFieldEngine()
            eng.open_key("k1")
            eng.state.keys["k1"].staleness = 0.5
            eng.state.keys["k1"].urgency = 0.8
            eng.update(dt_override=10.0)
            
            # Save
            # We must use the updated API that accepts path
            eng.save_snapshot(path=snap_path)
            
            # Load new instance
            eng2 = TimeFieldEngine()
            eng2.load_snapshot(snap_path)
            
            # Compare
            k1 = eng2.state.keys.get("k1")
            if k1 is None:
                print("DEBUG: k1 missing in eng2.state.keys:", eng2.state.keys.keys())
            assert k1 is not None, "Key k1 missing after load"
            
            # Check values
            # Compare against the evolving state of the original engine (which was saved)
            # Not hardcoded 0.5/0.8, because update(10.0) changed them.
            
            target_staleness = eng.state.keys["k1"].staleness
            target_urgency = eng.state.keys["k1"].urgency
            
            if abs(k1.staleness - target_staleness) > 1e-6:
                print(f"DEBUG: Staleness mismatch. Got {k1.staleness}, Want {target_staleness}")
            assert abs(k1.staleness - target_staleness) < 1e-6
            
            if abs(k1.urgency - target_urgency) > 1e-6:
                print(f"DEBUG: Urgency mismatch. Got {k1.urgency}, Want {target_urgency}")
            assert abs(k1.urgency - target_urgency) < 1e-6
            
            if eng2.state.episode_id != eng.state.episode_id + 1:
                print(f"DEBUG: Episode ID mismatch. Got {eng2.state.episode_id}, Want {eng.state.episode_id + 1}")
            assert eng2.state.episode_id == eng.state.episode_id + 1, "Restart boundary should inc episode"
            
        finally:
            shutil.rmtree(tmp_dir)

    def test_p2_task_drop(rng, seed):
        tmp_dir = tempfile.mkdtemp()
        try:
            snap_path = os.path.join(tmp_dir, "snap.json")
            
            eng = TimeFieldEngine()
            eng.start_task("k1")
            if eng.state.active_task != "k1":
                print(f"DEBUG P2: start_task failed. active_task is {eng.state.active_task}")
            assert eng.state.active_task == "k1"
            
            eng.save_snapshot(path=snap_path)
            
            eng2 = TimeFieldEngine()
            eng2.load_snapshot(snap_path)
            
            if eng2.state.active_task is not None:
                print(f"DEBUG P2: active_task not dropped! It is {eng2.state.active_task}")
            assert eng2.state.active_task is None, "Active task should be dropped on restart"
            
            if eng2.state.tasks_dropped_on_restart != 1:
                print(f"DEBUG P2: tasks_dropped_on_restart is {eng2.state.tasks_dropped_on_restart}, expected 1")
            assert eng2.state.tasks_dropped_on_restart == 1
            
        finally:
            shutil.rmtree(tmp_dir)

    def test_p9_config_conflict(rng, seed):
        # Save with config A, load with config B
        tmp_dir = tempfile.mkdtemp()
        try:
            snap_path = os.path.join(tmp_dir, "snap.json")
            
            eng = TimeFieldEngine()
            # Default config
            eng.save_snapshot(snap_path)
            
            # Load with differnet config
            from Time_engine.config import TFEConfig
            cfg_b = TFEConfig(tau_staleness=999.0)
            eng2 = TimeFieldEngine(config=cfg_b)
            eng2.load_snapshot(snap_path)
            
            assert eng2.state.config_conflict_count == 1, "Should detect config conflict"
            
        finally:
            shutil.rmtree(tmp_dir)

    suite.run_seeded(test_p1_save_load_fidelity, "P1", phase)
    suite.run_seeded(test_p2_task_drop, "P2", phase)
    suite.run_seeded(test_p9_config_conflict, "P9", phase)
