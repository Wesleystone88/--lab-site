"""
Observatory Runner
==================
Watch the agent learn. See the artifact.

This is the evidence environment.
Not a benchmark. Not a score.
A record of what the agent discovered.

Usage:
    python run_observatory.py --scenario triage --episodes 200
    python run_observatory.py --scenario navigation --episodes 300
    python run_observatory.py --scenario diagnosis --episodes 250
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, 'agents/deployable_biorag_hybrids')
sys.path.insert(0, '/home/claude/emergence_mvp')

from environments.observatory import ObservatoryEnv, SCENARIOS
from agents.deployable_biorag_hybrids.sext_biorag import SextBioRAGAgent
from bus.schemas import Action, ActionTier
from bus.bus import EnvironmentBus, AgentClient


# ============================================================
# OBSERVATORY ADAPTER
# Special adapter that feeds context directly to BioRAG
# and logs decision sources back to the environment
# ============================================================

class ObservatoryAdapter(AgentClient):
    """
    Adapter that bridges ObservatoryEnv ↔ SextBioRAGAgent.

    Key difference from standard adapter:
        - Actions are drawn from scenario action list, not ASSEMBLE/MINT/MUTATE
        - Outcome feedback goes back to the agent via update()
        - Source logs flow back to the environment for artifact
    """

    def __init__(self, bus, native_agent: SextBioRAGAgent, env: ObservatoryEnv, seed=42):
        super().__init__(bus)
        self.agent = native_agent
        self.env = env
        self.episode_num = 0
        self._last_condition = {}
        self._last_actions = []
        self._last_chosen = ''

    def select_action(self, obs) -> Action:
        task = obs.task if hasattr(obs, "task") else obs.get("task", {})
        ctx = task.get('context', {})
        actions = task.get('actions', ['A', 'B', 'C'])

        self._last_condition = ctx
        self._last_actions = actions

        # Let BioRAG choose
        chosen, source = self.agent.choose_action(ctx, actions)
        self._last_chosen = chosen
        self._last_source = source

        # Log source back to environment
        self.env.log_source(self.episode_num, source)

        return Action(
            tier=ActionTier.ASSEMBLE,
            payload={
                'op':      'choose',
                'result':  chosen,
                'source':  source,
                'primitives': [chosen],
                'used_library_primitive': False,
            }
        )

    def run_episode(self) -> float:
        self.episode_num += 1
        obs = self.bus.reset()
        action = self.select_action(obs)
        result = self.bus.act(action)

        # Feed outcome back into all 6 pillars
        info = result.info
        success = info.get('success', False)
        correct = info.get('correct', '')

        self.agent.update(
            condition=self._last_condition,
            action=self._last_chosen,
            success=success,
            step=self.episode_num,
        )

        return result.reward


# ============================================================
# MAIN RUN
# ============================================================

def run_observatory(
    scenario:    str  = 'triage',
    n_episodes:  int  = 200,
    seed:        int  = 42,
    verbose:     bool = True,
) -> str:
    """
    Run the observatory. Returns the artifact as a string.
    """

    print(f"\n{'='*60}")
    print(f"  EMERGENCE OBSERVATORY")
    print(f"  Scenario : {SCENARIOS[scenario]['display']}")
    print(f"  Episodes : {n_episodes}")
    print(f"  Agent    : SextBioRAG (6-pillar)")
    print(f"{'='*60}")
    print(f"\n  Hidden rules exist. Agent knows nothing.")
    print(f"  Watch what it learns.\n")

    # Build environment and agent
    env = ObservatoryEnv(scenario=scenario, seed=seed)
    native = SextBioRAGAgent(seed=seed)

    # Wire through bus
    bus = EnvironmentBus(env)
    adapter = ObservatoryAdapter(bus, native, env, seed=seed)

    # Run
    accuracy_window = []
    for ep in range(n_episodes):
        reward = adapter.run_episode()
        correct = env._episode_correct[-1] if env._episode_correct else 0
        accuracy_window.append(correct)

        if verbose and (ep + 1) % 50 == 0:
            recent_acc = sum(accuracy_window[-20:]) / min(20, len(accuracy_window))
            print(f"  ep {ep+1:4d} | accuracy(last20)={recent_acc:.0%}")

    # Extract artifact
    artifact = env.extract_artifact(native, n_episodes)

    print(f"\n{'='*60}")
    print(f"  LEARNING COMPLETE. Extracting artifact...")
    print(f"{'='*60}\n")

    rendered = artifact.render()
    print(rendered)

    # Save artifact
    os.makedirs('results/artifacts', exist_ok=True)
    filename = f"results/artifacts/observatory_{scenario}_{n_episodes}ep.json"
    with open(filename, 'w') as f:
        f.write(artifact.to_json())
    print(f"\n  Artifact saved: {filename}")

    return rendered


# ============================================================
# COMPARE: what cold agent says vs what learned agent says
# ============================================================

def compare_cold_vs_learned(scenario: str = 'triage', n_episodes: int = 200):
    """
    Side by side: agent on episode 1 vs episode N.
    This is the clearest possible evidence of emergence.
    """
    sc = SCENARIOS[scenario]
    test_cases = [
        {k: sc['context_values'][k][0] for k in sc['context_keys']},
        {k: sc['context_values'][k][-1] for k in sc['context_keys']},
        {k: sc['context_values'][k][len(sc['context_values'][k])//2]
         for k in sc['context_keys']},
    ]

    print(f"\n{'='*60}")
    print(f"  COLD vs LEARNED COMPARISON")
    print(f"  Scenario: {sc['display']}")
    print(f"{'='*60}")

    # Cold agent
    cold = SextBioRAGAgent(seed=42)
    print(f"\n  COLD AGENT (episode 0 — knows nothing):")
    for ctx in test_cases:
        chosen, source = cold.choose_action(ctx, sc['actions'])
        correct = sc['correct_fn'](ctx)
        mark = '✓' if chosen == correct else '✗'
        print(f"    {mark} context={ctx}")
        print(f"      chose={chosen} correct={correct} source={source}")

    # Train it
    env = ObservatoryEnv(scenario=scenario, seed=42)
    native = SextBioRAGAgent(seed=42)
    bus = EnvironmentBus(env)
    adapter = ObservatoryAdapter(bus, native, env, seed=42)

    print(f"\n  Training for {n_episodes} episodes...")
    for _ in range(n_episodes):
        adapter.run_episode()

    # Learned agent
    print(f"\n  LEARNED AGENT (episode {n_episodes}):")
    correct_count = 0
    for ctx in test_cases:
        chosen, source = native.choose_action(ctx, sc['actions'])
        correct = sc['correct_fn'](ctx)
        mark = '✓' if chosen == correct else '✗'
        if chosen == correct:
            correct_count += 1
        print(f"    {mark} context={ctx}")
        print(f"      chose={chosen} correct={correct} source={source}")

    print(f"\n  Accuracy after training: {correct_count}/{len(test_cases)}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--scenario',  default='triage',
                        choices=list(SCENARIOS.keys()))
    parser.add_argument('--episodes',  type=int, default=200)
    parser.add_argument('--seed',      type=int, default=42)
    parser.add_argument('--compare',   action='store_true',
                        help='Show cold vs learned side by side')
    args = parser.parse_args()

    if args.compare:
        compare_cold_vs_learned(args.scenario, args.episodes)
    else:
        run_observatory(args.scenario, args.episodes, args.seed)
