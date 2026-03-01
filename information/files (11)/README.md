# Emergence MVP

A pressure chamber for measuring structural emergence in agents.
Domain: algebraic expression simplification (math first).

---

## Structure

```
emergence_mvp/
├── bus/
│   ├── schemas.py       # The protocol contract (Action, Observation, StepResult)
│   └── bus.py           # The airlock — environment ↔ agent boundary
├── environment/
│   └── math_env.py      # Math environment: tasks, costs, library, scoring
├── agents/
│   └── null_models.py   # Three null baselines (reset / no-mint / episodic)
├── metrics/
│   └── tracker.py       # BCG, Reuse Rate, Time-to-Stability
└── run_experiment.py    # Harness: wires everything, runs comparison
```

---

## The Bus (how to plug in your agent)

```python
from bus.bus import AgentClient, EnvironmentBus
from bus.schemas import Action, ActionTier, Observation

class MyAgent(AgentClient):
    def select_action(self, obs: Observation) -> Action:
        # obs.task         — current math problem
        # obs.library      — available primitives
        # obs.available_atoms — base operations
        # obs.budget_remaining — how much reward budget left
        return Action(
            tier=ActionTier.ASSEMBLE,
            payload={"op": "combine", "primitives": [...], "result": "..."}
        )

env = MathEnvironment()
bus = EnvironmentBus(env)
agent = MyAgent(bus)
reward = agent.run_episode()
```

That's the full interface. Any agent — LLM, RL, symbolic — connects here.

---

## Action tiers

| Tier | Cost | What it does |
|------|------|-------------|
| 0 ASSEMBLE | 0.05 | Combine existing primitives / atoms |
| 1 MUTATE   | 0.30 | Edit an existing primitive |
| 2 MINT     | 1.00 | Define a new primitive (uses library capacity) |

Library capacity is fixed at 50 AST nodes total.
Storage rent is implicit: holding a primitive costs capacity.
Usage cost is near-zero — reuse is never punished.

---

## Metrics

- **Reuse Rate** — fraction of steps using a library primitive
- **BCG** — behavioral compression gain (DL without library − DL with library)
- **Time to Stability** — episodes until reward variance drops below threshold

---

## Null models

| Null | Ablation | What it tests |
|------|----------|---------------|
| A (not yet wired) | Library resets each episode | Is persistence necessary? |
| B | No minting allowed | Are tasks solvable without abstraction? |
| C | Episodic cache, no library | Does persistence help without structure? |

Emergence is claimed only when the candidate beats all three on:
- mean reward
- reuse rate
- BCG
- cross-generator transfer (probe)

---

## What's MVP and what's next

**Done:**
- Bus protocol and schemas
- Math environment with costs and library
- Null models B and C
- BCG and Reuse Rate metrics
- Experiment harness with online probes (stub)

**Next iterations:**
- Multiple task generators (defeat leakage)
- Generator swap probe (online, not stub)
- Null A (library reset requires env-side hook)
- Real learning agent (RL or LLM-based)
- Golden set for ε calibration on primitive matching
- NetBCG (charge library description length)
