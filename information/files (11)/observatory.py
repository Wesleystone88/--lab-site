"""
Emergence Observatory Environment
==================================
Domain: Knowledge Synthesis Under Hidden Structure

This is NOT a scored task environment.
This is an OBSERVATORY.

Design philosophy:
    Every other environment asks: "did it get the right answer?"
    This one asks: "what did it learn, and can you see it happening?"

    The agent is given:
        - A domain with hidden structure (e.g. triage rules, navigation laws)
        - Enough context to discover the rules if it pays attention
        - Tasks that are impossible to solve by random guessing alone
        - No hints about what the rules ARE

    The output is not a score.
    The output is an ARTIFACT:
        - What the agent now believes (Bandit Q-values as a policy table)
        - What it remembered (hippocampal traces, salience-weighted)
        - What it pinned as critical (high-salience, immune to forgetting)
        - What it learned to avoid (CME constraint memory)
        - How its confidence evolved (decision source over time)

    You watch it go from knowing nothing to knowing something.
    That is the evidence.

Three built-in scenarios (each with hidden invariants):
    TRIAGE    : medical prioritization (severity × resource)
    NAVIGATION: route selection (risk × urgency × cost)
    DIAGNOSIS : symptom → condition mapping (pattern recognition)
"""

from __future__ import annotations

import sys
import os
import random
import json
import time
from dataclasses import dataclass, field
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.base import EnvironmentBase, EnvironmentSpec
from bus.schemas import Action, ActionTier


# ============================================================
# SCENARIOS — each is a hidden-rule world
# ============================================================

SCENARIOS = {

    # ──────────────────────────────────────────────────────
    # TRIAGE
    # Hidden invariant: severity dominates, then resource availability
    # Rule: critical→treat_first always; minor+scarce→defer always
    # ──────────────────────────────────────────────────────
    'triage': {
        'display': 'Emergency Triage',
        'description': 'Allocate care under resource constraints.',
        'hidden_rules': [
            'Critical severity always gets treated first',
            'Minor cases defer when resources are scarce',
            'Moderate cases wait when resources are ample',
        ],
        'context_keys': ['severity', 'resource', 'wait_time'],
        'context_values': {
            'severity':  ['critical', 'moderate', 'minor'],
            'resource':  ['scarce', 'ample'],
            'wait_time': ['short', 'long'],
        },
        'actions': ['TREAT_FIRST', 'WAIT', 'DEFER'],
        'correct_fn': lambda ctx: (
            'TREAT_FIRST' if ctx['severity'] == 'critical' else
            'DEFER'       if ctx['severity'] == 'minor' and ctx['resource'] == 'scarce' else
            'WAIT'
        ),
        'atoms': ['severity=critical', 'severity=moderate', 'severity=minor',
                  'resource=scarce', 'resource=ample',
                  'TREAT_FIRST', 'WAIT', 'DEFER'],
    },

    # ──────────────────────────────────────────────────────
    # NAVIGATION
    # Hidden invariant: risk ceiling, then urgency, then cost
    # Rule: never take high-risk route; urgent+low-cost→fast route
    # ──────────────────────────────────────────────────────
    'navigation': {
        'display': 'Route Navigation',
        'description': 'Select optimal routes under risk/urgency constraints.',
        'hidden_rules': [
            'Never take high-risk routes regardless of urgency',
            'Urgent + low-cost → always take fast route',
            'Low urgency → always take scenic (low-risk) route',
        ],
        'context_keys': ['risk', 'urgency', 'cost'],
        'context_values': {
            'risk':    ['high', 'medium', 'low'],
            'urgency': ['urgent', 'normal', 'relaxed'],
            'cost':    ['high', 'low'],
        },
        'actions': ['FAST_ROUTE', 'SAFE_ROUTE', 'SCENIC_ROUTE'],
        'correct_fn': lambda ctx: (
            'SAFE_ROUTE'   if ctx['risk'] == 'high' else
            'FAST_ROUTE'   if ctx['urgency'] == 'urgent' and ctx['cost'] == 'low' else
            'SCENIC_ROUTE' if ctx['urgency'] == 'relaxed' else
            'SAFE_ROUTE'
        ),
        'atoms': ['risk=high', 'risk=medium', 'risk=low',
                  'urgency=urgent', 'urgency=relaxed',
                  'cost=high', 'cost=low',
                  'FAST_ROUTE', 'SAFE_ROUTE', 'SCENIC_ROUTE'],
    },

    # ──────────────────────────────────────────────────────
    # DIAGNOSIS
    # Hidden invariant: symptom clusters map to conditions
    # Rule: fever+rash→viral; pain+swelling→injury; fatigue+pale→anemia
    # ──────────────────────────────────────────────────────
    'diagnosis': {
        'display': 'Pattern Diagnosis',
        'description': 'Map symptom patterns to conditions.',
        'hidden_rules': [
            'Fever + rash → viral infection',
            'Pain + swelling → physical injury',
            'Fatigue + pallor → anemic condition',
            'Multiple signals → dominant pattern wins',
        ],
        'context_keys': ['symptom_a', 'symptom_b', 'duration'],
        'context_values': {
            'symptom_a': ['fever', 'pain', 'fatigue'],
            'symptom_b': ['rash', 'swelling', 'pallor'],
            'duration':  ['acute', 'chronic'],
        },
        'actions': ['VIRAL', 'INJURY', 'ANEMIA', 'UNCLEAR'],
        'correct_fn': lambda ctx: (
            'VIRAL'  if ctx['symptom_a'] == 'fever'   and ctx['symptom_b'] == 'rash'     else
            'INJURY' if ctx['symptom_a'] == 'pain'    and ctx['symptom_b'] == 'swelling' else
            'ANEMIA' if ctx['symptom_a'] == 'fatigue' and ctx['symptom_b'] == 'pallor'   else
            'UNCLEAR'
        ),
        'atoms': ['fever', 'pain', 'fatigue', 'rash', 'swelling', 'pallor',
                  'VIRAL', 'INJURY', 'ANEMIA', 'UNCLEAR'],
    },
}


