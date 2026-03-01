"""
Tri-Hybrid v0.3 Integration Test
Verifies the agent can run a full loop without crashing.
"""
import unittest
import sys
import os

# Ensure path
sandbox_root = os.path.dirname(os.path.abspath(__file__))
if sandbox_root not in sys.path:
    sys.path.insert(0, sandbox_root)

from tri_hybrid_v3 import TriHybridAgentV3

class TestTriHybridIntegration(unittest.TestCase):
    def test_full_loop(self):
        """Run a few steps to verify component wiring."""
        print("\nInitializing Tri-Hybrid Agent v0.3...")
        agent = TriHybridAgentV3(seed=42)
        
        condition = {"scene": "test_room"}
        actions = ["forward", "turn_left", "wait"]
        
        print("Running Step 1...")
        agent.step_decay(1)
        action, source = agent.choose_action(condition, actions)
        print(f"  Selected: {action} (Source: {source})")
        
        # Verify TFE Observables exist
        self.assertIsNotNone(agent.last_tfe_observables)
        self.assertEqual(agent.last_tfe_observables.episode_id, 0)
        
        # Verify Bandit State initialized
        ctx = agent._context_key(condition)
        self.assertIn(ctx, agent.bandit.state.posteriors)
        
        print("Updating Outcome (Success)...")
        agent.update(condition, action, success=True, step=1)
        
        # Verify Bandit Learned
        beta_params = agent.bandit.state.posteriors[ctx][action]
        # Alpha should be 1.0 (prior) + 1.0 (success) = 2.0
        self.assertEqual(beta_params.alpha, 2.0)
        
        print("Loop Complete. Integration Successful.")

if __name__ == "__main__":
    unittest.main()
