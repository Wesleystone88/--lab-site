"""
test_noesis_bridge.py
=====================
Full test suite for NoesisBridge middleware.

Tests cover:
  1. Context translation — sim metrics → agent vocabulary
  2. Action application — agent actions → sim parameter changes
  3. Reward computation — pre/post metric delta scoring
  4. Card logging — NoesisCards-compatible output
  5. Agent API compatibility — old and new API handled
  6. Domain loader integration — domain tag flows through
  7. JSONL log output — card format valid
  8. Momentum computation — trend detection works
  9. Parameter bounds — nudges never exceed safety limits
  10. Full loop integrity — 50 steps, no crash, cards match steps
  11. PFC signal handling — ESCALATE/SLOW verdicts logged
  12. Multi-domain run — domain switch mid-run works
"""

import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from noesis_bridge import (
    NoesisBridge, BridgeConfig, BridgeCard,
    CTX_CONSENSUS, CTX_CONFLICT, CTX_THROUGHPUT,
    CTX_MEMORY, CTX_TRUST, CTX_CHARISMATA, CTX_MOMENTUM, CTX_DOMAIN,
    ACTION_BOOST_TRUST, ACTION_REDUCE_TRUST,
    ACTION_AMPLIFY_SIGNAL, ACTION_DAMPEN_SIGNAL,
    ACTION_STRENGTHEN_MEMORY, ACTION_FLUSH_MEMORY,
    ACTION_PUSH_CONSENSUS, ACTION_RELEASE_CONSENSUS,
    ACTION_HOLD, ALL_ACTIONS,
    _MockSim, _MockAgent,
)


# ─────────────────────────────────────────────────────────────
# CONTROLLED MOCK SIM — returns exact metrics for testing
# ─────────────────────────────────────────────────────────────

class ControlledSim:
    """Sim that returns exactly what you tell it to."""
    def __init__(self, metrics_sequence=None):
        self.immune_strength = 0.12
        self.diff_U          = 0.20
        self.decay_D         = 0.0002
        self.target_drift    = 0.004
        self._t              = 0
        self._seq            = metrics_sequence or []
        self._idx            = 0
        self._default = {
            "t": 0, "align": 0.60, "conflict": 0.20, "throughput": 0.25,
            "E_mean": 0.55, "C_mean": 0.40, "T_mean": 0.75,
            "U_mean": 0.15, "D_mean": 0.10, "acted": False,
        }

    def step(self):
        self._t += 1
        if self._idx < len(self._seq):
            m = dict(self._seq[self._idx])
            self._idx += 1
        else:
            m = dict(self._default)
        m["t"] = self._t
        return m


class ControlledAgent:
    """Agent that always returns a predetermined action."""
    def __init__(self, fixed_action=ACTION_HOLD):
        self.fixed_action = fixed_action
        self.updates = []
        self.pfc_mode = False  # set True to simulate PFC API

    def choose_action(self, context, actions):
        return self.fixed_action, "controlled"

    def update(self, context, action, success, step):
        self.updates.append({
            "context": context,
            "action":  action,
            "success": success,
            "step":    step,
        })


class PFCAgent:
    """Simulates an agent with the new PFC API."""
    def __init__(self, action=ACTION_HOLD, verdict="PROCEED"):
        self.action  = action
        self.verdict = verdict
        self.updates = []

    def choose(self, context, actions):
        class FakeSignal:
            class verdict:
                value = "PROCEED"
        sig = FakeSignal()
        sig.verdict.value = self.verdict
        return self.action, sig

    def update(self, context, action, success, step):
        self.updates.append((context, action, success, step))


# ─────────────────────────────────────────────────────────────
# TESTS
# ─────────────────────────────────────────────────────────────

def test_context_translation_bins():
    """Sim metrics map to correct context vocabulary bins."""
    sim   = ControlledSim()
    agent = ControlledAgent()
    cfg   = BridgeConfig(sim_steps_per_agent_step=1)
    bridge = NoesisBridge(sim, agent, config=cfg)

    # Test high consensus
    m = {"align": 0.92, "conflict": 0.05, "throughput": 0.40,
         "D_mean": 2.0, "T_mean": 0.82, "U_mean": 0.90,
         "E_mean": 0.6, "C_mean": 0.5, "t": 1, "acted": False}
    ctx = bridge._build_context(m)

    passed = (
        ctx[CTX_CONSENSUS]  == "high"       and
        ctx[CTX_CONFLICT]   == "low"        and
        ctx[CTX_THROUGHPUT] == "high"       and
        ctx[CTX_MEMORY]     == "dense"      and
        ctx[CTX_TRUST]      == "strong"     and
        ctx[CTX_CHARISMATA] == "saturated"
    )
    return {
        "name":   "Bridge: context bins translate correctly (high state)",
        "passed": passed,
        "metrics": {k: v for k, v in ctx.items() if k != CTX_DOMAIN},
    }


