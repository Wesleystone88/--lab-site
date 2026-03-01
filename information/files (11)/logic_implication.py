"""
Logic Implication Environment — Plugin v1
==========================================
Domain: Propositional logic chain resolution
Hidden invariants: modus ponens, transitivity, contradiction detection

Different from math_algebraic in a critical way:
    Math rewards finding the right FORM (factored expression).
    Logic rewards finding the right CONCLUSION (valid inference).

Why this matters for BioRAG agents:
    The Hopfield attractor should learn that certain premise patterns
    always resolve to the same conclusion. Pattern completion from
    partial premises is exactly what CA3 is built for.

    Interference testing: premises that look similar but lead to
    different conclusions stress the dentate gyrus separation.
"""

import sys
import os
import random
import sympy.logic.boolalg as boolalg
from sympy import symbols
from sympy.logic.inference import satisfiable

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.base import EnvironmentBase, EnvironmentSpec
from bus.schemas import Action, ActionTier


# ─────────────────────────────────────────────
# LOGIC TASK GENERATOR
# ─────────────────────────────────────────────

class LogicTaskGenerator:
    """
    Generates propositional logic chain problems.

    Hidden invariant: modus ponens (if A→B and A, then B)
    Surface varies: variable names, chain length, distractors

    Three rule types (varying difficulty):
        CHAIN     : A→B→C, given A, conclude C
        BRANCH    : A→B, A→C, given A, both B and C
        CONTRADICT: A→B, ¬B, conclude ¬A (modus tollens)
    """

    VAR_POOLS = [
        ['P', 'Q', 'R', 'S'],
        ['A', 'B', 'C', 'D'],
        ['X', 'Y', 'Z', 'W'],
        ['M', 'N', 'O', 'K'],
    ]

    RULE_TYPES = ['CHAIN', 'BRANCH', 'CONTRADICT']

    def __init__(self, seed: int = 42, style_index: int = 0):
        self.rng = random.Random(seed)
        self.style_index = style_index

    def generate(self) -> dict:
        pool = self.VAR_POOLS[self.style_index % len(self.VAR_POOLS)]
        vars_ = self.rng.sample(pool, 3)
        rule_type = self.rng.choice(self.RULE_TYPES)

        if rule_type == 'CHAIN':
            # A→B, B→C, given A — conclude C
            a, b, c = vars_
            premises = [f"{a}→{b}", f"{b}→{c}", f"{a}"]
            conclusion = c
            distractors = [f"¬{c}", f"{b}→{a}", f"¬{a}"]

        elif rule_type == 'BRANCH':
            # A→B, A→C, given A — conclude B∧C
            a, b, c = vars_
            premises = [f"{a}→{b}", f"{a}→{c}", f"{a}"]
            conclusion = f"{b}∧{c}"
            distractors = [f"¬{b}", f"¬{c}", f"{b}→{c}"]

        else:  # CONTRADICT / modus tollens
            # A→B, ¬B — conclude ¬A
            a, b, c = vars_
            premises = [f"{a}→{b}", f"¬{b}"]
            conclusion = f"¬{a}"
            distractors = [f"{a}", f"¬{b}→¬{a}", f"{b}"]

        # Available atoms: premises + conclusion + distractors
        atoms = premises + [conclusion] + distractors
        self.rng.shuffle(atoms)

        return {
            'rule_type':  rule_type,
            'premises':   premises,
            'conclusion': conclusion,
            'distractors': distractors,
            'atoms':      atoms,
            'variables':  vars_,
        }


# ─────────────────────────────────────────────
# COST MODEL (same structure as math env)
# ─────────────────────────────────────────────

COSTS = {
    ActionTier.ASSEMBLE: 0.05,
    ActionTier.MUTATE:   0.3,
    ActionTier.MINT:     1.0,
}

CAPACITY_TOTAL = 40
EPISODE_BUDGET = 5.0


# ─────────────────────────────────────────────
# LOGIC LIBRARY (stores reusable inference patterns)
# ─────────────────────────────────────────────

