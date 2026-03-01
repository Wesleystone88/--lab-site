"""
Bus schemas — the protocol contract.
Every agent and every environment speaks this language.
Nothing else crosses the boundary.
"""

from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum


# ---------------------------------------------------------------------------
# Action side (Agent → Environment)
# ---------------------------------------------------------------------------

class ActionTier(Enum):
    ASSEMBLE = 0   # Cheap: combine existing primitives
    MUTATE   = 1   # Costly: edit/perturb an existing primitive
    MINT     = 2   # Very costly: define a new primitive


@dataclass
class Action:
    tier: ActionTier
    payload: dict[str, Any]
    # Examples:
    # Tier 0: {"op": "combine", "primitives": ["p1", "p2"], "params": {...}}
    # Tier 1: {"op": "mutate", "primitive_id": "p3", "edits": [...]}
    # Tier 2: {"op": "mint", "definition": <expr>, "name": "my_macro"}


# ---------------------------------------------------------------------------
# Observation side (Environment → Agent)
# ---------------------------------------------------------------------------

@dataclass
class LibraryEntry:
    id: str
    canonical_form: str       # Normalized expression string
    size: int                 # AST node count (for capacity tracking)
    use_count: int = 0        # How many times it's been used


@dataclass
class Observation:
    episode_id: int
    step: int
    task: dict[str, Any]           # The current math task surface
    available_atoms: list[str]     # Base expressions agent can use
    library: list[LibraryEntry]    # Current primitive library
    capacity_used: int             # Σ s(p) so far
    capacity_total: int            # Hard limit C
    budget_remaining: float        # Reward budget for this episode


@dataclass
class StepResult:
    observation: Observation
    reward: float
    done: bool
    info: dict[str, Any] = field(default_factory=dict)
    # info carries: action cost paid, whether action was valid, etc.


# ---------------------------------------------------------------------------
# Probe side (Diagnostics — agent doesn't need to know)
# ---------------------------------------------------------------------------

@dataclass
class ProbeResult:
    episode: int
    delta_transfer: float        # perf drop under generator swap
    delta_style: float           # perf drop under renaming
    shortcut_index: float        # perf drop on adversarial tasks
    cache_index: float           # perf on near-dup vs far tasks
    flags: list[str]             # e.g. ["generator_overfit_warning"]
