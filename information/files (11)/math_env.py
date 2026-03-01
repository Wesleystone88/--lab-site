"""
MathEnvironment MVP

Domain: algebraic expression simplification
Hidden invariants: commutativity, distributivity, factoring patterns

Tasks are generated from the same latent rules with varying surface.
The agent is never told what the invariants are.
"""

import sympy as sp
from sympy import symbols, expand, factor, simplify
import random
from dataclasses import dataclass
from bus.schemas import (
    Action, ActionTier, Observation, StepResult, ProbeResult,
    LibraryEntry
)


# ---------------------------------------------------------------------------
# Task generator (one generator for MVP — add more to defeat leakage later)
# ---------------------------------------------------------------------------

class TaskGenerator:
    """
    Generates expression transformation tasks.
    Hidden structure: distributivity and factoring always help.
    Surface: variable names, constants, ordering all vary.
    """

    VAR_POOLS = [
        ['x', 'y', 'z'],
        ['a', 'b', 'c'],
        ['u', 'v', 'w'],
        ['p', 'q', 'r'],
    ]

    def __init__(self, seed=None, style_index=0):
        self.rng = random.Random(seed)
        self.style_index = style_index  # which var pool — swap to test leakage

    def generate(self) -> dict:
        """Return a task: {input_expr, target_expr, hint_atoms}"""
        pool = self.VAR_POOLS[self.style_index % len(self.VAR_POOLS)]
        var_names = self.rng.sample(pool, 2)
        syms = symbols(' '.join(var_names))
        x, y = syms

        # Hidden invariant: (x + y)^2 = x^2 + 2xy + y^2
        # Task: given expanded form, find factored form
        # Varying surface: coefficients, which variable is which
        a = self.rng.randint(1, 4)
        b = self.rng.randint(1, 4)

        input_expr = expand((a*x + b*y)**2)
        target_expr = factor(input_expr)

        return {
            "input": str(input_expr),
            "target": str(target_expr),
            "variables": var_names,
            "atoms": self._make_atoms(x, y, a, b),
        }

    def _make_atoms(self, x, y, a, b):
        """Base operations the agent can combine."""
        return [
            str(x), str(y),
            str(a), str(b),
            f"({x} + {y})",
            f"({a}*{x} + {b}*{y})",
            "expand", "factor", "simplify",
        ]


# ---------------------------------------------------------------------------
# Cost model
# ---------------------------------------------------------------------------

COSTS = {
    ActionTier.ASSEMBLE: 0.05,
    ActionTier.MUTATE:   0.3,
    ActionTier.MINT:     1.0,
}

CAPACITY_TOTAL = 50   # total AST nodes the library can hold
EPISODE_BUDGET = 5.0  # reward budget per episode


# ---------------------------------------------------------------------------
# Library
# ---------------------------------------------------------------------------

class Library:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.primitives: dict[str, LibraryEntry] = {}
        self._next_id = 0

    def add(self, definition: str) -> tuple[bool, str]:
        """Try to add a primitive. Returns (success, id_or_reason)."""
        canonical = self._canonicalize(definition)
        size = self._estimate_size(canonical)

        if self.used_capacity + size > self.capacity:
            return False, "capacity_exceeded"

        pid = f"p{self._next_id}"
        self._next_id += 1
        self.primitives[pid] = LibraryEntry(
            id=pid,
            canonical_form=canonical,
            size=size,
        )
        return True, pid

    def use(self, pid: str) -> bool:
        if pid in self.primitives:
            self.primitives[pid].use_count += 1
            return True
        return False

    @property
    def used_capacity(self) -> int:
        return sum(p.size for p in self.primitives.values())

    def snapshot(self) -> list[LibraryEntry]:
        return list(self.primitives.values())

    def _canonicalize(self, expr_str: str) -> str:
        """Normalize: parse with sympy, convert back to string."""
        try:
            expr = sp.sympify(expr_str)
            return str(sp.expand(expr))  # canonical expanded form
        except Exception:
            return expr_str  # fallback: raw string

    def _estimate_size(self, canonical: str) -> int:
        """Rough AST size: token count as proxy."""
        return max(1, len(canonical.split()))


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

class MathEnvironment:
    def __init__(self, generator: TaskGenerator = None):
        self.generator = generator or TaskGenerator()
        self.library = Library(capacity=CAPACITY_TOTAL)
        self._current_task = None
        self._step = 0
        self._budget = EPISODE_BUDGET
        self._episode_id = 0

    def reset(self, episode_id: int = 0) -> Observation:
        self._current_task = self.generator.generate()
        self._step = 0
        self._budget = EPISODE_BUDGET
        self._episode_id = episode_id
        return self._observe()

    def step(self, action: Action) -> StepResult:
        cost = COSTS[action.tier]
        reward = 0.0
        info = {"cost": cost, "valid": True}

        self._budget -= cost

        if action.tier == ActionTier.ASSEMBLE:
            reward = self._handle_assemble(action.payload)

        elif action.tier == ActionTier.MUTATE:
            reward = self._handle_mutate(action.payload)

        elif action.tier == ActionTier.MINT:
            reward, info = self._handle_mint(action.payload, info)

        self._step += 1
        done = self._budget <= 0 or self._step >= 20

        return StepResult(
            observation=self._observe(),
            reward=reward - cost,
            done=done,
            info=info,
        )

    def run_probes(self, episode: int) -> ProbeResult:
        """
        MVP stub — run basic generator swap probe.
        Full implementation: swap generator style, measure perf delta.
        """
        return ProbeResult(
            episode=episode,
            delta_transfer=0.0,   # TODO: run alt generator
            delta_style=0.0,      # TODO: rename variables
            shortcut_index=0.0,   # TODO: adversarial tasks
            cache_index=0.0,      # TODO: near-dup vs far
            flags=[],
        )

    # ------------------------------------------------------------------
    # Action handlers
    # ------------------------------------------------------------------

    def _handle_assemble(self, payload: dict) -> float:
        """Combine primitives or atoms. Reward if result moves toward target."""
        primitives = payload.get("primitives", [])
        for pid in primitives:
            self.library.use(pid)

        result = payload.get("result", "")
        return self._score_result(result)

    def _handle_mutate(self, payload: dict) -> float:
        pid = payload.get("primitive_id", "")
        self.library.use(pid)
        result = payload.get("result", "")
        return self._score_result(result)

    def _handle_mint(self, payload: dict, info: dict) -> tuple[float, dict]:
        definition = payload.get("definition", "")
        success, result = self.library.add(definition)
        info["mint_success"] = success
        info["mint_result"] = result
        reward = 0.2 if success else -0.1   # small bonus for valid mint
        return reward, info

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    def _score_result(self, result_str: str) -> float:
        """Check if result matches target expression (symbolically)."""
        if not result_str or not self._current_task:
            return 0.0
        try:
            result_expr = sp.sympify(result_str)
            target_expr = sp.sympify(self._current_task["target"])
            diff = sp.simplify(result_expr - target_expr)
            if diff == 0:
                return 2.0   # full reward for correct answer
            # Partial: how close?
            return 0.0
        except Exception:
            return 0.0

    def _observe(self) -> Observation:
        return Observation(
            episode_id=self._episode_id,
            step=self._step,
            task=self._current_task or {},
            available_atoms=self._current_task.get("atoms", []) if self._current_task else [],
            library=self.library.snapshot(),
            capacity_used=self.library.used_capacity,
            capacity_total=CAPACITY_TOTAL,
            budget_remaining=self._budget,
        )
