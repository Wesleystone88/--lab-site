"""
Math Algebraic Environment — Plugin v1
=======================================
Domain: Algebraic expression simplification
Hidden invariants: commutativity, distributivity, factoring

This is the environment we built and validated.
Now wrapped as a proper EnvironmentBase plugin.
Serves as the reference implementation other environments follow.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.base import EnvironmentBase, EnvironmentSpec
from environment.math_env import MathEnvironment, TaskGenerator


class MathAlgebraicEnv(EnvironmentBase):
    """
    Algebraic simplification wrapped as an engine plugin.

    What agents must discover:
        - Commutativity: a+b = b+a, so order doesn't matter
        - Distributivity: a(b+c) = ab+ac, enabling factoring
        - Factoring: (ax+by)^2 collapses to a reusable pattern

    Why this tests emergence:
        Every episode varies surface (variable names, coefficients).
        The underlying transformation is always the same.
        Agents that discover the pattern mint it once and reuse it.
        Agents that don't rediscover it every time and run out of budget.
    """

    def __init__(self, generator_style: int = 0, seed: int = 42):
        self._env = MathEnvironment(TaskGenerator(seed=seed, style_index=generator_style))
        self._seed = seed
        self._style = generator_style

    @property
    def spec(self) -> EnvironmentSpec:
        return EnvironmentSpec(
            name         = "math_algebraic",
            display_name = "Algebraic Simplification",
            domain       = "mathematics",
            description  = (
                "Transform expanded polynomial expressions into factored form. "
                "Hidden invariants: commutativity and distributivity. "
                "Surface varies: variable names, coefficients, ordering."
            ),
            difficulty   = 2,
            invariants   = ["commutativity", "distributivity", "binomial_expansion"],
            tags         = ["math", "symbolic", "factoring", "single_invariant_class"],
            version      = "1.0.0",
        )

    def reset(self, episode_id: int = 0) -> dict:
        obs = self._env.reset(episode_id=episode_id)
        return self._obs_to_dict(obs)

    def step(self, action) -> tuple:
        result = self._env.step(action)
        return (
            self._obs_to_dict(result.observation),
            result.reward,
            result.done,
            result.info,
        )

    def run_probes(self, episode: int) -> dict:
        probe = self._env.run_probes(episode)
        return {
            'delta_transfer':  probe.delta_transfer,
            'delta_style':     probe.delta_style,
            'shortcut_index':  probe.shortcut_index,
            'cache_index':     probe.cache_index,
            'flags':           probe.flags,
        }

    def _obs_to_dict(self, obs) -> dict:
        return {
            'episode_id':      obs.episode_id,
            'step':            obs.step,
            'task':            obs.task,
            'available_atoms': obs.available_atoms,
            'library':         [
                {
                    'id':             p.id,
                    'canonical_form': p.canonical_form,
                    'size':           p.size,
                    'use_count':      p.use_count,
                }
                for p in obs.library
            ],
            'capacity_total':  obs.capacity_total,
            'budget_remaining': obs.budget_remaining,
        }
