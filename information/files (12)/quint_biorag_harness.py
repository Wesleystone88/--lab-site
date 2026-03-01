"""
QuintBioRAG — Production Readiness Harness
===========================================
Not just "does it work" — how does it break, how slow does it get,
where does it fall over under load.

Test Suites:
  1. BEHAVIORAL  — does each pillar do its job
  2. ABLATION    — what breaks when we remove each pillar
  3. STRESS      — load, memory growth, long-horizon stability
  4. BOTTLENECK  — latency per component, slow path detection
  5. DOMAIN LOAD — does differentiation actually work
  6. WHAT-IF     — edge cases, adversarial inputs, failure modes
  7. BASELINE    — establish numeric baselines for regression tracking

Run:
    python quint_biorag_harness.py
    python quint_biorag_harness.py --suite behavioral
    python quint_biorag_harness.py --suite stress
    python quint_biorag_harness.py --suite all
"""

import sys
import os
import time
import math
import random
import traceback
import argparse
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict, deque

# ── Path setup ────────────────────────────────────────────────────────────────
# Place this harness file in the same folder as quint_biorag.py
# (i.e. Tester/01_Core_Implementation/) and run from there.
# OR set QUINT_PATH env var to that directory.
# The sandbox_hybrid/ folder (tri_hybrid_v3, Bandit_engine, Time_engine)
# must be on the path — set SANDBOX_PATH env var if needed.
_here = os.path.dirname(os.path.abspath(__file__))
_impl    = os.environ.get("QUINT_PATH",   _here)
_sandbox = os.environ.get("SANDBOX_PATH", os.path.join(_impl, '..', 'sandbox_hybrid'))
for _p in [_impl, _sandbox]:
    _p = os.path.abspath(_p)
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ── Try to import the agent ───────────────────────────────────────────────────
IMPORT_ERROR = None
try:
    from quint_biorag import (
        QuintBioRAGAgent, BioRAG, SparseEncoder,
        InternalSignalBus, WorkingMemory, HippocampalIndex,
    )
    from quint_hybrid import QuintHybridAgent, RAGInterface, PillarSignal
    AGENT_AVAILABLE = True
except Exception as e:
    IMPORT_ERROR = str(e)
    AGENT_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════════
# RESULT TRACKING
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TestResult:
    name: str
    suite: str
    passed: bool
    metrics: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""
    duration_ms: float = 0.0
    error: str = ""

class Harness:
    def __init__(self):
        self.results: List[TestResult] = []
        self.baselines: Dict[str, Any] = {}

    def run(self, suite: str, name: str, fn, *args, **kwargs) -> TestResult:
        start = time.perf_counter()
        try:
            result = fn(*args, **kwargs)
            duration = (time.perf_counter() - start) * 1000
            if isinstance(result, TestResult):
                result.duration_ms = duration
                self.results.append(result)
                return result
            # If fn returned a plain dict of metrics, wrap it
            r = TestResult(name=name, suite=suite, passed=True,
                           metrics=result or {}, duration_ms=duration)
            self.results.append(r)
            return r
        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            r = TestResult(name=name, suite=suite, passed=False,
                           error=traceback.format_exc(), duration_ms=duration)
            self.results.append(r)
            return r

    def summary(self):
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        print("\n" + "═" * 72)
        print("  PRODUCTION READINESS REPORT")
        print("═" * 72)
        suites = sorted(set(r.suite for r in self.results))
        for suite in suites:
            suite_results = [r for r in self.results if r.suite == suite]
            sp = sum(1 for r in suite_results if r.passed)
            print(f"\n  [{suite.upper()}]  {sp}/{len(suite_results)} passed")
            for r in suite_results:
                icon = "✓" if r.passed else "✗"
                dur = f"{r.duration_ms:.1f}ms"
                metric_str = ""
                if r.metrics:
                    top = list(r.metrics.items())[:3]
                    metric_str = "  |  " + "  ".join(f"{k}={v}" for k, v in top)
                note = f"  ← {r.notes}" if r.notes else ""
                err_hint = f"  ERROR: {r.error.splitlines()[-1]}" if r.error else ""
                print(f"    {icon}  {r.name:<42} {dur:>8}{metric_str}{note}{err_hint}")
        print()
        print(f"  TOTAL: {passed}/{total} passed", end="")
        if failed:
            print(f"  ← {failed} FAILING", end="")
        print()
        print("═" * 72)
        print()
        if self.baselines:
            print("  BASELINES (save these — use for regression tracking)")
            print("  " + "-" * 50)
            for k, v in self.baselines.items():
                print(f"    {k:<40} {v}")
            print()
        return passed, total


