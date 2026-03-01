"""
EmerEviro Environment Engine
============================
The foundation. Everything else is a plugin.

Core principle:
    An environment is anything that implements EnvironmentBase.
    The engine loads it, wraps it in the bus, runs agents through it,
    and measures emergence. The environment doesn't know about agents.
    The agent doesn't know about environments. The engine connects them.

    Adding a new environment:
        1. Subclass EnvironmentBase
        2. Implement 4 methods: reset(), step(), run_probes(), info()
        3. Register it: engine.register(MyEnv, "my_env")
        4. Done. Every agent, every metric, every null model works with it.

Architecture:
    EnvironmentBase   — what every environment must implement
    EnvironmentSpec   — metadata: name, domain, invariants, difficulty
    EnvironmentEngine — loader, registry, run harness
    EnvironmentResult — structured output every run produces
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional
import time


# ============================================================
# ENVIRONMENT SPEC — metadata about what an environment tests
# ============================================================

@dataclass
class EnvironmentSpec:
    """
    What an environment is and what it's testing for.

    This is the passport an environment carries.
    The engine reads it to know how to configure runs,
    which metrics matter, and how to display results.

    Fields:
        name         : short identifier, used in registry + results
        display_name : human-readable
        domain       : broad category (math, logic, planning, language, ...)
        description  : what the hidden invariants are and why they matter
        difficulty   : 1 (easy) to 5 (hard) — calibrated across envs
        invariants   : list of the hidden rules agents must discover
        tags         : searchable labels (e.g. ["temporal", "interference"])
        version      : semver — bump when env changes so results stay comparable
    """
    name:         str
    display_name: str
    domain:       str
    description:  str
    difficulty:   int                    = 3
    invariants:   list[str]              = field(default_factory=list)
    tags:         list[str]              = field(default_factory=list)
    version:      str                    = "0.1.0"


# ============================================================
# ENVIRONMENT BASE — the contract every environment signs
# ============================================================

class EnvironmentBase(ABC):
    """
    The only thing an environment needs to be.

    Four methods. That's the entire contract.
    Everything else — bus, metrics, null models, probes — 
    is handled by the engine.

    The environment is a pressure chamber.
    It doesn't teach. It doesn't scaffold.
    It just applies pressure and measures what survives.
    """

    @property
    @abstractmethod
    def spec(self) -> EnvironmentSpec:
        """
        Return this environment's spec.
        Called once at registration time.
        """
        ...

    @abstractmethod
    def reset(self, episode_id: int = 0) -> dict:
        """
        Start a new episode. Return the initial observation dict.

        The observation dict is free-form — the environment defines its schema.
        The bus will wrap it into an Observation object.
        Convention: always include 'task', 'available_atoms', 'episode_id'.
        """
        ...

    @abstractmethod
    def step(self, action: Any) -> tuple[dict, float, bool, dict]:
        """
        Take an action. Return (observation, reward, done, info).

        observation : the new state (same schema as reset())
        reward      : scalar — positive for progress, negative for waste
        done        : True when episode ends
        info        : arbitrary metadata (costs paid, validity, etc.)
        """
        ...

    @abstractmethod
    def run_probes(self, episode: int) -> dict:
        """
        Run the diagnostic suite at scheduled intervals.

        Returns a probe result dict with at minimum:
            delta_transfer  : perf drop under generator swap
            delta_style     : perf drop under surface renaming
            shortcut_index  : perf drop on adversarial tasks
            cache_index     : near-dup vs far performance gap
            flags           : list of warning strings

        Stub these out if not yet implemented — 
        the engine handles missing probes gracefully.
        """
        ...

    def info(self) -> dict:
        """
        Optional: return runtime info about environment state.
        Useful for debugging and live dashboards.
        Default: empty dict.
        """
        return {}


# ============================================================
# ENVIRONMENT RESULT — structured output every run produces
# ============================================================

@dataclass
class EnvironmentResult:
    """
    Everything a run produces. Structured so results are comparable
    across environments, agents, and time.

    This is what gets saved to disk, submitted to leaderboards,
    and fed into analysis pipelines.
    """
    # Identity
    env_name:        str
    env_version:     str
    agent_name:      str
    run_id:          str
    timestamp:       float   = field(default_factory=time.time)

    # Episode stats
    n_episodes:      int     = 0
    mean_reward:     float   = 0.0
    reward_curve:    list    = field(default_factory=list)  # per-episode rewards

    # Emergence metrics
    reuse_rate:      float   = 0.0
    bcg:             float   = 0.0
    time_to_stability: int   = -1

    # Probe results (last probe run)
    delta_transfer:  float   = 0.0
    delta_style:     float   = 0.0
    shortcut_index:  float   = 0.0
    cache_index:     float   = 0.0
    probe_flags:     list    = field(default_factory=list)

    # Emergence verdict
    beats_null_b:    bool    = False
    beats_null_c:    bool    = False
    emergence:       bool    = False   # True only if beats ALL nulls on ALL metrics

    # Raw config for reproducibility
    config:          dict    = field(default_factory=dict)

    def summary(self) -> str:
        lines = [
            f"{'='*52}",
            f"  {self.agent_name} on {self.env_name} v{self.env_version}",
            f"{'='*52}",
            f"  Episodes        : {self.n_episodes}",
            f"  Mean Reward     : {self.mean_reward:+.4f}",
            f"  Reuse Rate      : {self.reuse_rate:.4f}",
            f"  BCG             : {self.bcg:.2f}",
            f"  Time-to-Stable  : {self.time_to_stability}",
            f"  Emergence       : {'✓ YES' if self.emergence else '✗ NO'}",
        ]
        if self.probe_flags:
            lines.append(f"  Probe Flags     : {self.probe_flags}")
        return "\n".join(lines)
