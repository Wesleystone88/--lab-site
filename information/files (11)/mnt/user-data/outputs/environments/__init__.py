"""
Environments — the plugin library.

Each environment is a self-contained module.
Import and register the ones you want to use.

Usage:
    from engine.engine import EnvironmentEngine
    from environments import register_all

    engine = EnvironmentEngine()
    register_all(engine)          # registers everything available
    engine.list_environments()    # see what's loaded
"""

from environments.math_algebraic import MathAlgebraicEnv
from environments.logic_implication import LogicImplicationEnv

# Registry of all available environments
# Add new ones here as they're built
_ALL_ENVIRONMENTS = [
    MathAlgebraicEnv,
    LogicImplicationEnv,
    # PartialCueEnv,            # exercises Hopfield attractor completion
    # InterferenceEnv,          # exercises dentate gyrus separation
    # TemporalStructureEnv,     # exercises TFE + hippocampal recency
]


def register_all(engine) -> None:
    """Register every available environment into the engine."""
    for env_class in _ALL_ENVIRONMENTS:
        engine.register(env_class)


def register(engine, *names: str) -> None:
    """Register specific environments by name."""
    lookup = {cls().spec.name: cls for cls in _ALL_ENVIRONMENTS}
    for name in names:
        if name not in lookup:
            raise ValueError(f"Unknown environment: {name}. Available: {list(lookup.keys())}")
        engine.register(lookup[name])