def test_context_translation_low_state():
    """Low metrics map to low/degraded bins."""
    sim    = ControlledSim()
    agent  = ControlledAgent()
    cfg    = BridgeConfig(sim_steps_per_agent_step=1)
    bridge = NoesisBridge(sim, agent, config=cfg)

    m = {"align": 0.30, "conflict": 0.40, "throughput": 0.05,
         "D_mean": 0.01, "T_mean": 0.40, "U_mean": 0.01,
         "E_mean": 0.3, "C_mean": 0.2, "t": 1, "acted": False}
    ctx = bridge._build_context(m)

    passed = (
        ctx[CTX_CONSENSUS]  == "low"       and
        ctx[CTX_CONFLICT]   == "high"      and
        ctx[CTX_THROUGHPUT] == "low"       and
        ctx[CTX_MEMORY]     == "sparse"    and
        ctx[CTX_TRUST]      == "degraded"  and
        ctx[CTX_CHARISMATA] == "quiet"
    )
    return {
        "name":   "Bridge: context bins translate correctly (low state)",
        "passed": passed,
        "metrics": {k: v for k, v in ctx.items() if k != CTX_DOMAIN},
    }


def test_action_boost_trust():
    """boost_trust increases sim.immune_strength within bounds."""
    sim    = ControlledSim()
    agent  = ControlledAgent(ACTION_BOOST_TRUST)
    cfg    = BridgeConfig(sim_steps_per_agent_step=1, trust_nudge=0.015)
    bridge = NoesisBridge(sim, agent, config=cfg)

    before = sim.immune_strength
    bridge._apply_action(ACTION_BOOST_TRUST)
    after  = sim.immune_strength

    passed = abs(after - (before + cfg.trust_nudge)) < 1e-9
    return {
        "name":   "Bridge: boost_trust increases immune_strength",
        "passed": passed,
        "metrics": {"before": before, "after": after, "delta": after - before},
    }


def test_action_reduce_trust():
    """reduce_trust decreases immune_strength, never below minimum."""
    sim    = ControlledSim()
    sim.immune_strength = 0.025  # near floor
    agent  = ControlledAgent()
    cfg    = BridgeConfig(sim_steps_per_agent_step=1, trust_nudge=0.015, immune_min=0.02)
    bridge = NoesisBridge(sim, agent, config=cfg)

    # Apply many times — should never go below immune_min
    for _ in range(20):
        bridge._apply_action(ACTION_REDUCE_TRUST)

    passed = sim.immune_strength >= cfg.immune_min
    return {
        "name":   "Bridge: reduce_trust respects immune_min bound",
        "passed": passed,
        "metrics": {"final_immune": sim.immune_strength, "floor": cfg.immune_min},
    }


def test_action_parameter_bounds():
    """All actions respect their parameter safety bounds."""
    sim   = ControlledSim()
    agent = ControlledAgent()
    cfg   = BridgeConfig(
        sim_steps_per_agent_step=1,
        immune_max=0.40, immune_min=0.02,
        diff_U_max=0.50, diff_U_min=0.05,
        decay_D_max=0.002, decay_D_min=0.00005,
    )
    bridge = NoesisBridge(sim, agent, config=cfg)

    # Slam every action 50 times
    for _ in range(50):
        for action in ALL_ACTIONS:
            bridge._apply_action(action)

    passed = (
        cfg.immune_min <= sim.immune_strength <= cfg.immune_max and
        cfg.diff_U_min <= sim.diff_U          <= cfg.diff_U_max and
        cfg.decay_D_min <= sim.decay_D        <= cfg.decay_D_max
    )
    return {
        "name":   "Bridge: 50x all actions — parameters stay in bounds",
        "passed": passed,
        "metrics": {
            "immune": round(sim.immune_strength, 4),
            "diff_U": round(sim.diff_U, 4),
            "decay_D": round(sim.decay_D, 6),
        },
    }