# ============================================================
# ARTIFACT — the output, not a score
# ============================================================

@dataclass
class EmergenceArtifact:
    """
    What the agent learned. The real output of this environment.

    Not a number. A readable record of what changed in the agent's
    internal state from episode 1 to episode N.
    """
    scenario:           str
    n_episodes:         int
    timestamp:          float = field(default_factory=time.time)

    # What the Bandit now believes (the learned policy)
    learned_policy:     dict = field(default_factory=dict)
    # Format: {context_key: {action: Q_value}}

    # What BioRAG remembered (top salient traces)
    salient_memories:   list = field(default_factory=list)
    # Format: [{action, success, salience, retrievals, pinned}]

    # What CME locked down (hard constraints)
    constraints:        list = field(default_factory=list)

    # Decision source evolution (how pillar dominance shifted)
    source_history:     list = field(default_factory=list)
    # Format: [{episode, source}] sampled every 10 episodes

    # Accuracy curve (did it actually converge on correct answers?)
    accuracy_curve:     list = field(default_factory=list)
    # Format: [float] per episode

    # The hidden rules (revealed at the end)
    hidden_rules:       list = field(default_factory=list)

    def render(self) -> str:
        """Human-readable artifact. This is the evidence."""
        lines = [
            "=" * 60,
            f"  EMERGENCE ARTIFACT",
            f"  Scenario: {self.scenario.upper()}",
            f"  Episodes: {self.n_episodes}",
            "=" * 60,
            "",
            "── WHAT IT LEARNED (Bandit Policy) ─────────────────────",
        ]

        # Policy table
        for ctx_key, action_prefs in self.learned_policy.items():
            sorted_actions = sorted(action_prefs.items(), key=lambda x: -x[1])
            top = sorted_actions[0]
            rest = sorted_actions[1:]
            lines.append(f"  {ctx_key}")
            lines.append(f"    → prefers: {top[0]} (Q={top[1]:.3f})")
            for a, q in rest:
                lines.append(f"      also knows: {a} (Q={q:.3f})")

        lines += [
            "",
            "── WHAT IT REMEMBERED (BioRAG Hippocampus) ─────────────",
        ]

        if self.salient_memories:
            for m in self.salient_memories[:8]:
                pin = " [PINNED]" if m.get('pinned') else ""
                outcome = "✓" if m.get('success') else "✗"
                lines.append(
                    f"  {outcome} {m['action']:15s} "
                    f"salience={m['salience']:.2f} "
                    f"retrieved={m['retrievals']}x"
                    f"{pin}"
                )
        else:
            lines.append("  (no traces yet)")

        lines += [
            "",
            "── HOW ITS DECISIONS EVOLVED (Source History) ──────────",
        ]

        if self.source_history:
            # Show source every 10 episodes
            for entry in self.source_history:
                lines.append(f"  ep {entry['episode']:4d}: {entry['source']}")
        
        lines += [
            "",
            "── ACCURACY CURVE ───────────────────────────────────────",
        ]

        if self.accuracy_curve:
            # Show in chunks of 10
            chunk = 10
            for i in range(0, len(self.accuracy_curve), chunk):
                block = self.accuracy_curve[i:i+chunk]
                avg = sum(block) / len(block)
                bar = "█" * int(avg * 10) + "░" * (10 - int(avg * 10))
                lines.append(f"  ep {i:3d}-{i+len(block):3d}: [{bar}] {avg:.0%}")

        lines += [
            "",
            "── HIDDEN RULES (revealed) ──────────────────────────────",
        ]
        for rule in self.hidden_rules:
            lines.append(f"  • {rule}")

        lines.append("=" * 60)
        return "\n".join(lines)

    def to_json(self) -> str:
        return json.dumps({
            'scenario':         self.scenario,
            'n_episodes':       self.n_episodes,
            'learned_policy':   self.learned_policy,
            'salient_memories': self.salient_memories,
            'constraints':      self.constraints,
            'source_history':   self.source_history,
            'accuracy_curve':   self.accuracy_curve,
            'hidden_rules':     self.hidden_rules,
        }, indent=2)


