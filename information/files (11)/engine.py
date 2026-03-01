"""
EnvironmentEngine
=================
The loader and run harness.

Responsibilities:
    - Registry: knows every installed environment by name
    - Loading: instantiates environments with correct config
    - Running: wraps in bus, feeds agents, collects metrics
    - Comparing: null model runs happen automatically
    - Saving: every run produces a structured EnvironmentResult

Usage:
    from engine.engine import EnvironmentEngine
    from environments.math_algebraic import MathAlgebraicEnv

    engine = EnvironmentEngine()
    engine.register(MathAlgebraicEnv)

    result = engine.run(
        env_name   = "math_algebraic",
        agent      = my_agent,
        n_episodes = 500,
    )
    print(result.summary())
"""

from __future__ import annotations

import sys
import os
import json
import time
import uuid
from typing import Type, Optional

# Engine internals
from engine.base import EnvironmentBase, EnvironmentResult

# Bus
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bus.bus import EnvironmentBus, AgentClient
from bus.schemas import Action, ActionTier, Observation

# Metrics
sys.path.insert(0, '/home/claude/emergence_mvp')
from metrics.tracker import MetricsTracker, EpisodeRecord


# ============================================================
# BUS ADAPTER — wraps any EnvironmentBase into the bus protocol
# ============================================================

class EnvironmentBusAdapter:
    """
    Makes any EnvironmentBase speak the bus protocol.
    The bus expects: reset(episode_id), step(action), run_probes(episode)
    EnvironmentBase provides exactly those — this is a thin shim.
    """
    def __init__(self, env: EnvironmentBase, probe_interval: int = 25):
        self._env = env
        self._probe_interval = probe_interval
        self._episode = 0
        self._library_capacity = 50      # default, overridable via config
        self._library_used = 0
        self._budget = 5.0

    def reset(self, episode_id: int = 0) -> Observation:
        self._episode = episode_id
        raw = self._env.reset(episode_id=episode_id)
        return self._to_observation(raw)

    def step(self, action: Action) -> tuple:
        obs_raw, reward, done, info = self._env.step(action)
        obs = self._to_observation(obs_raw)
        from bus.schemas import StepResult
        return StepResult(observation=obs, reward=reward, done=done, info=info)

    def run_probes(self, episode: int) -> dict:
        return self._env.run_probes(episode)

    def _to_observation(self, raw: dict) -> Observation:
        from bus.schemas import LibraryEntry
        library = [
            LibraryEntry(
                id=p.get('id', f'p{i}'),
                canonical_form=p.get('canonical_form', str(p)),
                size=p.get('size', 1),
                use_count=p.get('use_count', 0),
            )
            for i, p in enumerate(raw.get('library', []))
        ]
        return Observation(
            episode_id=raw.get('episode_id', self._episode),
            step=raw.get('step', 0),
            task=raw.get('task', {}),
            available_atoms=raw.get('available_atoms', []),
            library=library,
            capacity_used=sum(p.size for p in library),
            capacity_total=raw.get('capacity_total', self._library_capacity),
            budget_remaining=raw.get('budget_remaining', self._budget),
        )


# ============================================================
# ENGINE
# ============================================================