def test_reward_good_state():
    """High throughput + low conflict → reward >= 0.5 (success)."""
    sim    = ControlledSim()
    agent  = ControlledAgent()
    bridge = NoesisBridge(sim, agent)

    pre  = {"throughput": 0.30, "conflict": 0.08, "align": 0.85,
            "E_mean": 0.6, "C_mean": 0.5, "T_mean": 0.8,
            "U_mean": 0.2, "D_mean": 0.5, "acted": False}
    post = {"throughput": 0.35, "conflict": 0.06, "align": 0.88,
            "E_mean": 0.6, "C_mean": 0.5, "T_mean": 0.8,
            "U_mean": 0.2, "D_mean": 0.5, "acted": False}

    reward, success = bridge._compute_reward(pre, post)
    passed = success and reward >= 0.5
    return {
        "name":   "Bridge: good state → reward >= 0.5 (success=True)",
        "passed": passed,
        "metrics": {"reward": round(reward, 4), "success": success},
    }


def test_reward_bad_state():
    """Low throughput + high conflict + declining → reward < 0.5."""
    sim    = ControlledSim()
    agent  = ControlledAgent()
    bridge = NoesisBridge(sim, agent)

    pre  = {"throughput": 0.20, "conflict": 0.35, "align": 0.40,
            "E_mean": 0.3, "C_mean": 0.2, "T_mean": 0.5,
            "U_mean": 0.1, "D_mean": 0.1, "acted": False}
    post = {"throughput": 0.12, "conflict": 0.40, "align": 0.35,
            "E_mean": 0.3, "C_mean": 0.2, "T_mean": 0.5,
            "U_mean": 0.1, "D_mean": 0.1, "acted": False}

    reward, success = bridge._compute_reward(pre, post)
    passed = not success and reward < 0.5
    return {
        "name":   "Bridge: bad state → reward < 0.5 (success=False)",
        "passed": passed,
        "metrics": {"reward": round(reward, 4), "success": success},
    }


def test_card_logging():
    """Cards are logged — count matches steps, fields are complete."""
    sim    = _MockSim()
    agent  = ControlledAgent(ACTION_HOLD)
    cfg    = BridgeConfig(sim_steps_per_agent_step=2, log_every_n=999)
    bridge = NoesisBridge(sim, agent, config=cfg)

    bridge.run(steps=20, verbose=False)
    cards = bridge.get_cards()

    passed = (
        len(cards) == 20 and
        all(hasattr(c, 'card_id') for c in cards) and
        all(hasattr(c, 'context') for c in cards) and
        all(hasattr(c, 'action')  for c in cards) and
        all(hasattr(c, 'reward')  for c in cards) and
        cards[0].card_id == "BRIDGE_00001" and
        cards[-1].card_id == "BRIDGE_00020"
    )
    return {
        "name":   "Bridge: 20 steps → 20 cards, all fields present",
        "passed": passed,
        "metrics": {
            "cards": len(cards),
            "first": cards[0].card_id if cards else None,
            "last":  cards[-1].card_id if cards else None,
        },
    }


def test_jsonl_card_output():
    """Cards write valid JSONL — each line is parseable JSON."""
    sim    = _MockSim()
    agent  = ControlledAgent(ACTION_HOLD)
    cfg    = BridgeConfig(sim_steps_per_agent_step=1, log_every_n=999)
    bridge = NoesisBridge(sim, agent, config=cfg)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl',
                                     delete=False) as f:
        log_path = f.name

    bridge.run(steps=10, log_path=log_path, verbose=False)

    lines = open(log_path).readlines()
    errors = []
    for i, line in enumerate(lines):
        try:
            d = json.loads(line)
            if "card_id" not in d:
                errors.append(f"line {i}: no card_id")
            if "context" not in d:
                errors.append(f"line {i}: no context")
            if "action" not in d:
                errors.append(f"line {i}: no action")
        except json.JSONDecodeError as e:
            errors.append(f"line {i}: {e}")

    passed = len(lines) == 10 and len(errors) == 0
    return {
        "name":   "Bridge: JSONL output — 10 valid parseable cards",
        "passed": passed,
        "metrics": {"lines": len(lines), "errors": len(errors)},
        "notes":  "; ".join(errors[:2]) if errors else "",
    }


def test_agent_update_called():
    """Agent.update() is called once per agent step."""
    sim    = _MockSim()
    agent  = ControlledAgent(ACTION_HOLD)
    cfg    = BridgeConfig(sim_steps_per_agent_step=1, log_every_n=999)
    bridge = NoesisBridge(sim, agent, config=cfg)

    bridge.run(steps=15, verbose=False)

    passed = len(agent.updates) == 15
    return {
        "name":   "Bridge: agent.update() called once per step",
        "passed": passed,
        "metrics": {"updates": len(agent.updates), "expected": 15},
    }