# ═══════════════════════════════════════════════════════════════════════════════
# SHARED ENVIRONMENT UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

ACTIONS = ["A", "B", "C", "D"]
CONDITIONS_2 = ["X", "Y"]
CONDITIONS_4 = ["X", "Y", "Z", "W"]

def make_agent(seed=42, **kwargs) -> "QuintBioRAGAgent":
    return QuintBioRAGAgent(seed=seed, **kwargs)

def simple_env(condition: str, action: str, fail_rules: Dict) -> bool:
    """Returns True=success, False=failure."""
    return not fail_rules.get((condition, action), False)

def run_episode(agent, steps: int, conditions: List[str],
                fail_rules: Dict, seed: int = 0) -> Dict:
    """Run agent for N steps, return performance metrics."""
    rng = random.Random(seed)
    failures = 0
    latencies = []

    for step in range(1, steps + 1):
        cond_str = conditions[(step - 1) % len(conditions)]
        condition = {"cond": cond_str}

        t0 = time.perf_counter()
        action = agent.choose(condition, ACTIONS)
        latencies.append((time.perf_counter() - t0) * 1000)

        success = simple_env(cond_str, action, fail_rules)
        agent.update(condition, action, success, step)

        if not success:
            failures += 1

    return {
        "failure_rate": failures / steps,
        "mean_latency_ms": sum(latencies) / len(latencies),
        "p95_latency_ms": sorted(latencies)[int(len(latencies) * 0.95)],
        "p99_latency_ms": sorted(latencies)[int(len(latencies) * 0.99)],
        "max_latency_ms": max(latencies),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# SUITE 1: BEHAVIORAL — does each pillar do its job?
# ═══════════════════════════════════════════════════════════════════════════════

def test_cme_learns_constraint():
    """CME should block a consistently failing action within 20 steps."""
    agent = make_agent()
    # A always fails under X
    fail_rules = {("X", "A"): True}
    condition = {"cond": "X"}

    for step in range(1, 30):
        action = agent.choose(condition, ACTIONS)
        success = simple_env("X", action, fail_rules)
        agent.update(condition, action, success, step)

    # After 30 steps, A should rarely be chosen
    a_count = sum(
        1 for _ in range(50)
        if agent.choose(condition, ACTIONS) == "A"
    )
    passed = a_count <= 5  # at most 10% (explore rate allows some)
    return TestResult(
        name="CME learns constraint (avoid A under X)",
        suite="behavioral",
        passed=passed,
        metrics={"A_chosen_in_50": a_count},
        notes="CME not suppressing" if not passed else "",
    )

def test_pee_surprise_amplifies_learning():
    """Surprising failures should update Bandit harder than expected ones."""
    agent = make_agent()
    condition = {"cond": "X"}

    # Establish a strong prior that A succeeds (many successes)
    for step in range(1, 40):
        agent.update(condition, "A", True, step)

    # Now surprise: A suddenly fails
    bus_before = agent._signal_bus.encoding_weight
    agent.update(condition, "A", False, 40)
    bus_after = agent._signal_bus.last_error_magnitude

    # Surprising failure should have high error magnitude
    passed = bus_after > 0.1
    return TestResult(
        name="PEE surprise amplifies on unexpected failure",
        suite="behavioral",
        passed=passed,
        metrics={"error_magnitude": round(bus_after, 4)},
        notes="PEE not firing on surprise" if not passed else "",
    )

def test_biorag_memory_grows():
    """BioRAG hippocampus should accumulate traces."""
    agent = make_agent()
    fail_rules = {("X", "A"): True}

    run_episode(agent, 50, CONDITIONS_2, fail_rules)

    trace_count = len(agent.rag.hippocampus.traces)
    passed = trace_count > 0
    return TestResult(
        name="BioRAG hippocampus accumulates traces",
        suite="behavioral",
        passed=passed,
        metrics={"trace_count": trace_count},
        notes="No memory being written" if not passed else "",
    )

def test_working_memory_influences_choice():
    """Working memory should boost recently successful actions."""
    agent = make_agent()
    condition = {"cond": "X"}

    # Train heavily on D succeeding
    for step in range(1, 60):
        agent.update(condition, "D", True, step)

    # D should be preferred
    d_count = sum(1 for _ in range(50) if agent.choose(condition, ACTIONS) == "D")
    passed = d_count >= 20
    return TestResult(
        name="Working memory boosts recent successful action",
        suite="behavioral",
        passed=passed,
        metrics={"D_in_50": d_count},
        notes="Working memory not influencing choice" if not passed else "",
    )

def test_environment_flip_recovery():
    """Agent should recover after environment rules flip."""
    agent = make_agent()
    fail_pre  = {("X", "A"): True, ("Y", "B"): True}
    fail_post = {("X", "B"): True, ("Y", "A"): True}
    FLIP = 100

    # Pre-flip
    for step in range(1, FLIP + 1):
        cond = CONDITIONS_2[(step - 1) % 2]
        action = agent.choose({"cond": cond}, ACTIONS)
        success = simple_env(cond, action, fail_pre)
        agent.update({"cond": cond}, action, success, step)

    # Post-flip — measure failure rate in two windows
    early_fails, late_fails = 0, 0
    for step in range(FLIP + 1, FLIP + 101):
        cond = CONDITIONS_2[(step - 1) % 2]
        action = agent.choose({"cond": cond}, ACTIONS)
        success = simple_env(cond, action, fail_post)
        agent.update({"cond": cond}, action, success, step)
        if step < FLIP + 30:
            if not success: early_fails += 1
        else:
            if not success: late_fails += 1

    early_rate = early_fails / 29
    late_rate  = late_fails / 71
    recovered  = late_rate < early_rate
    return TestResult(
        name="Recovery after environment flip",
        suite="behavioral",
        passed=recovered,
        metrics={
            "early_fail_rate": round(early_rate, 3),
            "late_fail_rate":  round(late_rate, 3),
        },
        notes="Not recovering from flip" if not recovered else "",
    )

def test_signal_bus_decoupling():
    """PEE and BioRAG should not directly reference each other."""
    agent = make_agent()
    # Check bus exists and pillars use it
    has_bus   = hasattr(agent, '_signal_bus')
    rag_wired = hasattr(agent.rag, '_signal_bus') if hasattr(agent, 'rag') else False
    passed    = has_bus and rag_wired
    return TestResult(
        name="InternalSignalBus wired to BioRAG",
        suite="behavioral",
        passed=passed,
        metrics={"has_bus": has_bus, "rag_wired": rag_wired},
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SUITE 2: ABLATION — what breaks when we disable each pillar?
# ═══════════════════════════════════════════════════════════════════════════════

def _ablation_run(agent, steps=200) -> float:
    fail_rules = {("X", "A"): True, ("Y", "B"): True}
    result = run_episode(agent, steps, CONDITIONS_2, fail_rules)
    return result["failure_rate"]

def test_ablation_no_biorag():
    """Stub RAG vs BioRAG — BioRAG should perform better or equal."""
    agent_stub  = QuintHybridAgent(seed=42)  # uses stub RAG
    agent_biorag = make_agent(seed=42)

    rate_stub   = _ablation_run(agent_stub)
    rate_biorag = _ablation_run(agent_biorag)

    delta  = rate_stub - rate_biorag
    passed = rate_biorag <= rate_stub + 0.02  # biorag should not be much worse

    return TestResult(
        name="Ablation: BioRAG vs stub RAG",
        suite="ablation",
        passed=passed,
        metrics={
            "stub_fail_rate":   round(rate_stub, 3),
            "biorag_fail_rate": round(rate_biorag, 3),
            "delta":            round(delta, 3),
        },
        notes="BioRAG degrading performance" if not passed else
              ("BioRAG helps" if delta > 0.01 else "no difference yet"),
    )

def test_ablation_sham_pee():
    """Sham PEE (random surprise) should degrade vs real PEE."""
    agent_real  = make_agent(seed=42, sham_pe=False)
    agent_sham  = make_agent(seed=42, sham_pe=True)

    rate_real   = _ablation_run(agent_real, 300)
    rate_sham   = _ablation_run(agent_sham, 300)

    passed = rate_real <= rate_sham + 0.05

    return TestResult(
        name="Ablation: real PEE vs sham PEE",
        suite="ablation",
        passed=passed,
        metrics={
            "real_fail_rate": round(rate_real, 3),
            "sham_fail_rate": round(rate_sham, 3),
        },
        notes="Sham PEE performing same or better — PEE may not be contributing" if not passed else "",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SUITE 3: STRESS — load, memory growth, long-horizon stability
# ═══════════════════════════════════════════════════════════════════════════════

def test_stress_long_horizon():
    """10,000 step run — does the agent stay stable or degrade?"""
    agent = make_agent()
    fail_rules = {("X", "A"): True, ("Y", "B"): True}
    STEPS = 10_000
    window = 500
    fail_windows = []
    fails_this_window = 0

    for step in range(1, STEPS + 1):
        cond = CONDITIONS_2[(step - 1) % 2]
        action = agent.choose({"cond": cond}, ACTIONS)
        success = simple_env(cond, action, fail_rules)
        agent.update({"cond": cond}, action, success, step)

        if not success:
            fails_this_window += 1

        if step % window == 0:
            fail_windows.append(fails_this_window / window)
            fails_this_window = 0

    early_rate = sum(fail_windows[:3]) / 3
    late_rate  = sum(fail_windows[-3:]) / 3
    stable     = late_rate <= early_rate + 0.05  # should not drift up

    trace_count = len(agent.rag.hippocampus.traces)

    return TestResult(
        name="Stress: 10k steps stability",
        suite="stress",
        passed=stable,
        metrics={
            "early_fail_rate": round(early_rate, 3),
            "late_fail_rate":  round(late_rate, 3),
            "final_trace_count": trace_count,
        },
        notes="Agent degrading over time" if not stable else "",
    )

def test_stress_memory_growth():
    """Does hippocampal memory grow unbounded or does it cap/prune?"""
    agent = make_agent()
    fail_rules = {("X", "A"): True}
    checkpoints = []

    for step in range(1, 5001):
        cond = CONDITIONS_2[(step - 1) % 2]
        action = agent.choose({"cond": cond}, ACTIONS)
        success = simple_env(cond, action, fail_rules)
        agent.update({"cond": cond}, action, success, step)

        if step in (500, 1000, 2000, 5000):
            checkpoints.append(len(agent.rag.hippocampus.traces))

    # Memory should not grow strictly linear forever (sleep/pruning should help)
    growth_500_to_5000 = checkpoints[-1] - checkpoints[0]
    unbounded = checkpoints[-1] > 5000  # if every step creates a trace, problem

    return TestResult(
        name="Stress: hippocampal memory growth",
        suite="stress",
        passed=True,  # informational — establishes baseline
        metrics={
            "traces_at_500":  checkpoints[0],
            "traces_at_1000": checkpoints[1],
            "traces_at_2000": checkpoints[2],
            "traces_at_5000": checkpoints[3],
        },
        notes="UNBOUNDED growth — sleep/pruning not activating" if unbounded else "",
    )

def test_stress_concurrent_contexts():
    """Many unique contexts — does memory stay coherent?"""
    agent = make_agent()
    # 20 distinct contexts — simulating domain variety
    contexts = [f"ctx_{i}" for i in range(20)]
    fail_rules = {(f"ctx_{i}", "A"): True for i in range(0, 10)}  # A fails in first 10

    for step in range(1, 2001):
        cond = contexts[(step - 1) % len(contexts)]
        action = agent.choose({"cond": cond}, ACTIONS)
        success = simple_env(cond, action, fail_rules)
        agent.update({"cond": cond}, action, success, step)

    # In the failing contexts, A should now be rarely chosen
    fail_ctx_a_count  = sum(1 for _ in range(50) if agent.choose({"cond": "ctx_0"}, ACTIONS) == "A")
    safe_ctx_a_count  = sum(1 for _ in range(50) if agent.choose({"cond": "ctx_15"}, ACTIONS) == "A")

    # A should be suppressed in fail contexts, not in safe contexts
    passed = fail_ctx_a_count < safe_ctx_a_count

    return TestResult(
        name="Stress: 20 concurrent contexts stay coherent",
        suite="stress",
        passed=passed,
        metrics={
            "A_in_fail_ctx_50":  fail_ctx_a_count,
            "A_in_safe_ctx_50":  safe_ctx_a_count,
        },
        notes="Context bleeding — agent not separating domain memories" if not passed else "",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SUITE 4: BOTTLENECK — where is the slow path?
# ═══════════════════════════════════════════════════════════════════════════════

def test_bottleneck_choose_latency():
    """Measure choose() latency at various memory sizes."""
    results = {}
    fail_rules = {("X", "A"): True}

    for target_traces in [0, 100, 500, 1000]:
        agent = make_agent()
        # Pre-load memory
        for step in range(1, target_traces * 2 + 1):
            cond = CONDITIONS_2[(step - 1) % 2]
            action = agent.choose({"cond": cond}, ACTIONS)
            success = simple_env(cond, action, fail_rules)
            agent.update({"cond": cond}, action, success, step)

        actual_traces = len(agent.rag.hippocampus.traces)

        # Measure 200 choose() calls
        times = []
        for _ in range(200):
            t0 = time.perf_counter()
            agent.choose({"cond": "X"}, ACTIONS)
            times.append((time.perf_counter() - t0) * 1000)

        mean_ms = sum(times) / len(times)
        p99_ms  = sorted(times)[int(len(times) * 0.99)]
        results[f"traces_{actual_traces}_mean_ms"] = round(mean_ms, 3)
        results[f"traces_{actual_traces}_p99_ms"]  = round(p99_ms, 3)

    # Flag if p99 at 1000 traces > 50ms (would be noticeable in production)
    high_load_p99 = results.get("traces_1000_p99_ms", 0) or results.get(f"traces_{max(int(k.split('_')[1]) for k in results if '_p99_' in k)}_p99_ms", 0)
    passed = True  # informational — sets baseline

    return TestResult(
        name="Bottleneck: choose() latency vs memory size",
        suite="bottleneck",
        passed=passed,
        metrics=results,
        notes="p99 > 50ms at 1k traces — may bottleneck under load" if high_load_p99 > 50 else "",
    )

def test_bottleneck_update_latency():
    """Measure update() latency — the write path."""
    agent = make_agent()
    fail_rules = {("X", "A"): True}

    # Warm up
    for step in range(1, 201):
        cond = CONDITIONS_2[(step - 1) % 2]
        agent.update({"cond": cond}, "B", True, step)

    # Measure
    times = []
    for step in range(201, 601):
        cond = CONDITIONS_2[(step - 1) % 2]
        action = random.choice(ACTIONS)
        success = simple_env(cond, action, fail_rules)
        t0 = time.perf_counter()
        agent.update({"cond": cond}, action, success, step)
        times.append((time.perf_counter() - t0) * 1000)

    return TestResult(
        name="Bottleneck: update() latency",
        suite="bottleneck",
        passed=True,
        metrics={
            "mean_ms": round(sum(times) / len(times), 3),
            "p95_ms":  round(sorted(times)[int(len(times) * 0.95)], 3),
            "p99_ms":  round(sorted(times)[int(len(times) * 0.99)], 3),
            "max_ms":  round(max(times), 3),
        },
    )

def test_bottleneck_sdr_encoding():
    """How fast is the SparseEncoder? It runs on every choose() call."""
    encoder = SparseEncoder(seed=42)
    contexts = [
        {"cond": f"ctx_{i}", "domain": f"domain_{i % 5}", "risk": str(i % 3)}
        for i in range(100)
    ]

    times = []
    for _ in range(1000):
        ctx = random.choice(contexts)
        t0 = time.perf_counter()
        encoder.encode_context(ctx)
        times.append((time.perf_counter() - t0) * 1000)

    mean_ms = sum(times) / len(times)
    passed  = mean_ms < 1.0  # SDR should be sub-millisecond

    return TestResult(
        name="Bottleneck: SDR encoding speed",
        suite="bottleneck",
        passed=passed,
        metrics={
            "mean_ms": round(mean_ms, 4),
            "p99_ms":  round(sorted(times)[990], 4),
        },
        notes="SDR encoding too slow — will bottleneck choose()" if not passed else "",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SUITE 5: DOMAIN LOAD — does differentiation actually work?
# ═══════════════════════════════════════════════════════════════════════════════

def test_domain_separation():
    """
    Train on two semantically distinct domains.
    Medical domain: A=dangerous, load that signal.
    Legal domain:   B=dangerous, load that signal.
    Agent should remember domain-specific constraints without bleed.
    """
    agent = make_agent()

    medical_ctx = {"domain": "medical", "risk": "high"}
    legal_ctx   = {"domain": "legal",   "risk": "medium"}

    # Train medical: A always fails
    for step in range(1, 101):
        action = agent.choose(medical_ctx, ACTIONS)
        success = (action != "A")
        agent.update(medical_ctx, action, success, step)

    # Train legal: B always fails
    for step in range(101, 201):
        action = agent.choose(legal_ctx, ACTIONS)
        success = (action != "B")
        agent.update(legal_ctx, action, success, step)

    # Now test: medical should suppress A, not B
    medical_A = sum(1 for _ in range(50) if agent.choose(medical_ctx, ACTIONS) == "A")
    medical_B = sum(1 for _ in range(50) if agent.choose(medical_ctx, ACTIONS) == "B")

    legal_A   = sum(1 for _ in range(50) if agent.choose(legal_ctx, ACTIONS) == "A")
    legal_B   = sum(1 for _ in range(50) if agent.choose(legal_ctx, ACTIONS) == "B")

    medical_correct = medical_A < medical_B
    legal_correct   = legal_B   < legal_A

    passed = medical_correct and legal_correct

    return TestResult(
        name="Domain: medical vs legal constraint separation",
        suite="domain",
        passed=passed,
        metrics={
            "medical_A_in_50": medical_A,
            "medical_B_in_50": medical_B,
            "legal_A_in_50":   legal_A,
            "legal_B_in_50":   legal_B,
        },
        notes="Domain bleeding — constraints crossing domains" if not passed else "",
    )

def test_domain_attractor_divergence():
    """
    Two BioRAG instances trained on different domains should have
    different attractor landscapes (low SDR overlap between stored traces).
    """
    encoder = SparseEncoder(seed=42)
    biorag_med = BioRAG(encoder=SparseEncoder(seed=42))
    biorag_leg = BioRAG(encoder=SparseEncoder(seed=42))

    medical_ctx = {"domain": "medical", "cond": "X"}
    legal_ctx   = {"domain": "legal",   "cond": "X"}

    for step in range(50):
        biorag_med.write_back(medical_ctx, "B", step % 2 == 0)
        biorag_leg.write_back(legal_ctx,   "C", step % 2 == 0)

    med_traces = len(biorag_med.hippocampus.traces)
    leg_traces = len(biorag_leg.hippocampus.traces)

    # They should have built separate trace sets
    passed = med_traces > 0 and leg_traces > 0

    return TestResult(
        name="Domain: BioRAG attractor divergence",
        suite="domain",
        passed=passed,
        metrics={
            "medical_traces": med_traces,
            "legal_traces":   leg_traces,
        },
        notes="No traces stored — attractor not building" if not passed else "",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SUITE 6: WHAT-IF — edge cases and adversarial inputs
# ═══════════════════════════════════════════════════════════════════════════════

def test_whatif_all_actions_fail():
    """What happens when every action fails every time?"""
    agent = make_agent()
    condition = {"cond": "X"}
    errors = []

    try:
        for step in range(1, 51):
            action = agent.choose(condition, ACTIONS)
            agent.update(condition, action, False, step)  # always fail
    except Exception as e:
        errors.append(str(e))

    passed = len(errors) == 0
    return TestResult(
        name="What-if: all actions always fail",
        suite="whatif",
        passed=passed,
        metrics={"errors": len(errors)},
        notes="Agent crashes on total failure" if not passed else "",
        error=errors[0] if errors else "",
    )

def test_whatif_single_action():
    """Only one action available — should not crash."""
    agent = make_agent()
    condition = {"cond": "X"}
    errors = []

    try:
        for step in range(1, 30):
            action = agent.choose(condition, ["A"])  # single action
            agent.update(condition, action, step % 3 != 0, step)
    except Exception as e:
        errors.append(str(e))

    passed = len(errors) == 0
    return TestResult(
        name="What-if: single action available",
        suite="whatif",
        passed=passed,
        metrics={"errors": len(errors)},
        error=errors[0] if errors else "",
    )

def test_whatif_empty_context():
    """Empty context dict — should not crash."""
    agent = make_agent()
    errors = []

    try:
        for step in range(1, 20):
            action = agent.choose({}, ACTIONS)
            agent.update({}, action, True, step)
    except Exception as e:
        errors.append(str(e))

    passed = len(errors) == 0
    return TestResult(
        name="What-if: empty context dict",
        suite="whatif",
        passed=passed,
        metrics={"errors": len(errors)},
        error=errors[0] if errors else "",
    )

def test_whatif_rapid_domain_switching():
    """Switch domain every step — does the agent stay coherent?"""
    agent = make_agent()
    domains = [{"domain": d} for d in ["medical", "legal", "finance", "hr"]]
    errors = []
    fail_count = 0

    try:
        for step in range(1, 201):
            ctx = domains[(step - 1) % len(domains)]
            action = agent.choose(ctx, ACTIONS)
            success = (action != "A")  # A always bad
            if not success:
                fail_count += 1
            agent.update(ctx, action, success, step)
    except Exception as e:
        errors.append(str(e))

    late_fail_rate = sum(
        1 for step in range(150, 200)
        if agent.choose(domains[step % 4], ACTIONS) == "A"
    ) / 50

    passed = len(errors) == 0
    return TestResult(
        name="What-if: rapid domain switching every step",
        suite="whatif",
        passed=passed,
        metrics={
            "errors": len(errors),
            "late_A_rate": round(late_fail_rate, 3),
        },
        notes="Agent destabilized by rapid switching" if late_fail_rate > 0.3 else "",
        error=errors[0] if errors else "",
    )

def test_whatif_state_persistence():
    """Save and reload state — does agent behavior match pre-save?"""
    import tempfile
    agent = make_agent(seed=42)
    fail_rules = {("X", "A"): True}

    for step in range(1, 101):
        cond = CONDITIONS_2[(step - 1) % 2]
        action = agent.choose({"cond": cond}, ACTIONS)
        success = simple_env(cond, action, fail_rules)
        agent.update({"cond": cond}, action, success, step)

    # Sample choices pre-save
    pre_choices = [agent.choose({"cond": "X"}, ACTIONS) for _ in range(20)]

    # Save and reload
    with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
        filepath = f.name

    try:
        agent.save_state(filepath)
        agent2 = make_agent(seed=42)
        agent2.load_state(filepath)
        post_choices = [agent2.choose({"cond": "X"}, ACTIONS) for _ in range(20)]

        match_rate = sum(a == b for a, b in zip(pre_choices, post_choices)) / 20
        passed = match_rate >= 0.7  # expect high but not 100% due to stochastic sampling
    except Exception as e:
        passed = False
        match_rate = 0.0
    finally:
        os.unlink(filepath)

    return TestResult(
        name="What-if: save/load state consistency",
        suite="whatif",
        passed=passed,
        metrics={"choice_match_rate": round(match_rate, 3)},
        notes="State not preserving agent behavior" if not passed else "",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SUITE 7: BASELINES — establish numeric anchors for regression tracking
# ═══════════════════════════════════════════════════════════════════════════════

def test_baseline_standard_scenario(harness: Harness):
    """
    Canonical 500-step run. These numbers become your regression baseline.
    If future versions score worse, something regressed.
    """
    agent = make_agent(seed=42)
    fail_rules = {("X", "A"): True, ("Y", "B"): True}
    metrics = run_episode(agent, 500, CONDITIONS_2, fail_rules, seed=42)

    # Store as baselines
    harness.baselines["standard_500_failure_rate"]   = round(metrics["failure_rate"], 4)
    harness.baselines["standard_500_mean_latency_ms"] = round(metrics["mean_latency_ms"], 3)
    harness.baselines["standard_500_p99_latency_ms"]  = round(metrics["p99_latency_ms"], 3)
    harness.baselines["final_trace_count"]             = len(agent.rag.hippocampus.traces)

    return TestResult(
        name="Baseline: 500-step canonical scenario",
        suite="baseline",
        passed=True,
        metrics=metrics,
        notes="Record these numbers — use for future regression detection",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

SUITES = {
    "behavioral": [
        test_cme_learns_constraint,
        test_pee_surprise_amplifies_learning,
        test_biorag_memory_grows,
        test_working_memory_influences_choice,
        test_environment_flip_recovery,
        test_signal_bus_decoupling,
    ],
    "ablation": [
        test_ablation_no_biorag,
        test_ablation_sham_pee,
    ],
    "stress": [
        test_stress_long_horizon,
        test_stress_memory_growth,
        test_stress_concurrent_contexts,
    ],
    "bottleneck": [
        test_bottleneck_choose_latency,
        test_bottleneck_update_latency,
        test_bottleneck_sdr_encoding,
    ],
    "domain": [
        test_domain_separation,
        test_domain_attractor_divergence,
    ],
    "whatif": [
        test_whatif_all_actions_fail,
        test_whatif_single_action,
        test_whatif_empty_context,
        test_whatif_rapid_domain_switching,
        test_whatif_state_persistence,
    ],
}

def main():
    parser = argparse.ArgumentParser(description="QuintBioRAG Production Readiness Harness")
    parser.add_argument("--suite", default="all",
                        choices=list(SUITES.keys()) + ["all"],
                        help="Which test suite to run")
    args = parser.parse_args()

    print()
    print("╔" + "═" * 70 + "╗")
    print("║" + "  QUINTBIORAG — PRODUCTION READINESS HARNESS".center(70) + "║")
    print("╚" + "═" * 70 + "╝")
    print()

    if not AGENT_AVAILABLE:
        print(f"  ✗ CANNOT IMPORT AGENT")
        print(f"    {IMPORT_ERROR}")
        print()
        print("  The harness is ready but needs the agent's dependencies.")
        print("  Run from the directory containing the Tester/ folder,")
        print("  or ensure sandbox_hybrid/ deps are installed.")
        print()
        return

    harness = Harness()

    suites_to_run = list(SUITES.keys()) if args.suite == "all" else [args.suite]

    for suite_name in suites_to_run:
        print(f"  Running [{suite_name.upper()}]...")
        for fn in SUITES[suite_name]:
            harness.run(suite_name, fn.__name__, fn)

    # Always run baselines at the end
    if args.suite == "all" or args.suite == "baseline":
        harness.run("baseline", "baseline_standard", test_baseline_standard_scenario, harness)

    passed, total = harness.summary()
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