class LogicLibrary:
    def __init__(self, capacity: int = CAPACITY_TOTAL):
        self.capacity = capacity
        self.primitives: dict = {}
        self._next_id = 0

    def add(self, definition: str) -> tuple:
        size = max(1, len(definition.split()))
        if self.used_capacity + size > self.capacity:
            return False, 'capacity_exceeded'
        pid = f"lp{self._next_id}"
        self._next_id += 1
        self.primitives[pid] = {
            'id': pid,
            'canonical_form': definition.strip(),
            'size': size,
            'use_count': 0,
        }
        return True, pid

    def use(self, pid: str):
        if pid in self.primitives:
            self.primitives[pid]['use_count'] += 1

    @property
    def used_capacity(self) -> int:
        return sum(p['size'] for p in self.primitives.values())

    def snapshot(self) -> list:
        return list(self.primitives.values())


# ─────────────────────────────────────────────
# ENVIRONMENT
# ─────────────────────────────────────────────

class LogicImplicationEnv(EnvironmentBase):
    """
    Logic chain resolution as an emergence environment.

    The agent must derive valid conclusions from premises.
    Reusable inference patterns (modus ponens, transitivity)
    should be minted once and applied across episodes.
    """

    def __init__(self, style_index: int = 0, seed: int = 42):
        self.generator = LogicTaskGenerator(seed=seed, style_index=style_index)
        self.library = LogicLibrary()
        self._task = None
        self._step = 0
        self._budget = EPISODE_BUDGET
        self._episode_id = 0

    @property
    def spec(self) -> EnvironmentSpec:
        return EnvironmentSpec(
            name         = "logic_implication",
            display_name = "Logic Implication Chains",
            domain       = "logic",
            description  = (
                "Derive valid conclusions from propositional premises. "
                "Hidden invariants: modus ponens, transitivity, modus tollens. "
                "Surface varies: variable names, chain structure, distractors."
            ),
            difficulty   = 3,
            invariants   = ["modus_ponens", "transitivity", "modus_tollens",
                            "conjunction_introduction"],
            tags         = ["logic", "propositional", "inference", "interference"],
            version      = "1.0.0",
        )

    def reset(self, episode_id: int = 0) -> dict:
        self._task = self.generator.generate()
        self._step = 0
        self._budget = EPISODE_BUDGET
        self._episode_id = episode_id
        return self._observe()

    def step(self, action: Action) -> tuple:
        cost = COSTS.get(action.tier, 0.05)
        self._budget -= cost
        reward = 0.0
        info = {'cost': cost, 'valid': True}

        if action.tier == ActionTier.ASSEMBLE:
            result_str = action.payload.get('result', '')
            reward = self._score(result_str)

        elif action.tier == ActionTier.MUTATE:
            pid = action.payload.get('primitive_id', '')
            self.library.use(pid)
            result_str = action.payload.get('result', '')
            reward = self._score(result_str)

        elif action.tier == ActionTier.MINT:
            defn = action.payload.get('definition', '')
            ok, res = self.library.add(defn)
            info['mint_success'] = ok
            reward = 0.2 if ok else -0.1

        self._step += 1
        done = self._budget <= 0 or self._step >= 20

        return self._observe(), reward - cost, done, info

    def run_probes(self, episode: int) -> dict:
        return {
            'delta_transfer':  0.0,
            'delta_style':     0.0,
            'shortcut_index':  0.0,
            'cache_index':     0.0,
            'flags':           [],
        }

    def _score(self, result: str) -> float:
        if not result or not self._task:
            return 0.0
        # Clean comparison: strip spaces, normalize arrows
        norm = lambda s: s.replace(' ', '').replace('->', '→')
        if norm(result) == norm(self._task['conclusion']):
            return 2.0
        # Partial: was it at least a valid atom (not a distractor)?
        valid_atoms = self._task['premises'] + [self._task['conclusion']]
        if norm(result) in [norm(a) for a in valid_atoms]:
            return 0.3
        return 0.0

    def _observe(self) -> dict:
        return {
            'episode_id':       self._episode_id,
            'step':             self._step,
            'task': {
                'premises':     self._task.get('premises', []) if self._task else [],
                'conclusion':   self._task.get('conclusion', '?') if self._task else '?',
                'rule_type':    self._task.get('rule_type', '?') if self._task else '?',
                'input':        ' | '.join(self._task.get('premises', [])) if self._task else '',
                'target':       self._task.get('conclusion', '') if self._task else '',
            },
            'available_atoms':  self._task.get('atoms', []) if self._task else [],
            'library':          self.library.snapshot(),
            'capacity_total':   CAPACITY_TOTAL,
            'budget_remaining': self._budget,
        }