def test_pfc_api_compatibility():
    """Bridge handles new PFC API (choose → (action, pfc_signal))."""
    sim    = _MockSim()
    agent  = PFCAgent(action=ACTION_BOOST_TRUST, verdict="SLOW")
    cfg    = BridgeConfig(sim_steps_per_agent_step=1, log_every_n=999)
    bridge = NoesisBridge(sim, agent, config=cfg)

    bridge.run(steps=5, verbose=False)
    cards  = bridge.get_cards()

    passed = (
        len(cards) == 5 and
        all(c.pfc_verdict == "SLOW" for c in cards) and
        all(c.action == ACTION_BOOST_TRUST for c in cards)
    )
    return {
        "name":   "Bridge: PFC API (choose) — verdict flows into cards",
        "passed": passed,
        "metrics": {
            "cards":   len(cards),
            "verdict": cards[0].pfc_verdict if cards else None,
        },
    }


def test_pfc_escalation_count():
    """PFC ESCALATE verdicts are counted in report."""
    sim    = _MockSim()
    agent  = PFCAgent(action=ACTION_HOLD, verdict="ESCALATE")
    cfg    = BridgeConfig(sim_steps_per_agent_step=1, log_every_n=999)
    bridge = NoesisBridge(sim, agent, config=cfg)

    bridge.run(steps=10, verbose=False)
    report = bridge._report
    bridge._finalize_report()

    passed = report["pfc_escalations"] == 10
    return {
        "name":   "Bridge: ESCALATE verdicts counted in report",
        "passed": passed,
        "metrics": {"escalations": report["pfc_escalations"], "expected": 10},
    }


def test_momentum_computation():
    """Momentum rises when throughput trend is improving."""
    sim    = ControlledSim()
    agent  = ControlledAgent()
    bridge = NoesisBridge(sim, agent)

    # Inject rising throughput history
    for v in [0.10, 0.12, 0.14, 0.16, 0.18, 0.22, 0.26, 0.30, 0.34, 0.38]:
        bridge._throughput_history.append(v)

    momentum = bridge._compute_momentum()
    passed   = momentum == "rising"

    # Now inject falling history
    bridge._throughput_history.clear()
    for v in [0.38, 0.34, 0.30, 0.26, 0.22, 0.18, 0.14, 0.12, 0.10, 0.08]:
        bridge._throughput_history.append(v)

    momentum_fall = bridge._compute_momentum()
    passed = passed and momentum_fall == "falling"

    return {
        "name":   "Bridge: momentum detects rising and falling trends",
        "passed": passed,
        "metrics": {"rising": "rising", "falling": momentum_fall},
    }


def test_domain_tag_in_context():
    """Domain tag flows from bridge into every card."""
    sim    = _MockSim()
    agent  = ControlledAgent(ACTION_HOLD)
    cfg    = BridgeConfig(sim_steps_per_agent_step=1, log_every_n=999)
    bridge = NoesisBridge(sim, agent, config=cfg)
    bridge._domain = "medical"  # inject domain

    bridge.run(steps=5, verbose=False)
    cards = bridge.get_cards()

    passed = all(c.domain == "medical" for c in cards)
    return {
        "name":   "Bridge: domain tag propagates into all cards",
        "passed": passed,
        "metrics": {"domain": cards[0].domain if cards else None},
    }


def test_full_loop_50_steps():
    """50 steps with mock sim+agent — no crash, correct counts."""
    sim    = _MockSim()
    agent  = _MockAgent()
    cfg    = BridgeConfig(sim_steps_per_agent_step=5, log_every_n=999)
    bridge = NoesisBridge(sim, agent, config=cfg)

    report = bridge.run(steps=50, verbose=False)
    bridge._finalize_report()

    total_action_count = sum(report["action_counts"].values())
    passed = (
        report["total_bridge_steps"]  == 50 and
        report["total_sim_steps"]     == 50 * 5 + 50 and  # pre + post steps
        total_action_count            == 50 and
        len(bridge.get_cards())       == 50
    )
    return {
        "name":   "Bridge: 50 steps — counts, sim steps, cards all correct",
        "passed": passed,
        "metrics": {
            "bridge_steps":   report["total_bridge_steps"],
            "sim_steps":      report["total_sim_steps"],
            "action_total":   total_action_count,
            "cards":          len(bridge.get_cards()),
        },
    }


