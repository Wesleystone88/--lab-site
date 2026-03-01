"""
Experiment harness.

Wires together: environment → bus → agent → metrics → probes

Usage:
    python run_experiment.py

This is the MVP run. It demonstrates the full pipeline with null models.
Plug in a real agent by subclassing AgentClient and passing it in.
"""

import sys
sys.path.insert(0, '.')

from environment.math_env import MathEnvironment, TaskGenerator
from bus.bus import EnvironmentBus, AgentClient
from bus.schemas import Action, ActionTier, Observation
from agents.null_models import NullA_LibraryReset, NullB_NoMinting, NullC_EpisodicMemory
from metrics.tracker import MetricsTracker, EpisodeRecord

PROBE_INTERVAL = 25    # run diagnostic suite every N episodes
N_EPISODES     = 100   # total episodes per agent


# ---------------------------------------------------------------------------
# Simple candidate agent (placeholder — swap in your real agent here)
# ---------------------------------------------------------------------------

class CandidateAgent(AgentClient):
    """
    MVP candidate: tries to mint a primitive after seeing the same pattern twice,
    then reuses it. Demonstrates the pipeline, not intelligence.
    """
    import random as _random

    def __init__(self, bus: EnvironmentBus):
        super().__init__(bus)
        self._seen_inputs: dict[str, int] = {}
        self._rng = __import__('random').Random(42)

    def select_action(self, obs: Observation) -> Action:
        task_input = obs.task.get("input", "")
        self._seen_inputs[task_input] = self._seen_inputs.get(task_input, 0) + 1

        # If we've seen this pattern before and have budget, try minting
        if (self._seen_inputs[task_input] >= 2
                and obs.capacity_used < obs.capacity_total - 5
                and obs.step == 0):
            return Action(
                tier=ActionTier.MINT,
                payload={"definition": task_input, "name": "cached_pattern"}
            )

        # Otherwise assemble from library or atoms
        if obs.library and self._rng.random() > 0.5:
            pid = self._rng.choice([p.id for p in obs.library])
            return Action(
                tier=ActionTier.ASSEMBLE,
                payload={
                    "op": "combine",
                    "primitives": [pid],
                    "primitive_id": pid,
                    "used_library_primitive": True,
                    "result": obs.library[0].canonical_form,
                }
            )

        atoms = obs.available_atoms or ["x", "y"]
        chosen = self._rng.sample(atoms, min(2, len(atoms)))
        target = obs.task.get("target", "")
        return Action(
            tier=ActionTier.ASSEMBLE,
            payload={"op": "combine", "primitives": chosen, "result": target}
        )


# ---------------------------------------------------------------------------
# Run one agent for N episodes, return metrics summary
# ---------------------------------------------------------------------------

def run_agent(agent_class, agent_name: str, n_episodes: int = N_EPISODES) -> dict:
    env = MathEnvironment(TaskGenerator(seed=42))
    bus = EnvironmentBus(env)

    agent = agent_class(bus)
    tracker = MetricsTracker()

    print(f"\n{'='*50}")
    print(f"Running: {agent_name}")
    print(f"{'='*50}")

    for ep in range(n_episodes):
        obs = bus.reset()
        total_reward = 0.0
        trace = []

        while True:
            action = agent.select_action(obs)
            result = bus.act(action)

            trace.append({
                "tier": action.tier.name,
                "payload": str(action.payload),
                "reward": result.reward,
                "used_library_primitive": action.payload.get("used_library_primitive", False),
                "primitive_id": action.payload.get("primitive_id", None),
            })

            total_reward += result.reward
            obs = result.observation
            if result.done:
                break

        tracker.record(EpisodeRecord(
            episode_id=ep,
            total_reward=total_reward,
            trace=trace,
            library_snapshot=obs.library,
            library_used_ids={
                s.get("primitive_id") for s in trace
                if s.get("used_library_primitive")
            },
        ))

        # Online probe
        if (ep + 1) % PROBE_INTERVAL == 0:
            probe = bus.probe()
            print(f"  [Probe ep {ep+1}] flags={probe.flags or 'none'} "
                  f"ΔTransfer={probe.delta_transfer:.3f}")

        if (ep + 1) % 20 == 0:
            s = tracker.summary()
            print(f"  ep {ep+1:3d} | reward={s['mean_reward']:+.3f} | "
                  f"reuse={s['reuse_rate']:.2f} | bcg={s['bcg']:.1f}")

    return {agent_name: tracker.summary()}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    results = {}

    # Candidate
    results.update(run_agent(CandidateAgent, "Candidate"))

    # Null models
    results.update(run_agent(NullB_NoMinting,      "Null B (no minting)"))
    results.update(run_agent(NullC_EpisodicMemory, "Null C (episodic only)"))

    # Final comparison
    print(f"\n{'='*50}")
    print("RESULTS SUMMARY")
    print(f"{'='*50}")
    for name, summary in results.items():
        print(f"\n{name}:")
        for k, v in summary.items():
            if isinstance(v, float):
                print(f"  {k}: {v:.4f}")
            else:
                print(f"  {k}: {v}")

    print("\nEmergence check:")
    candidate = results.get("Candidate", {})
    null_b    = results.get("Null B (no minting)", {})
    null_c    = results.get("Null C (episodic only)", {})

    candidate_wins = (
        candidate.get("mean_reward", 0) > null_b.get("mean_reward", 0) and
        candidate.get("mean_reward", 0) > null_c.get("mean_reward", 0) and
        candidate.get("reuse_rate",  0) > null_b.get("reuse_rate",  0) and
        candidate.get("bcg",         0) > null_c.get("bcg",         0)
    )

    print(f"  Candidate beats all nulls: {candidate_wins}")
    if not candidate_wins:
        print("  → No emergence demonstrated yet. That's fine — this is the MVP.")
        print("  → Replace CandidateAgent with a real learning agent and rerun.")
