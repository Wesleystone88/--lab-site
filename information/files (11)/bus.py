"""
EnvironmentBus — the airlock.

The environment lives on one side.
The agent lives on the other.
This is the only passage between them.

Usage:
    bus = EnvironmentBus(environment)
    obs = bus.reset()
    result = bus.act(Action(tier=ActionTier.ASSEMBLE, payload={...}))
    probe = bus.probe()   # run diagnostic suite
"""

from bus.schemas import Action, Observation, StepResult, ProbeResult


class EnvironmentBus:
    def __init__(self, environment):
        self._env = environment
        self._episode_count = 0

    def reset(self) -> Observation:
        """Start a new episode. Returns initial observation."""
        self._episode_count += 1
        return self._env.reset(episode_id=self._episode_count)

    def act(self, action: Action) -> StepResult:
        """Submit an action. Returns next observation + reward."""
        # Validate action is well-formed before passing through
        self._validate(action)
        return self._env.step(action)

    def probe(self) -> ProbeResult:
        """
        Run the online diagnostic suite.
        Called every N episodes by the experiment harness.
        Agent does not call this — harness does.
        """
        return self._env.run_probes(self._episode_count)

    def _validate(self, action: Action):
        if action.tier is None:
            raise ValueError("Action must have a tier")
        if not isinstance(action.payload, dict):
            raise ValueError("Action payload must be a dict")


# ---------------------------------------------------------------------------
# Agent-side client — what agents implement
# ---------------------------------------------------------------------------

class AgentClient:
    """
    Base class for any agent connecting to the bus.
    Override select_action().
    """
    def __init__(self, bus: EnvironmentBus):
        self.bus = bus

    def select_action(self, obs: Observation) -> Action:
        raise NotImplementedError

    def run_episode(self) -> float:
        """Run one episode, return total reward."""
        obs = self.bus.reset()
        total_reward = 0.0
        while True:
            action = self.select_action(obs)
            result = self.bus.act(action)
            total_reward += result.reward
            obs = result.observation
            if result.done:
                break
        return total_reward