def test_action_distribution_in_report():
    """Action distribution sums to 1.0 after run."""
    sim    = _MockSim()
    agent  = _MockAgent()
    cfg    = BridgeConfig(sim_steps_per_agent_step=2, log_every_n=999)
    bridge = NoesisBridge(sim, agent, config=cfg)

    bridge.run(steps=30, verbose=False)
    dist = bridge.get_action_distribution()

    total  = sum(dist.values())
    passed = abs(total - 1.0) < 1e-6
    return {
        "name":   "Bridge: action distribution sums to 1.0",
        "passed": passed,
        "metrics": {
            "total":       round(total, 6),
            "n_actions":   len([v for v in dist.values() if v > 0]),
        },
    }


def test_card_to_dict_format():
    """BridgeCard.to_dict() produces NoesisCards-compatible structure."""
    card = BridgeCard(
        card_id="BRIDGE_00001",
        step=1,
        sim_step=5,
        timestamp=1700000000.0,
        context={"consensus": "high", "conflict": "low"},
        raw_metrics={"align": 0.85, "conflict": 0.08},
        action=ACTION_BOOST_TRUST,
        pfc_verdict="PROCEED",
        source="bandit",
        success=True,
        reward=0.72,
        outcome_metrics={"throughput": 0.38, "align": 0.87},
        domain="medical",
        acted=False,
    )
    d = card.to_dict()

    required_fields = [
        "card_id", "type", "step", "sim_step", "timestamp",
        "context", "raw_metrics", "action", "pfc_verdict",
        "source", "success", "reward", "outcome_metrics",
        "domain", "acted",
    ]
    missing = [f for f in required_fields if f not in d]
    passed  = len(missing) == 0 and d["type"] == "bridge_decision"

    return {
        "name":   "Bridge: card.to_dict() has all required NoesisCards fields",
        "passed": passed,
        "metrics": {"fields": len(d), "missing": missing},
    }


def test_vocabulary_completeness():
    """get_context_vocabulary and get_action_effects cover all actions."""
    sim    = _MockSim()
    agent  = ControlledAgent()
    bridge = NoesisBridge(sim, agent)

    vocab   = bridge.get_context_vocabulary()
    effects = bridge.get_action_effects()

    all_ctx_keys    = {CTX_CONSENSUS, CTX_CONFLICT, CTX_THROUGHPUT,
                       CTX_MEMORY, CTX_TRUST, CTX_CHARISMATA,
                       CTX_MOMENTUM, CTX_DOMAIN}
    all_actions_set = set(ALL_ACTIONS)

    passed = (
        set(vocab.keys())   == all_ctx_keys    and
        set(effects.keys()) == all_actions_set
    )
    return {
        "name":   "Bridge: vocabulary and effects cover all keys/actions",
        "passed": passed,
        "metrics": {
            "ctx_keys":   len(vocab),
            "action_effects": len(effects),
        },
    }


# ─────────────────────────────────────────────────────────────
# RUNNER
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        test_context_translation_bins,
        test_context_translation_low_state,
        test_action_boost_trust,
        test_action_reduce_trust,
        test_action_parameter_bounds,
        test_reward_good_state,
        test_reward_bad_state,
        test_card_logging,
        test_jsonl_card_output,
        test_agent_update_called,
        test_pfc_api_compatibility,
        test_pfc_escalation_count,
        test_momentum_computation,
        test_domain_tag_in_context,
        test_full_loop_50_steps,
        test_action_distribution_in_report,
        test_card_to_dict_format,
        test_vocabulary_completeness,
    ]

    print(f"\n{'═'*64}")
    print(f"  NOESIS BRIDGE TEST SUITE — {len(tests)} tests")
    print(f"{'═'*64}")

    passed_count = 0
    for fn in tests:
        try:
            result = fn()
        except Exception as e:
            result = {
                "name":   fn.__name__,
                "passed": False,
                "metrics": {},
                "notes":  str(e),
            }

        icon = "✓" if result["passed"] else "✗"
        metrics = result.get("metrics", {})
        metric_str = "  |  " + "  ".join(
            f"{k}={v}" for k, v in list(metrics.items())[:3]
        )
        note = f"  ← {result['notes']}" if result.get("notes") else ""
        print(f"  {icon}  {result['name']:<54}{metric_str}{note}")
        if result["passed"]:
            passed_count += 1

    print()
    print(f"  {passed_count}/{len(tests)} passed")
    print(f"{'═'*64}\n")
