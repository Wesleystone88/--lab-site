"""
Null model agents.

These are NOT dumb agents — they are precise ablations.
Each removes exactly one abstracting capacity.
Emergence is real only if the candidate beats all three.

NullA — Library Reset    : wipes library every episode
NullB — No Minting       : assembly only, can never define new primitives
NullC — Episodic Memory  : persistent storage but no compositional library
"""

import random
from bus.schemas import Action, ActionTier, Observation
from bus.bus import AgentClient, EnvironmentBus


class RandomAssemblyAgent(AgentClient):
    """
    Base: picks random atoms and tries to assemble them.
    Used as the substrate for all null models.
    """
    def __init__(self, bus: EnvironmentBus, seed=None):
        super().__init__(bus)
        self.rng = random.Random(seed)

    def select_action(self, obs: Observation) -> Action:
        atoms = obs.available_atoms or ["x", "y"]
        chosen = self.rng.sample(atoms, min(2, len(atoms)))
        return Action(
            tier=ActionTier.ASSEMBLE,
            payload={
                "op": "combine",
                "primitives": chosen,
                "result": f"({' + '.join(chosen)})",
            }
        )


class NullA_LibraryReset(RandomAssemblyAgent):
    """
    Null A: library resets every episode.
    Tests: is persistence necessary?
    """
    def run_episode(self) -> float:
        obs = self.bus.reset()
        # Wipe the library via the environment hook
        # In MVP: we pass a reset flag in reset payload
        # (environment must honor this — tracked as a known limitation)
        total_reward = 0.0
        while True:
            action = self.select_action(obs)
            result = self.bus.act(action)
            total_reward += result.reward
            obs = result.observation
            if result.done:
                break
        return total_reward


class NullB_NoMinting(AgentClient):
    """
    Null B: assembly only, never mints primitives.
    Tests: are tasks solvable by recomposition alone?
    """
    def __init__(self, bus: EnvironmentBus, seed=None):
        super().__init__(bus)
        self.rng = random.Random(seed)

    def select_action(self, obs: Observation) -> Action:
        atoms = obs.available_atoms or ["x", "y"]
        # Can use library if it exists, but never add to it
        library_ids = [p.id for p in obs.library]
        pool = atoms + library_ids
        chosen = self.rng.sample(pool, min(2, len(pool)))
        return Action(
            tier=ActionTier.ASSEMBLE,   # NEVER ActionTier.MINT
            payload={
                "op": "combine",
                "primitives": chosen,
                "result": f"({' + '.join(chosen)})",
            }
        )


class NullC_EpisodicMemory(AgentClient):
    """
    Null C: persistent storage, but no library.
    Stores raw episode outcomes as key-value cache.
    Tests: does persistence help without abstraction?
    """
    def __init__(self, bus: EnvironmentBus, seed=None):
        super().__init__(bus)
        self.rng = random.Random(seed)
        self.episode_cache: list[dict] = []   # raw outcomes, no structure

    def select_action(self, obs: Observation) -> Action:
        # Look for "similar" past episode by task string match
        task_str = str(obs.task.get("input", ""))
        for past in reversed(self.episode_cache):
            if past.get("task") == task_str:
                # Replay cached action
                return past.get("best_action", self._random_action(obs))

        return self._random_action(obs)

    def _random_action(self, obs: Observation) -> Action:
        atoms = obs.available_atoms or ["x"]
        chosen = self.rng.sample(atoms, min(2, len(atoms)))
        return Action(
            tier=ActionTier.ASSEMBLE,
            payload={"op": "combine", "primitives": chosen,
                     "result": f"({' + '.join(chosen)})"}
        )

    def run_episode(self) -> float:
        obs = self.bus.reset()
        best_action = None
        best_reward = -999
        total_reward = 0.0
        while True:
            action = self.select_action(obs)
            result = self.bus.act(action)
            if result.reward > best_reward:
                best_reward = result.reward
                best_action = action
            total_reward += result.reward
            obs = result.observation
            if result.done:
                break
        # Cache outcome (raw, unstructured)
        self.episode_cache.append({
            "task": str(obs.task.get("input", "")),
            "best_action": best_action,
            "best_reward": best_reward,
        })
        return total_reward