class EnvironmentEngine:
    """
    The central registry and run harness.

    One engine. Many environments. Any agent.
    """

    def __init__(self, results_dir: str = "results"):
        self._registry: dict[str, Type[EnvironmentBase]] = {}
        self._configs:  dict[str, dict] = {}
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)

    # ----------------------------------------------------------
    # REGISTRY
    # ----------------------------------------------------------

    def register(
        self,
        env_class: Type[EnvironmentBase],
        config: dict = None,
    ) -> None:
        """
        Register an environment class.
        The name comes from env_class().spec.name.

        Args:
            env_class : the EnvironmentBase subclass
            config    : optional default config dict passed to __init__
        """
        # Instantiate briefly just to get the spec
        probe = env_class()
        name = probe.spec.name
        self._registry[name] = env_class
        self._configs[name]  = config or {}
        print(f"[Engine] Registered: {name} ({probe.spec.domain}) v{probe.spec.version}")

    def list_environments(self) -> list[dict]:
        """List all registered environments with their specs."""
        results = []
        for name, cls in self._registry.items():
            spec = cls().spec
            results.append({
                'name':        spec.name,
                'domain':      spec.domain,
                'difficulty':  spec.difficulty,
                'version':     spec.version,
                'invariants':  spec.invariants,
                'tags':        spec.tags,
            })
        return results

    def load(self, env_name: str, config: dict = None) -> EnvironmentBase:
        """Instantiate a registered environment by name."""
        if env_name not in self._registry:
            raise ValueError(
                f"Environment '{env_name}' not registered. "
                f"Available: {list(self._registry.keys())}"
            )
        cls = self._registry[env_name]
        merged = {**self._configs.get(env_name, {}), **(config or {})}
        return cls(**merged) if merged else cls()

    # ----------------------------------------------------------
    # RUN
    # ----------------------------------------------------------

    def run(
        self,
        env_name:      str,
        agent_factory,                    # callable(bus) -> AgentClient
        agent_name:    str    = "agent",
        n_episodes:    int    = 100,
        probe_interval: int   = 25,
        env_config:    dict   = None,
        save:          bool   = True,
        verbose:       bool   = True,
    ) -> EnvironmentResult:
        """
        Run an agent on a registered environment.

        Args:
            env_name       : registered environment name
            agent_factory  : callable that takes a bus and returns an AgentClient
            agent_name     : label for results
            n_episodes     : how many episodes to run
            probe_interval : run diagnostic suite every N episodes
            env_config     : override env defaults
            save           : write result JSON to results_dir
            verbose        : print progress

        Returns:
            EnvironmentResult with all metrics filled in
        """
        run_id = str(uuid.uuid4())[:8]
        env = self.load(env_name, env_config)
        spec = env.spec

        if verbose:
            print(f"\n{'='*52}")
            print(f"  {agent_name} on {spec.display_name}")
            print(f"  {n_episodes} episodes | probe every {probe_interval}")
            print(f"{'='*52}")

        # Wire up
        adapter = EnvironmentBusAdapter(env, probe_interval)
        bus = EnvironmentBus(adapter)
        agent = agent_factory(bus)
        tracker = MetricsTracker()
        reward_curve = []
        last_probe = {}

        for ep in range(n_episodes):
            obs = bus.reset()
            total = 0.0
            trace = []

            while True:
                action = agent.select_action(obs)
                result = bus.act(action)
                trace.append({
                    'tier':                   action.tier.name,
                    'payload':                str(action.payload),
                    'reward':                 result.reward,
                    'used_library_primitive': action.payload.get('used_library_primitive', False),
                    'primitive_id':           action.payload.get('primitive_id'),
                })
                total += result.reward
                obs = result.observation
                if result.done:
                    break

            reward_curve.append(total)
            tracker.record(EpisodeRecord(
                episode_id=ep,
                total_reward=total,
                trace=trace,
                library_snapshot=obs.library,
                library_used_ids={
                    s.get('primitive_id') for s in trace
                    if s.get('used_library_primitive')
                },
            ))

            # Scheduled probe
            if (ep + 1) % probe_interval == 0:
                last_probe = bus.probe()
                if verbose and getattr(last_probe, 'flags', []):
                    print(f"  [probe ep{ep+1}] flags={last_probe.flags}")

            if verbose and (ep + 1) % max(1, n_episodes // 5) == 0:
                s = tracker.summary()
                print(f"  ep {ep+1:4d} | "
                      f"reward={s['mean_reward']:+.3f} | "
                      f"reuse={s['reuse_rate']:.3f} | "
                      f"bcg={s['bcg']:.1f}")

        summary = tracker.summary()

        result = EnvironmentResult(
            env_name       = env_name,
            env_version    = spec.version,
            agent_name     = agent_name,
            run_id         = run_id,
            timestamp      = time.time(),
            n_episodes     = n_episodes,
            mean_reward    = summary['mean_reward'],
            reward_curve   = reward_curve,
            reuse_rate     = summary['reuse_rate'],
            bcg            = summary['bcg'],
            time_to_stability = summary['time_to_stability'],
            delta_transfer = getattr(last_probe, 'delta_transfer', 0.0),
            delta_style    = getattr(last_probe, 'delta_style', 0.0),
            shortcut_index = getattr(last_probe, 'shortcut_index', 0.0),
            cache_index    = getattr(last_probe, 'cache_index', 0.0),
            probe_flags    = getattr(last_probe, 'flags', []),
            config         = {'n_episodes': n_episodes, 'env_config': env_config or {}},
        )

        if save:
            self._save(result)

        return result

    def run_suite(
        self,
        env_name:      str,
        agents:        dict,              # {agent_name: agent_factory}
        n_episodes:    int    = 100,
        probe_interval: int   = 25,
        env_config:    dict   = None,
        verbose:       bool   = True,
    ) -> dict[str, EnvironmentResult]:
        """
        Run multiple agents on the same environment.
        Returns dict of {agent_name: EnvironmentResult}.

        Automatically runs null models for comparison.
        Fills in emergence verdict by comparing against nulls.
        """
        from agents.null_models import NullB_NoMinting, NullC_EpisodicMemory

        all_agents = {
            **agents,
            '_null_b': lambda bus: NullB_NoMinting(bus, seed=42),
            '_null_c': lambda bus: NullC_EpisodicMemory(bus, seed=42),
        }

        results = {}
        for name, factory in all_agents.items():
            results[name] = self.run(
                env_name=env_name,
                agent_factory=factory,
                agent_name=name,
                n_episodes=n_episodes,
                probe_interval=probe_interval,
                env_config=env_config,
                verbose=verbose,
            )

        # Fill emergence verdicts
        null_b = results['_null_b']
        null_c = results['_null_c']
        for name, r in results.items():
            if name.startswith('_null'):
                continue
            r.beats_null_b = (
                r.mean_reward > null_b.mean_reward and
                r.reuse_rate  > null_b.reuse_rate
            )
            r.beats_null_c = (
                r.mean_reward > null_c.mean_reward and
                r.bcg         > null_c.bcg
            )
            r.emergence = r.beats_null_b and r.beats_null_c

        return results

    def compare(self, results: dict[str, EnvironmentResult]) -> str:
        """Print a comparison table of multiple results."""
        lines = [
            f"\n{'Agent':<28} {'Reward':>10} {'Reuse':>8} {'BCG':>10} {'Stable':>8} {'Emerge':>8}",
            '-' * 76,
        ]
        for name, r in results.items():
            if name.startswith('_null'):
                continue
            emerge = '✓' if r.emergence else '✗'
            lines.append(
                f"{name:<28} {r.mean_reward:>+10.3f} {r.reuse_rate:>8.3f} "
                f"{r.bcg:>10.1f} {r.time_to_stability:>8} {emerge:>8}"
            )
        # Null baselines at the bottom
        for name, r in results.items():
            if name.startswith('_null'):
                label = 'Null B (no-mint)' if 'b' in name else 'Null C (episodic)'
                lines.append(
                    f"  [{label}]{'':>10} {r.mean_reward:>+10.3f} {r.reuse_rate:>8.3f} "
                    f"{r.bcg:>10.1f} {r.time_to_stability:>8} {'—':>8}"
                )
        return '\n'.join(lines)

    # ----------------------------------------------------------
    # PERSISTENCE
    # ----------------------------------------------------------

    def _save(self, result: EnvironmentResult) -> str:
        filename = f"{result.env_name}_{result.agent_name}_{result.run_id}.json"
        path = os.path.join(self.results_dir, filename)
        data = {k: v for k, v in result.__dict__.items() if not k.startswith('_')}
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return path

    def load_result(self, path: str) -> EnvironmentResult:
        with open(path) as f:
            data = json.load(f)
        return EnvironmentResult(**data)
