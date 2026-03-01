"""
Bandit Engine Verification
Tests core distribution logic and guidance injection.
"""
import unittest
import random
from Bandit_engine.config import BanditConfig
from Bandit_engine.state import BetaParams
from Bandit_engine import distribution, guidance
from Bandit_engine.engine import BanditEngine

class TestBanditCore(unittest.TestCase):
    def setUp(self):
        self.rng = random.Random(42)

    def test_beta_update(self):
        """Test simple bayesian update."""
        p = BetaParams(1.0, 1.0)
        p = distribution.update(p, success=True)
        self.assertEqual(p.alpha, 2.0)
        self.assertEqual(p.beta, 1.0)
        
        p = distribution.update(p, success=False)
        self.assertEqual(p.alpha, 2.0)
        self.assertEqual(p.beta, 2.0)

    def test_decay(self):
        """Test decay towards prior."""
        p = BetaParams(10.0, 10.0)
        # Decay by 0.5 -> should be halfway to 1.0
        # New = 1 + (10-1)*0.5 = 1 + 4.5 = 5.5
        p_new = distribution.apply_decay(p, 0.5)
        self.assertAlmostEqual(p_new.alpha, 5.5)
        self.assertAlmostEqual(p_new.beta, 5.5)
        
    def test_guidance_injection(self):
        """Test that guidance modifies params correctly."""
        cfg = BanditConfig()
        base = BetaParams(5.0, 5.0)
        
        # 1. Hard Block
        p_blocked, src = guidance.apply_guidance(base, True, 1.0, 1.0, cfg)
        self.assertIn("cme_block", src)
        self.assertEqual(p_blocked.beta, 5.0 + cfg.hard_block_penalty)
        
        # 2. Soft Penalty (Weight < 0.8)
        weight = 0.5
        p_soft, src = guidance.apply_guidance(base, False, weight, 1.0, cfg)
        expected_penalty = (1.0 - weight) * cfg.soft_weight_scale # 0.5 * 1.5 = 0.75
        self.assertIn("cme_weight_neg", src)
        self.assertEqual(p_soft.beta, 5.0 + expected_penalty)
        
        # 3. TFE Decay
        decay = 0.1
        p_decay, src = guidance.apply_guidance(base, False, 1.0, decay, cfg)
        # 1 + (4 * 0.1) = 1.4
        self.assertIn("tfe_decay", src)
        self.assertAlmostEqual(p_decay.alpha, 1.4)

class TestBanditEngine(unittest.TestCase):
    def test_end_to_end_decision(self):
        eng = BanditEngine()
        actions = ["A", "B"]
        context = "ctx1"
        
        # Initial: uniform random-ish
        # We can't deterministic check random sample easily without seed control
        # checking structure instead
        act, src, debug = eng.get_action(context, actions)
        self.assertIn(act, actions)
        self.assertEqual(src, "unbiased")
        
        # Inject Block on A
        act, src, debug = eng.get_action(
            context, actions, 
            cme_blocks={"A": True}
        )
        # With A blocked, B should be chosen (statistically)
        # A beta -> 1 + 3 = 4, alpha=1 -> Mean 0.2
        # B beta -> 1, alpha=1 -> Mean 0.5
        # Over many samples B wins.
        
        # Update A success
        eng.update(context, "A", True)
        self.assertEqual(eng.state.posteriors[context]["A"].alpha, 2.0)

if __name__ == '__main__':
    unittest.main()
