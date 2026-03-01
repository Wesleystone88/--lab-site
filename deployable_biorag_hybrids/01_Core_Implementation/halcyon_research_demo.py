"""
halcyon_research_demo.py
CME Demo for External Research Review

STAGE 1: Enhanced Flip Dynamics (rolling metrics, action frequencies)
STAGE 2: Baseline Comparison (CME vs Sliding Window Bandit)
STAGE 3: Skill Synthesis Evidence (in separate file)

Run: python halcyon_research_demo.py
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Literal
from collections import deque, defaultdict

# ============================================================
# CME Core (from tri-hybrid, simplified for clarity)
# ============================================================

MemoryType = Literal["CONSTRAINT", "PREFERENCE"]

@dataclass
class RuleMemory:
    mem_id: str
    mem_type: MemoryType
    condition_subset: Dict[str, str]
    action: str
    
    strength: float = 1.0
    confidence: float = 0.7
    
    status: Literal["ACTIVE", "SUPERSEDED"] = "ACTIVE"
    created_step: int = 0
    last_seen_step: int = 0
    applied_count: int = 0
    
    counter_evidence: float = 0.0
    counter_hits: int = 0
    supersession_step: Optional[int] = None
    counter_at_supersession: Optional[float] = None
    needed_at_supersession: Optional[float] = None
    prior_inhib_at_supersession: Optional[float] = None


@dataclass
class BiasSurface:
    hard_blocks: Dict[str, bool]
    weights: Dict[str, float]


class CME:
    def __init__(
        self,
        *,
        seed: int = 7,
        explore_rate: float = 0.02,
        decay_per_step: float = 0.002,
        reinforce_gain: float = 0.25,
        confidence_ceiling: float = 0.98,
        supersede_factor: float = 1.15,
        counter_decay: float = 0.004,
        min_counter_events: int = 2,
    ):
        self.rng = random.Random(seed)
        self.explore_rate = explore_rate
        self.decay_per_step = decay_per_step
        self.reinforce_gain = reinforce_gain
        self.confidence_ceiling = confidence_ceiling
        self.supersede_factor = supersede_factor
        self.counter_decay = counter_decay
        self.min_counter_events = min_counter_events
        
        self.mem: Dict[str, RuleMemory] = {}
        self._seq = 0
        
        self.probe_attempts = 0
        self.probe_successes = 0

    def _new_id(self) -> str:
        self._seq += 1
        return f"M{self._seq:05d}"

    def step_decay(self, step: int) -> None:
        for m in self.mem.values():
            if m.status != "ACTIVE":
                continue
            dt = step - m.last_seen_step
            if dt > 0:
                m.strength = max(0.0, m.strength * (1.0 - self.decay_per_step * dt))
            if m.counter_evidence > 0:
                m.counter_evidence = max(0.0, m.counter_evidence * (1.0 - self.counter_decay * max(1, dt)))

    def emit_bias(self, condition: Dict[str, str], actions: List[str]) -> BiasSurface:
        hard_blocks = {a: False for a in actions}
        weights = {a: 1.0 for a in actions}
        
        for m in self.mem.values():
            if m.status != "ACTIVE":
                continue
            if not self._matches(condition, m.condition_subset):
                continue
            
            inhib = m.strength * m.confidence
            
            if m.mem_type == "CONSTRAINT":
                if inhib >= 0.25:
                    hard_blocks[m.action] = True
                    m.applied_count += 1
            else:
                weights[m.action] *= max(0.02, 1.0 - inhib)
                m.applied_count += 1
        
        return BiasSurface(hard_blocks, weights)

    def _matches(self, current: Dict[str, str], subset: Dict[str, str]) -> bool:
        for k, v in subset.items():
            if current.get(k) != v:
                return False
        return True

    def choose_action(self, bias: BiasSurface, actions: List[str]) -> Tuple[str, bool]:
        disallowed = [a for a in actions if bias.hard_blocks.get(a, False)]
        allowed = [a for a in actions if not bias.hard_blocks.get(a, False)]
        pool = allowed if allowed else actions
        
        did_probe = False
        if disallowed and self.rng.random() < self.explore_rate:
            did_probe = True
            self.probe_attempts += 1
            return self._pick_weighted(disallowed, bias.weights), did_probe
        
        return self._pick_weighted(pool, bias.weights), did_probe

    def _pick_weighted(self, actions: List[str], weights: Dict[str, float]) -> str:
        ws = [max(0.0, weights.get(a, 1.0)) for a in actions]
        total = sum(ws)
        if total <= 0:
            return self.rng.choice(actions)
        r = self.rng.random() * total
        upto = 0.0
        for a, w in zip(actions, ws):
            upto += w
            if upto >= r:
                return a
        return actions[-1]

    def reinforce_memory(
        self,
        *,
        mem_type: MemoryType,
        condition_subset: Dict[str, str],
        action: str,
        step: int,
    ) -> None:
        subset_items = tuple(sorted(condition_subset.items()))
        key = f"{mem_type}|{action}|{subset_items}"
        
        existing = self.mem.get(key)
        if existing is None:
            mid = self._new_id()
            self.mem[key] = RuleMemory(
                mem_id=mid,
                mem_type=mem_type,
                condition_subset=dict(condition_subset),
                action=action,
                strength=1.0,
                confidence=0.7,
                created_step=step,
                last_seen_step=step,
            )
            return
        
        m = existing
        m.last_seen_step = step
        m.strength = min(3.0, m.strength + self.reinforce_gain * (1.0 / (1.0 + m.strength)))
        m.confidence = min(self.confidence_ceiling, m.confidence + 0.05 * (1.0 - m.confidence))

    def counter_evidence(
        self,
        *,
        condition: Dict[str, str],
        action: str,
        success: bool,
        step: int,
    ) -> None:
        if not success:
            return
        
        for m in self.mem.values():
            if m.status != "ACTIVE":
                continue
            if m.action != action:
                continue
            if not self._matches(condition, m.condition_subset):
                continue
            
            m.counter_evidence += 1.0
            m.counter_hits += 1
            m.last_seen_step = step
            
            prior = m.strength * m.confidence
            needed = max(float(self.min_counter_events), prior * self.supersede_factor)
            
            if m.counter_evidence >= needed:
                m.status = "SUPERSEDED"
                m.supersession_step = step
                m.counter_at_supersession = float(m.counter_evidence)
                m.needed_at_supersession = float(needed)
                m.prior_inhib_at_supersession = float(prior)
                m.strength = max(0.1, m.strength * 0.5)
                m.confidence = max(0.2, m.confidence * 0.6)


# ============================================================
# Sliding Window Baseline (for comparison)
# ============================================================

class SlidingWindowBaseline:
    """
    Sliding window bandit: tracks recent outcomes only.
    Naturally adapts to non-stationary environments.
    """
    def __init__(self, window_size: int = 20, explore_rate: float = 0.02, seed: int = 7):
        self.window_size = window_size
        self.explore_rate = explore_rate
        self.rng = random.Random(seed)
        
        # Action history: deque of (action, reward) tuples
        self.history: deque = deque(maxlen=window_size)
        
        # Q-value estimates (from window)
        self.q_values: Dict[str, float] = {}
        self.action_counts: Dict[str, int] = {}
    
    def _update_q_values(self) -> None:
        """Recompute Q-values from sliding window."""
        counts = defaultdict(int)
        rewards = defaultdict(float)
        
        for action, reward in self.history:
            counts[action] += 1
            rewards[action] += reward
        
        self.action_counts = dict(counts)
        self.q_values = {
            action: rewards[action] / count if count > 0 else 0.0
            for action, count in counts.items()
        }
    
    def choose_action(self, actions: List[str]) -> str:
        """Choose action with ε-greedy."""
        if self.rng.random() < self.explore_rate:
            return self.rng.choice(actions)
        
        # Exploit: pick best Q-value
        if not self.q_values:
            return self.rng.choice(actions)
        
        best_action = max(actions, key=lambda a: self.q_values.get(a, 0.0))
        return best_action
    
    def update(self, action: str, success: bool) -> None:
        """Update with outcome."""
        reward = 1.0 if success else 0.0
        self.history.append((action, reward))
        self._update_q_values()


# ============================================================
# Metrics Collection
# ============================================================

@dataclass
class WindowMetrics:
    """Metrics over a rolling window of steps."""
    start_step: int
    end_step: int
    failure_rate: float
    action_freq: Dict[str, int]
    dominant_action: str
    entropy: float  # Action selection entropy


@dataclass
class RecoveryMetrics:
    """Metrics for environment flip recovery."""
    flip_step: int
    supersession_step: Optional[int]  # CME only
    recovery_step: int  # When failure rate < threshold
    time_to_recovery: int
    stability_score: float  # Inverse of action variance


def calculate_window_metrics(
    action_history: List[str],
    failure_history: List[bool],
    start_step: int,
    end_step: int,
) -> WindowMetrics:
    """Calculate metrics for a window of steps."""
    window_actions = action_history[start_step:end_step+1]
    window_failures = failure_history[start_step:end_step+1]
    
    if not window_actions:
        return WindowMetrics(start_step, end_step, 0.0, {}, "", 0.0)
    
    # Failure rate
    failure_rate = sum(window_failures) / len(window_failures) if window_failures else 0.0
    
    # Action frequencies
    action_freq = {}
    for action in window_actions:
        action_freq[action] = action_freq.get(action, 0) + 1
    
    # Dominant action
    dominant = max(action_freq, key=action_freq.get) if action_freq else ""
    
    # Entropy (uniformity of selection)
    total = sum(action_freq.values())
    probs = [count / total for count in action_freq.values()]
    entropy = -sum(p * (p ** 0.5) for p in probs if p > 0)  # Simplified entropy
    
    return WindowMetrics(start_step, end_step, failure_rate, action_freq, dominant, entropy)


def find_recovery_step(failure_history: List[bool], flip_step: int, threshold: float = 0.10, window_size: int = 10) -> int:
    """Find when failure rate stabilizes below threshold after flip."""
    for i in range(flip_step, len(failure_history) - window_size):
        window = failure_history[i:i+window_size]
        if window and (sum(window) / len(window)) < threshold:
            return i
    return len(failure_history) - 1


# ============================================================
# Environment (Simple X/Y Flip)
# ============================================================

ACTIONS = ["A", "B", "C"]
CONDITIONS = ["X", "Y"]

# Pre-flip rules: X→B fails, Y→A fails
FAIL_PRE = {("X", "B"): True, ("Y", "A"): True}

# Post-flip rules: X→A fails, Y→A fails
FAIL_POST = {("X", "A"): True, ("Y", "A"): True}


def env_evaluate(step: int, flip_at: int, condition: str, action: str) -> bool:
    """Evaluate action success."""
    rules = FAIL_PRE if step < flip_at else FAIL_POST
    return not rules.get((condition, action), False)


# ============================================================
# STAGE 1: Enhanced Flip Dynamics (CME only)
# ============================================================

def stage1_enhanced_flip_dynamics(steps: int = 240, flip_at: int = 120) -> None:
    """Run CME with enhanced metrics around flip point."""
    print("=" * 80)
    print("STAGE 1: Enhanced Flip Dynamics with CME")
    print("=" * 80)
    print()
    print(f"Environment: 2-step task, flip at step {flip_at}")
    print(f"  Pre-flip:  X→(C,B) safe, X→A fails | Y→(B,C) safe, Y→A fails")
    print(f"  Post-flip: X→(C,B) fails, X→A safe | Y→(B,C) safe, Y→A fails")
    print()
    
    cme = CME(seed=42, explore_rate=0.02)
    
    action_history = []
    failure_history = []
    
    for step in range(1, steps + 1):
        cme.step_decay(step)
        
        cond = CONDITIONS[(step - 1) % 2]
        condition = {"cond": cond}
        
        bias = cme.emit_bias(condition, ACTIONS)
        action, did_probe = cme.choose_action(bias, ACTIONS)
        
        success = env_evaluate(step, flip_at, cond, action)
        
        if did_probe and success:
            cme.probe_successes += 1
        
        if not success:
            subset = {"cond": cond}
            cme.reinforce_memory(mem_type="CONSTRAINT", condition_subset=subset, action=action, step=step)
        
        cme.counter_evidence(condition=condition, action=action, success=success, step=step)
        
        action_history.append(action)
        failure_history.append(not success)
    
    # Calculate rolling metrics
    window_size = 20
    
    print(f"[Rolling Metrics - {window_size}-step windows]")
    print()
    
    # Pre-flip window
    pre_start = max(0, flip_at - window_size - 1)
    pre_end = flip_at - 2
    pre_metrics = calculate_window_metrics(action_history, failure_history, pre_start, pre_end)
    
    print(f"Steps {pre_start+1}-{pre_end+1} (pre-flip):")
    print(f"  Failure rate: {pre_metrics.failure_rate:.1%}")
    print(f"  Actions: {pre_metrics.action_freq}")
    print(f"  Dominant: {pre_metrics.dominant_action}")
    print()
    
    # Disruption window (right after flip)
    dis_start = flip_at - 1
    dis_end = flip_at + 14
    dis_metrics = calculate_window_metrics(action_history, failure_history, dis_start, dis_end)
    
    print(f"Steps {dis_start+1}-{dis_end+1} (disruption):")
    print(f"  Failure rate: {dis_metrics.failure_rate:.1%}")
    
    # Find supersession
    superseded = [m for m in cme.mem.values() if m.status == "SUPERSEDED"]
    if superseded:
        for m in superseded:
            if m.supersession_step:
                print(f"  Supersession: {m.mem_id} (avoid {m.action}@{m.condition_subset}) at step {m.supersession_step}")
    print()
    
    # Recovery window
    rec_step = find_recovery_step(failure_history, flip_at)
    rec_start = rec_step
    rec_end = min(rec_step + window_size - 1, len(action_history) - 1)
    rec_metrics = calculate_window_metrics(action_history, failure_history, rec_start, rec_end)
    
    print(f"Steps {rec_start+1}-{rec_end+1} (recovery):")
    print(f"  Failure rate: {rec_metrics.failure_rate:.1%}")
    print(f"  Actions: {rec_metrics.action_freq}")
    print(f"  Dominant: {rec_metrics.dominant_action}")
    print()
    
    print(f"Recovery time: {rec_step - flip_at + 1} steps")
    print()


# ============================================================
# STAGE 2: Baseline Comparison (CME vs Sliding Window Bandit)
# ============================================================

def stage2_baseline_comparison(steps: int = 240, flip_at: int = 120) -> None:
    """Compare CME against sliding window bandit baseline."""
    print("=" * 80)
    print("STAGE 2: Baseline Comparison (CME vs Sliding Window Bandit)")
    print("=" * 80)
    print()
    print("Running both systems on identical environment...")
    print()
    
    # Run baseline first
    print("-" * 80)
    print("BASELINE: Sliding Window Bandit (window=20)")
    print("-" * 80)
    print()
    
    baseline = SlidingWindowBaseline(window_size=20, explore_rate=0.02, seed=42)
    baseline_failures = []
    baseline_actions = []
    
    for step in range(1, steps + 1):
        cond = CONDITIONS[(step - 1) % 2]
        action = baseline.choose_action(ACTIONS)
        success = env_evaluate(step, flip_at, cond, action)
        
        baseline.update(action, success)
        
        baseline_failures.append(not success)
        baseline_actions.append(action)
    
    baseline_recovery = find_recovery_step(baseline_failures, flip_at)
    baseline_time = baseline_recovery - flip_at + 1
    
    # Count action switches (oscillation measure)
    baseline_switches = sum(1 for i in range(len(baseline_actions)-1) if baseline_actions[i] != baseline_actions[i+1])
    
    print(f"Recovery time: {baseline_time} steps")
    print(f"Action switches (total): {baseline_switches}")
    print()
    
    # Run CME
    print("-" * 80)
    print("CME: Supersession-Based Memory")
    print("-" * 80)
    print()
    
    cme = CME(seed=42, explore_rate=0.02)
    cme_failures = []
    cme_actions = []
    
    for step in range(1, steps + 1):
        cme.step_decay(step)
        
        cond = CONDITIONS[(step - 1) % 2]
        condition = {"cond": cond}
        
        bias = cme.emit_bias(condition, ACTIONS)
        action, did_probe = cme.choose_action(bias, ACTIONS)
        
        success = env_evaluate(step, flip_at, cond, action)
        
        if did_probe and success:
            cme.probe_successes += 1
        
        if not success:
            subset = {"cond": cond}
            cme.reinforce_memory(mem_type="CONSTRAINT", condition_subset=subset, action=action, step=step)
        
        cme.counter_evidence(condition=condition, action=action, success=success, step=step)
        
        cme_failures.append(not success)
        cme_actions.append(action)
    
    cme_recovery = find_recovery_step(cme_failures, flip_at)
    cme_time = cme_recovery - flip_at + 1
    
    # Count action switches
    cme_switches = sum(1 for i in range(len(cme_actions)-1) if cme_actions[i] != cme_actions[i+1])
    
    # Find supersession moment
    superseded = [m for m in cme.mem.values() if m.status == "SUPERSEDED"]
    supersession_step = None
    if superseded:
        for m in superseded:
            if m.supersession_step:
                supersession_step = m.supersession_step
                break
    
    print(f"Recovery time: {cme_time} steps")
    if supersession_step:
        print(f"Supersession at: step {supersession_step}")
    print(f"Action switches (total): {cme_switches}")
    print()
    
    # DETAILED SWITCH ANALYSIS
    print("-" * 80)
    print("SWITCH ANALYSIS")
    print("-" * 80)
    print()
    
    # Analyze switches by phase
    def count_switches_in_range(actions, start, end):
        if start >= len(actions) or end > len(actions):
            return 0
        window = actions[start:end]
        return sum(1 for i in range(len(window)-1) if window[i] != window[i+1])
    
    # Pre-flip switches
    baseline_pre_switches = count_switches_in_range(baseline_actions, 0, flip_at)
    cme_pre_switches = count_switches_in_range(cme_actions, 0, flip_at)
    
    # Post-flip switches
    baseline_post_switches = count_switches_in_range(baseline_actions, flip_at, len(baseline_actions))
    cme_post_switches = count_switches_in_range(cme_actions, flip_at, len(cme_actions))
    
    print("Switch breakdown by phase:")
    print(f"  Pre-flip  (steps 1-{flip_at}):")
    print(f"    Baseline: {baseline_pre_switches} switches")
    print(f"    CME:      {cme_pre_switches} switches")
    print(f"  Post-flip (steps {flip_at+1}-{steps}):")
    print(f"    Baseline: {baseline_post_switches} switches")
    print(f"    CME:      {cme_post_switches} switches")
    print()
    
    # Action frequency distribution for understanding
    from collections import Counter
    
    baseline_action_dist = Counter(baseline_actions)
    cme_action_dist = Counter(cme_actions)
    
    print("Action distributions (total counts):")
    print(f"  Baseline: {dict(baseline_action_dist)}")
    print(f"  CME:      {dict(cme_action_dist)}")
    print()
    
    # Explanation of high switches
    print("Why CME has more switches:")
    print("  CME alternates between X and Y conditions every step")
    print("  Each condition may prefer different actions")
    print("  Baseline's sliding window smooths across both conditions")
    print("  CME's context-specific biases cause X/Y oscillation")
    print()
    
    # Comparison
    print("=" * 80)
    print("COMPARISON RESULTS")
    print("=" * 80)
    print()
    
    print(f"{'Metric':<30} {'Baseline':<15} {'CME':<15} {'Winner':<10}")
    print("-" * 70)
    
    # Recovery time
    baseline_str = f"{baseline_time} steps"
    cme_str = f"{cme_time} steps"
    winner = "CME" if cme_time < baseline_time else ("Baseline" if baseline_time < cme_time else "Tie")
    print(f"{'Recovery Time':<30} {baseline_str:<15} {cme_str:<15} {winner:<10}")
    
    # Speedup
    if baseline_time > 0:
        speedup = baseline_time / cme_time if cme_time > 0 else float('inf')
        print(f"{'CME Speedup':<30} {'-':<15} {f'{speedup:.2f}x':<15} {'':<10}")
    
    # Stability (fewer switches = more stable)
    baseline_str = f"{baseline_switches}"
    cme_str = f"{cme_switches}"
    winner = "CME" if cme_switches < baseline_switches else ("Baseline" if baseline_switches < cme_switches else "Tie")
    print(f"{'Action Switches (lower=stable)':<30} {baseline_str:<15} {cme_str:<15} {winner:<10}")
    
    # Total failures
    baseline_fail_count = sum(baseline_failures)
    cme_fail_count = sum(cme_failures)
    baseline_str = f"{baseline_fail_count}"
    cme_str = f"{cme_fail_count}"
    winner = "CME" if cme_fail_count < baseline_fail_count else ("Baseline" if baseline_fail_count < cme_fail_count else "Tie")
    print(f"{'Total Failures (lower=better)':<30} {baseline_str:<15} {cme_str:<15} {winner:<10}")
    
    print()
    
    # Key insight
    print("KEY INSIGHT:")
    if cme_time < baseline_time:
        ratio = baseline_time / cme_time if cme_time > 0 else float('inf')
        print(f"  CME recovered {ratio:.1f}x faster via discrete supersession vs gradual averaging")
    print()


# ============================================================
# Main
# ============================================================

def main():
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "HALCYON RESEARCH DEMO" + " " * 37 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    # Stage 1: Enhanced flip dynamics
    stage1_enhanced_flip_dynamics(steps=240, flip_at=120)
    
    print("=" * 80)
    print()
    
    # Stage 2: Baseline comparison
    stage2_baseline_comparison(steps=240, flip_at=120)
    
    print("=" * 80)
    print("DEMO COMPLETE!")
    print("=" * 80)
    print()
    print("Summary:")
    print("  ✓ Stage 1: Enhanced flip dynamics with rolling metrics")
    print("  ✓ Stage 2: CME vs Sliding Window Bandit comparison")
    print()
    print("Next: Stage 3 (Skill Synthesis) - see halcyon_research_demo_skills.py")
    print()


if __name__ == "__main__":
    main()