# ============================================================
# ENVIRONMENT
# ============================================================

class ObservatoryEnv(EnvironmentBase):
    """
    The emergence observatory.

    Generates contextual decision tasks from a chosen scenario.
    Tracks what the agent learns and packages it as an artifact.

    The artifact is the output. Not a score.
    """

    def __init__(
        self,
        scenario:    str  = 'triage',
        seed:        int  = 42,
        noise:       float = 0.0,   # fraction of episodes with noisy labels
    ):
        if scenario not in SCENARIOS:
            raise ValueError(f"Unknown scenario: {scenario}. Options: {list(SCENARIOS.keys())}")

        self.scenario_name = scenario
        self.scenario = SCENARIOS[scenario]
        self.rng = random.Random(seed)
        self.noise = noise

        # Internal state
        self._context = None
        self._correct = None
        self._step = 0
        self._budget = 5.0
        self._episode_id = 0

        # Artifact tracking (persists across episodes)
        self._source_log = []
        self._accuracy_log = []
        self._episode_correct = []

        # Agent reference (set externally for artifact extraction)
        self._agent_ref = None

    @property
    def spec(self) -> EnvironmentSpec:
        sc = self.scenario
        return EnvironmentSpec(
            name         = f"observatory_{self.scenario_name}",
            display_name = f"Observatory: {sc['display']}",
            domain       = "emergence_observatory",
            description  = sc['description'],
            difficulty   = 3,
            invariants   = sc['hidden_rules'],
            tags         = ["observatory", "artifact", "evidence", self.scenario_name],
            version      = "1.0.0",
        )

    def reset(self, episode_id: int = 0) -> dict:
        self._episode_id = episode_id
        self._step = 0
        self._budget = 5.0

        # Generate a random context
        self._context = {
            k: self.rng.choice(vals)
            for k, vals in self.scenario['context_values'].items()
        }

        # The correct answer (hidden from agent)
        self._correct = self.scenario['correct_fn'](self._context)

        # Optional noise: sometimes the "correct" label is wrong
        if self.noise > 0 and self.rng.random() < self.noise:
            other = [a for a in self.scenario['actions'] if a != self._correct]
            self._correct = self.rng.choice(other)

        return self._observe()

    def step(self, action: Action) -> tuple:
        cost = 0.05   # all actions same cost — this env is about learning, not budget
        self._budget -= cost

        chosen = action.payload.get('result', action.payload.get('primitives', [''])[0])
        if isinstance(chosen, list):
            chosen = chosen[0] if chosen else ''

        correct = self._correct
        success = (chosen == correct)
        reward = 2.0 if success else -0.5

        # Track accuracy
        self._episode_correct.append(1.0 if success else 0.0)

        self._step += 1
        done = True  # one decision per episode in observatory mode

        info = {
            'correct':  correct,
            'chosen':   chosen,
            'success':  success,
            'context':  self._context,
        }

        return self._observe(), reward - cost, done, info

    def run_probes(self, episode: int) -> dict:
        return {'delta_transfer': 0.0, 'delta_style': 0.0,
                'shortcut_index': 0.0, 'cache_index': 0.0, 'flags': []}

    def extract_artifact(self, agent, n_episodes: int) -> EmergenceArtifact:
        """
        Extract the emergence artifact from the agent's internal state.
        Call this after training is complete.

        This is the whole point of this environment.
        """
        artifact = EmergenceArtifact(
            scenario    = self.scenario_name,
            n_episodes  = n_episodes,
            hidden_rules = self.scenario['hidden_rules'],
            accuracy_curve = self._episode_correct,
        )

        # ── Bandit learned policy ─────────────────────────────
        if hasattr(agent, 'bandit') and hasattr(agent.bandit, 'state'):
            for ctx_key, action_map in agent.bandit.state.posteriors.items():
                policy_entry = {}
                for act, bp in action_map.items():
                    q = bp.alpha / (bp.alpha + bp.beta)
                    policy_entry[act] = round(q, 3)
                if policy_entry:
                    artifact.learned_policy[ctx_key] = policy_entry

        # ── BioRAG salient memories ───────────────────────────
        try:
            from agents.deployable_biorag_hybrids.quint_biorag import BioRAG
            if hasattr(agent, 'rag') and isinstance(agent.rag, BioRAG):
                hippo = agent.rag.hippocampus
                # Sort by salience × retrieval_count
                sorted_traces = sorted(
                    hippo.traces,
                    key=lambda t: t.salience * (1 + t.retrieval_count),
                    reverse=True
                )
                artifact.salient_memories = [
                    {
                        'action':     t.action,
                        'success':    t.success,
                        'salience':   round(t.salience, 3),
                        'retrievals': t.retrieval_count,
                        'pinned':     t.pinned,
                    }
                    for t in sorted_traces[:10]
                ]
        except Exception:
            pass

        # ── Source history (decision attribution) ─────────────
        artifact.source_history = self._source_log

        return artifact

    def log_source(self, episode: int, source: str):
        """Called by the adapter after each decision."""
        if episode % 10 == 0:
            self._source_log.append({'episode': episode, 'source': source})

    def _observe(self) -> dict:
        ctx_display = {k: v for k, v in (self._context or {}).items()}
        return {
            'episode_id':       self._episode_id,
            'step':             self._step,
            'task': {
                'input':        json.dumps(ctx_display),
                'target':       '?',   # hidden
                'context':      ctx_display,
                'actions':      self.scenario['actions'],
            },
            'available_atoms':  self.scenario['atoms'],
            'library':          [],
            'capacity_total':   100,
            'budget_remaining': self._budget,
        }
