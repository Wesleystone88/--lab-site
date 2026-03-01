"""
noesis_bridge.py
================
Middleware connecting PhilosopherCellsSim ↔ QuintBioRAGAgent.

Architecture:
    PhilosopherCells  →  [NoesisBridge]  →  QuintBioRAGAgent
          ↑                                        |
          └────────────────────────────────────────┘

The bridge does THREE things and only three things:

  1. READS sim state → translates grid metrics into agent context dict
     The agent never sees numpy arrays. It sees domain language.

  2. TRANSLATES agent action → sim parameter nudge
     The sim never knows an agent exists. It just receives parameter changes.

  3. RECORDS every exchange as a structured card
     Full audit trail. NoesisCards-compatible format.
     Every context, action, outcome, and metric change is logged.

Design principles:
  - Zero coupling between sim and agent. Neither imports the other.
  - Bridge owns the vocabulary (context keys, action names).
  - Bridge owns the reward signal (how to measure outcome).
  - Swap sim → real data stream: bridge contract stays identical.
  - Swap agent → different model: bridge contract stays identical.

Integration path:
  PHASE 1 (now):     Philosopher Cells sim as environment
  PHASE 2 (soon):    Recorded real data replayed through same bridge
  PHASE 3 (later):   Live data stream through same bridge
  PHASE 4 (future):  Multiple agents, Pillar 7 social tuples shared via bridge

File dependencies:
  philosopher_cells_mvp.py   — sim (no import needed, passed as object)
  quint_biorag.py            — agent (no import needed, passed as object)
  domain_loader.py           — optional, for domain-aware bridge
  glyph_registry.py          — optional, for card-compatible logging

Usage:
    from philosopher_cells_mvp import PhilosopherCellsSim
    from noesis_bridge import NoesisBridge, BridgeConfig

    sim   = PhilosopherCellsSim(n=64, k=3, seed=42)
    agent = QuintBioRAGAgent(seed=42)

    bridge = NoesisBridge(sim, agent)
    report = bridge.run(steps=500)
"""

import time
import json
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from collections import deque
from enum import Enum


# ─────────────────────────────────────────────────────────────
# VOCABULARY — the bridge's language
# Names the agent sees. Sim never sees these.
# Change here to change the entire context/action space.
# ─────────────────────────────────────────────────────────────

# Context keys — what the agent reads
CTX_CONSENSUS    = "consensus"       # low / medium / high
CTX_CONFLICT     = "conflict"        # low / medium / high
CTX_THROUGHPUT   = "throughput"      # low / medium / high
CTX_MEMORY       = "memory"          # sparse / building / dense
CTX_TRUST        = "trust"           # degraded / nominal / strong
CTX_CHARISMATA   = "charismata"      # quiet / active / saturated
CTX_MOMENTUM     = "momentum"        # falling / stable / rising
CTX_DOMAIN       = "domain"          # injected by domain loader

# Actions the agent can take
ACTION_BOOST_TRUST       = "boost_trust"        # increase immune strength
ACTION_REDUCE_TRUST      = "reduce_trust"        # relax immune strength
ACTION_AMPLIFY_SIGNAL    = "amplify_signal"      # increase charismata diffusion
ACTION_DAMPEN_SIGNAL     = "dampen_signal"       # reduce charismata diffusion
ACTION_STRENGTHEN_MEMORY = "strengthen_memory"   # slow dust decay
ACTION_FLUSH_MEMORY      = "flush_memory"        # speed dust decay
ACTION_PUSH_CONSENSUS    = "push_consensus"      # nudge toward global target
ACTION_RELEASE_CONSENSUS = "release_consensus"   # allow local diversity
ACTION_HOLD              = "hold"                # no intervention

ALL_ACTIONS = [
    ACTION_BOOST_TRUST,
    ACTION_REDUCE_TRUST,
    ACTION_AMPLIFY_SIGNAL,
    ACTION_DAMPEN_SIGNAL,
    ACTION_STRENGTHEN_MEMORY,
    ACTION_FLUSH_MEMORY,
    ACTION_PUSH_CONSENSUS,
    ACTION_RELEASE_CONSENSUS,
    ACTION_HOLD,
]


# ─────────────────────────────────────────────────────────────
# BRIDGE CONFIG
# ─────────────────────────────────────────────────────────────

@dataclass
class BridgeConfig:
    """
    All tunable parameters for the bridge.

    Thresholds define the vocabulary bins.
    Nudge magnitudes define how strongly actions affect the sim.
    Reward defines what "success" means.

    Integration path note:
      When you move to real data, you'll adjust thresholds to match
      the real data's natural distribution. Everything else stays.
    """

    # ── Context binning thresholds ────────────────────────────
    # Consensus (align metric from sim)
    consensus_low:    float = 0.50
    consensus_high:   float = 0.80

    # Conflict (conflict metric from sim)
    conflict_low:     float = 0.10
    conflict_high:    float = 0.25

    # Throughput (E * C mean from sim)
    throughput_low:   float = 0.15
    throughput_high:  float = 0.35

    # Memory density (D_mean from sim)
    memory_sparse:    float = 0.10
    memory_dense:     float = 1.50

    # Trust health (T_mean from sim)
    trust_degraded:   float = 0.55
    trust_strong:     float = 0.78

    # Charismata activity (U_mean from sim)
    charismata_quiet:     float = 0.05
    charismata_saturated: float = 0.80

    # ── Action nudge magnitudes ───────────────────────────────
    # How much each action changes sim parameters
    trust_nudge:      float = 0.015   # immune_strength delta
    signal_nudge:     float = 0.020   # diff_U delta
    memory_nudge:     float = 0.00005 # decay_D delta
    consensus_nudge:  float = 0.003   # target_drift delta

    # Parameter safety bounds (prevent runaway)
    immune_min:       float = 0.02
    immune_max:       float = 0.40
    diff_U_min:       float = 0.05
    diff_U_max:       float = 0.50
    decay_D_min:      float = 0.00005
    decay_D_max:      float = 0.002

    # ── Reward definition ─────────────────────────────────────
    # What does "success" mean for the agent?
    # Default: high throughput AND low conflict AND improving trend
    reward_throughput_weight: float = 0.50
    reward_conflict_weight:   float = 0.30   # inverted — low conflict = reward
    reward_trend_weight:      float = 0.20   # improving over last N steps

    # ── Step control ──────────────────────────────────────────
    sim_steps_per_agent_step: int = 5   # agent acts every N sim steps
    trend_window:             int = 20  # steps to compute momentum trend

    # ── Logging ───────────────────────────────────────────────
    log_every_n:        int  = 10
    card_log_enabled:   bool = True
    checkpoint_every_n: int  = 100   # save agent state every N agent steps


# ─────────────────────────────────────────────────────────────
# BRIDGE CARD — NoesisCards-compatible log entry
# ─────────────────────────────────────────────────────────────

@dataclass
class BridgeCard:
    """
    One decision record. NoesisCards-compatible format.

    Integration path note:
      When you add the full NoesisCards stack, replace _emit_card()
      with a real JSONL append. The card structure is already compatible.
    """
    card_id:         str
    step:            int
    sim_step:        int
    timestamp:       float

    # What the agent saw
    context:         Dict[str, str]
    raw_metrics:     Dict[str, float]

    # What the agent decided
    action:          str
    pfc_verdict:     str    # PROCEED / SLOW / ESCALATE (when PFC wired in)
    source:          str    # bandit source

    # What happened
    success:         bool
    reward:          float
    outcome_metrics: Dict[str, float]

    # Audit fields
    domain:          str = "default"
    acted:           bool = False    # did sim reach "ship acts" threshold?
    notes:           str = ""

    def to_dict(self) -> dict:
        return {
            "card_id":        self.card_id,
            "type":           "bridge_decision",
            "step":           self.step,
            "sim_step":       self.sim_step,
            "timestamp":      self.timestamp,
            "context":        self.context,
            "raw_metrics":    self.raw_metrics,
            "action":         self.action,
            "pfc_verdict":    self.pfc_verdict,
            "source":         self.source,
            "success":        self.success,
            "reward":         round(self.reward, 4),
            "outcome_metrics": self.outcome_metrics,
            "domain":         self.domain,
            "acted":          self.acted,
            "notes":          self.notes,
        }


# ─────────────────────────────────────────────────────────────
# NOESIS BRIDGE
# ─────────────────────────────────────────────────────────────

class NoesisBridge:
    """
    Middleware connecting PhilosopherCellsSim ↔ QuintBioRAGAgent.

    Neither the sim nor the agent is imported here.
    Both are passed as objects — duck typing.
    The bridge only calls the public API of each.

    Sim API used:
        sim.step()                 → metrics dict
        sim.immune_strength        → float (read/write)
        sim.diff_U                 → float (read/write)
        sim.decay_D                → float (read/write)
        sim.target_drift           → float (read/write)

    Agent API used:
        agent.choose_action(context, actions) → (action, source)
        agent.update(context, action, success, step)
        agent.save_state(path)               → optional

    PFC API used (when wired):
        agent.choose(context, actions) → (action, pfc_signal)
        pfc_signal.verdict.value       → str

    Integration path:
        Phase 1: Pass PhilosopherCellsSim + QuintBioRAGAgent
        Phase 2: Pass DataReplaySim + QuintBioRAGAgent
        Phase 3: Pass LiveDataStream + QuintBioRAGAgent
        Phase 4: Pass LiveDataStream + [MultipleAgents]
    """

    def __init__(
        self,
        sim:    Any,
        agent:  Any,
        config: Optional[BridgeConfig] = None,
        domain_loader: Optional[Any]   = None,
    ):
        self.sim    = sim
        self.agent  = agent
        self.cfg    = config or BridgeConfig()
        self.domain_loader = domain_loader

        # Step counters
        self._bridge_step: int = 0
        self._sim_step:    int = 0
        self._card_counter: int = 0

        # Rolling metric history for trend/momentum computation
        self._throughput_history: deque = deque(
            maxlen=self.cfg.trend_window
        )
        self._reward_history: deque = deque(maxlen=200)

        # Card log
        self._cards: List[BridgeCard] = []

        # Last metrics (for momentum)
        self._last_metrics: Dict[str, float] = {}

        # Active domain tag
        self._domain: str = "default"
        if domain_loader:
            self._domain = domain_loader.get_current_domain()

        # Performance report
        self._report: Dict[str, Any] = {
            "total_bridge_steps":  0,
            "total_sim_steps":     0,
            "ship_acts":           0,
            "action_counts":       {a: 0 for a in ALL_ACTIONS},
            "pfc_escalations":     0,
            "avg_reward":          0.0,
            "peak_throughput":     0.0,
            "peak_consensus":      0.0,
            "final_metrics":       {},
        }

    # ─────────────────────────────────────────────
    # MAIN LOOP
    # ─────────────────────────────────────────────

    def run(
        self,
        steps: int,
        target: Optional[str] = None,
        checkpoint_path: Optional[str] = None,
        log_path: Optional[str] = None,
        verbose: bool = True,
    ) -> Dict[str, Any]:
        """
        Run the bridge for N agent steps.

        Each agent step:
          1. Advance sim N times (sim_steps_per_agent_step)
          2. Read sim state → build context
          3. Agent chooses action
          4. Apply action to sim
          5. Advance sim one more step → measure outcome
          6. Compute reward → update agent
          7. Log card

        Args:
            steps:           number of agent decision steps
            target:          optional target domain to load at start
            checkpoint_path: path to save agent state periodically
            log_path:        path to write JSONL card log
            verbose:         print progress

        Returns:
            Full performance report dict
        """
        if target and self.domain_loader:
            transition = self.domain_loader.activate(target, step=0)
            self._domain = self.domain_loader.get_current_domain()
            if verbose:
                print(f"[Bridge] Domain loaded: {self._domain}")

        if verbose:
            print(f"\n{'═'*64}")
            print(f"  NOESIS BRIDGE — {steps} agent steps")
            print(f"  sim_steps_per_agent_step = {self.cfg.sim_steps_per_agent_step}")
            print(f"  domain = {self._domain}")
            print(f"{'═'*64}")

        for i in range(steps):
            card = self._agent_step(i)

            # Logging
            if log_path and self.cfg.card_log_enabled:
                self._append_card_to_file(card, log_path)

            if verbose and (i % self.cfg.log_every_n == 0 or card.acted):
                self._print_step(card)

            # Checkpoint
            if (checkpoint_path and
                    i > 0 and
                    i % self.cfg.checkpoint_every_n == 0):
                if hasattr(self.agent, 'save_state'):
                    self.agent.save_state(checkpoint_path)
                    if verbose:
                        print(f"  [Bridge] Checkpoint saved at step {i}")

        # Final report
        self._finalize_report()
        if verbose:
            self._print_report()

        return self._report

    # ─────────────────────────────────────────────
    # SINGLE AGENT STEP
    # ─────────────────────────────────────────────

    def _agent_step(self, step: int) -> BridgeCard:
        """One full agent decision cycle."""
        self._bridge_step += 1
        cfg = self.cfg

        # ── 1. Advance sim (pre-action) ───────────────────────
        pre_metrics = self._advance_sim(cfg.sim_steps_per_agent_step)

        # ── 2. Read state → context ───────────────────────────
        context     = self._build_context(pre_metrics)
        raw_metrics = dict(pre_metrics)

        # ── 3. Agent chooses action ───────────────────────────
        action, source, pfc_verdict = self._agent_choose(context)

        # ── 4. Apply action to sim ────────────────────────────
        self._apply_action(action)

        # ── 5. Advance sim (post-action) — measure outcome ────
        post_metrics = self._advance_sim(1)

        # ── 6. Compute reward + success ───────────────────────
        reward, success = self._compute_reward(pre_metrics, post_metrics)

        # ── 7. Update agent ───────────────────────────────────
        self.agent.update(context, action, success, step)

        # ── 8. Update momentum history ────────────────────────
        self._throughput_history.append(post_metrics["throughput"])
        self._reward_history.append(reward)
        self._last_metrics = post_metrics

        # ── 9. Update report ──────────────────────────────────
        self._report["action_counts"][action] += 1
        if post_metrics.get("acted"):
            self._report["ship_acts"] += 1
        if pfc_verdict == "ESCALATE":
            self._report["pfc_escalations"] += 1
        self._report["peak_throughput"] = max(
            self._report["peak_throughput"],
            post_metrics["throughput"]
        )
        self._report["peak_consensus"] = max(
            self._report["peak_consensus"],
            post_metrics["align"]
        )

        # ── 10. Build and store card ──────────────────────────
        self._card_counter += 1
        card = BridgeCard(
            card_id=f"BRIDGE_{self._bridge_step:05d}",
            step=self._bridge_step,
            sim_step=self._sim_step,
            timestamp=time.time(),
            context=context,
            raw_metrics=raw_metrics,
            action=action,
            pfc_verdict=pfc_verdict,
            source=source,
            success=success,
            reward=reward,
            outcome_metrics={
                "align":      round(post_metrics["align"], 4),
                "conflict":   round(post_metrics["conflict"], 4),
                "throughput": round(post_metrics["throughput"], 4),
                "E_mean":     round(post_metrics["E_mean"], 4),
                "T_mean":     round(post_metrics["T_mean"], 4),
                "D_mean":     round(post_metrics["D_mean"], 4),
            },
            domain=self._domain,
            acted=post_metrics.get("acted", False),
        )
        if self.cfg.card_log_enabled:
            self._cards.append(card)

        return card

    # ─────────────────────────────────────────────
    # SIM INTERFACE
    # ─────────────────────────────────────────────

    def _advance_sim(self, n_steps: int) -> Dict[str, float]:
        """Advance the sim N steps. Return final metrics."""
        metrics = {}
        for _ in range(n_steps):
            metrics = self.sim.step()
            self._sim_step += 1
        return metrics

    def _build_context(self, m: Dict[str, float]) -> Dict[str, str]:
        """
        Translate raw sim metrics into agent context dict.

        This is the ONLY place sim metrics become agent language.
        Change the vocabulary here without touching agent or sim.

        Integration path note:
            When switching to real data, replace metric keys here.
            e.g. m["align"] → m["user_satisfaction_score"]
            The agent context keys stay identical.
        """
        cfg = self.cfg

        # Consensus bin
        if m["align"] >= cfg.consensus_high:
            consensus = "high"
        elif m["align"] >= cfg.consensus_low:
            consensus = "medium"
        else:
            consensus = "low"

        # Conflict bin
        if m["conflict"] <= cfg.conflict_low:
            conflict = "low"
        elif m["conflict"] <= cfg.conflict_high:
            conflict = "medium"
        else:
            conflict = "high"

        # Throughput bin
        if m["throughput"] >= cfg.throughput_high:
            throughput = "high"
        elif m["throughput"] >= cfg.throughput_low:
            throughput = "medium"
        else:
            throughput = "low"

        # Memory density bin
        if m["D_mean"] >= cfg.memory_dense:
            memory = "dense"
        elif m["D_mean"] >= cfg.memory_sparse:
            memory = "building"
        else:
            memory = "sparse"

        # Trust health bin
        if m["T_mean"] >= cfg.trust_strong:
            trust = "strong"
        elif m["T_mean"] >= cfg.trust_degraded:
            trust = "nominal"
        else:
            trust = "degraded"

        # Charismata activity bin
        if m["U_mean"] >= cfg.charismata_saturated:
            charismata = "saturated"
        elif m["U_mean"] >= cfg.charismata_quiet:
            charismata = "active"
        else:
            charismata = "quiet"

        # Momentum (throughput trend)
        momentum = self._compute_momentum()

        return {
            CTX_CONSENSUS:  consensus,
            CTX_CONFLICT:   conflict,
            CTX_THROUGHPUT: throughput,
            CTX_MEMORY:     memory,
            CTX_TRUST:      trust,
            CTX_CHARISMATA: charismata,
            CTX_MOMENTUM:   momentum,
            CTX_DOMAIN:     self._domain,
        }

    def _apply_action(self, action: str) -> None:
        """
        Translate agent action into sim parameter nudge.

        This is the ONLY place agent actions become sim changes.
        The sim never knows what triggered the parameter change.

        Integration path note:
            When switching to real data, these become API calls,
            database writes, or configuration changes.
            Action names stay identical.
        """
        cfg = self.cfg
        sim = self.sim

        if action == ACTION_BOOST_TRUST:
            sim.immune_strength = min(
                cfg.immune_max,
                sim.immune_strength + cfg.trust_nudge
            )

        elif action == ACTION_REDUCE_TRUST:
            sim.immune_strength = max(
                cfg.immune_min,
                sim.immune_strength - cfg.trust_nudge
            )

        elif action == ACTION_AMPLIFY_SIGNAL:
            sim.diff_U = min(
                cfg.diff_U_max,
                sim.diff_U + cfg.signal_nudge
            )

        elif action == ACTION_DAMPEN_SIGNAL:
            sim.diff_U = max(
                cfg.diff_U_min,
                sim.diff_U - cfg.signal_nudge
            )

        elif action == ACTION_STRENGTHEN_MEMORY:
            sim.decay_D = max(
                cfg.decay_D_min,
                sim.decay_D - cfg.memory_nudge
            )

        elif action == ACTION_FLUSH_MEMORY:
            sim.decay_D = min(
                cfg.decay_D_max,
                sim.decay_D + cfg.memory_nudge
            )

        elif action == ACTION_PUSH_CONSENSUS:
            # Slow the target drift → easier for cells to converge
            sim.target_drift = max(0.0005, sim.target_drift - cfg.consensus_nudge)

        elif action == ACTION_RELEASE_CONSENSUS:
            # Speed up target drift → allow more diversity
            sim.target_drift = min(0.02, sim.target_drift + cfg.consensus_nudge)

        elif action == ACTION_HOLD:
            pass  # intentional no-op

    # ─────────────────────────────────────────────
    # AGENT INTERFACE
    # ─────────────────────────────────────────────

    def _agent_choose(
        self,
        context: Dict[str, str],
    ) -> Tuple[str, str, str]:
        """
        Call the agent's choose method.

        Handles both:
          - Old API: choose_action(context, actions) → (action, source)
          - New API: choose(context, actions) → (action, pfc_signal)
            (when PFC is wired in from pfc_engine.py)

        Returns: (action, source, pfc_verdict)
        """
        actions = ALL_ACTIONS

        # Try new PFC-aware API first
        if hasattr(self.agent, 'choose'):
            try:
                result = self.agent.choose(context, actions)
                if isinstance(result, tuple) and len(result) == 2:
                    action, pfc_signal = result
                    # pfc_signal is PFCSignal object
                    verdict = pfc_signal.verdict.value \
                              if hasattr(pfc_signal, 'verdict') else "PROCEED"
                    source = "pfc_bandit"
                    return action, source, verdict
            except Exception:
                pass

        # Fall back to legacy API
        if hasattr(self.agent, 'choose_action'):
            action, source = self.agent.choose_action(context, actions)
            return action, source, "PROCEED"

        # Absolute fallback — shouldn't happen
        import random
        return random.choice(actions), "random", "PROCEED"

    # ─────────────────────────────────────────────
    # REWARD
    # ─────────────────────────────────────────────

    def _compute_reward(
        self,
        pre:  Dict[str, float],
        post: Dict[str, float],
    ) -> Tuple[float, bool]:
        """
        Compute reward from pre → post metric delta.

        Reward = weighted combination of:
          - Throughput level (absolute)
          - Conflict reduction (inverted)
          - Improving trend (momentum)

        Success = reward above 0.5 threshold.

        Integration path note:
            Real data version: replace with domain-specific KPI.
            Medical: patient outcome improvement.
            Legal:   case resolution quality.
            Financial: risk-adjusted return.
        """
        cfg = self.cfg

        # Throughput component (higher is better)
        thr_score = post["throughput"] / max(0.01, self.cfg.throughput_high)
        thr_score = min(1.0, thr_score)

        # Conflict component (lower is better — invert)
        conflict_score = 1.0 - (post["conflict"] / max(0.01, self.cfg.conflict_high))
        conflict_score = max(0.0, min(1.0, conflict_score))

        # Trend component — did throughput improve?
        delta = post["throughput"] - pre["throughput"]
        trend_score = 0.5 + (delta / 0.05)   # center at 0, scale
        trend_score = max(0.0, min(1.0, trend_score))

        reward = (
            cfg.reward_throughput_weight * thr_score +
            cfg.reward_conflict_weight   * conflict_score +
            cfg.reward_trend_weight      * trend_score
        )
        reward = max(0.0, min(1.0, reward))

        # Success threshold
        success = reward >= 0.50

        return reward, success

    def _compute_momentum(self) -> str:
        """Compute throughput trend from rolling history."""
        if len(self._throughput_history) < 5:
            return "stable"
        recent = list(self._throughput_history)
        first_half  = sum(recent[:len(recent)//2]) / (len(recent)//2)
        second_half = sum(recent[len(recent)//2:]) / (len(recent) - len(recent)//2)
        delta = second_half - first_half
        if delta > 0.02:
            return "rising"
        elif delta < -0.02:
            return "falling"
        return "stable"

    # ─────────────────────────────────────────────
    # LOGGING
    # ─────────────────────────────────────────────

    def _append_card_to_file(self, card: BridgeCard, path: str) -> None:
        """Append card as JSONL — NoesisCards compatible."""
        with open(path, "a") as f:
            f.write(json.dumps(card.to_dict()) + "\n")

    def _print_step(self, card: BridgeCard) -> None:
        act_marker = " ★ ACTED" if card.acted else ""
        pfc_marker = f" [{card.pfc_verdict}]" if card.pfc_verdict != "PROCEED" else ""
        print(
            f"  step={card.step:4d}  "
            f"ctx=[{card.context.get(CTX_CONSENSUS,'?')[:3]}|"
            f"{card.context.get(CTX_CONFLICT,'?')[:3]}|"
            f"{card.context.get(CTX_THROUGHPUT,'?')[:3]}]  "
            f"action={card.action:<22}  "
            f"reward={card.reward:.3f}  "
            f"thr={card.outcome_metrics.get('throughput',0):.3f}"
            f"{pfc_marker}{act_marker}"
        )

    def _finalize_report(self) -> None:
        """Populate final report fields."""
        rewards = list(self._reward_history)
        self._report["total_bridge_steps"] = self._bridge_step
        self._report["total_sim_steps"]    = self._sim_step
        self._report["avg_reward"] = sum(rewards) / max(1, len(rewards))
        self._report["final_metrics"] = self._last_metrics
        self._report["cards_logged"] = len(self._cards)
        self._report["domain"] = self._domain

    def _print_report(self) -> None:
        r = self._report
        print(f"\n{'═'*64}")
        print(f"  BRIDGE REPORT")
        print(f"{'─'*64}")
        print(f"  agent steps:      {r['total_bridge_steps']}")
        print(f"  sim steps:        {r['total_sim_steps']}")
        print(f"  ship acts:        {r['ship_acts']}")
        print(f"  pfc escalations:  {r['pfc_escalations']}")
        print(f"  avg reward:       {r['avg_reward']:.4f}")
        print(f"  peak throughput:  {r['peak_throughput']:.4f}")
        print(f"  peak consensus:   {r['peak_consensus']:.4f}")
        print(f"  cards logged:     {r['cards_logged']}")
        print(f"{'─'*64}")
        print(f"  action distribution:")
        sorted_acts = sorted(
            r["action_counts"].items(),
            key=lambda x: -x[1]
        )
        for act, count in sorted_acts:
            bar = "█" * min(30, count)
            print(f"    {act:<26} {count:4d}  {bar}")
        print(f"{'═'*64}\n")

    # ─────────────────────────────────────────────
    # INTROSPECTION
    # ─────────────────────────────────────────────

    def get_cards(self) -> List[BridgeCard]:
        """All logged decision cards."""
        return list(self._cards)

    def get_card_dicts(self) -> List[dict]:
        """Cards as plain dicts — for NoesisCards ingestion."""
        return [c.to_dict() for c in self._cards]

    def get_action_distribution(self) -> Dict[str, float]:
        """Normalized action frequencies."""
        total = max(1, sum(self._report["action_counts"].values()))
        return {
            a: round(c / total, 3)
            for a, c in self._report["action_counts"].items()
        }

    def get_context_vocabulary(self) -> Dict[str, List[str]]:
        """What context keys and values the agent can see."""
        return {
            CTX_CONSENSUS:  ["low", "medium", "high"],
            CTX_CONFLICT:   ["low", "medium", "high"],
            CTX_THROUGHPUT: ["low", "medium", "high"],
            CTX_MEMORY:     ["sparse", "building", "dense"],
            CTX_TRUST:      ["degraded", "nominal", "strong"],
            CTX_CHARISMATA: ["quiet", "active", "saturated"],
            CTX_MOMENTUM:   ["falling", "stable", "rising"],
            CTX_DOMAIN:     ["any string — injected by domain loader"],
        }

    def get_action_effects(self) -> Dict[str, str]:
        """Human-readable action → sim effect mapping."""
        return {
            ACTION_BOOST_TRUST:       f"immune_strength += {self.cfg.trust_nudge}",
            ACTION_REDUCE_TRUST:      f"immune_strength -= {self.cfg.trust_nudge}",
            ACTION_AMPLIFY_SIGNAL:    f"diff_U += {self.cfg.signal_nudge}",
            ACTION_DAMPEN_SIGNAL:     f"diff_U -= {self.cfg.signal_nudge}",
            ACTION_STRENGTHEN_MEMORY: f"decay_D -= {self.cfg.memory_nudge}",
            ACTION_FLUSH_MEMORY:      f"decay_D += {self.cfg.memory_nudge}",
            ACTION_PUSH_CONSENSUS:    f"target_drift -= {self.cfg.consensus_nudge}",
            ACTION_RELEASE_CONSENSUS: f"target_drift += {self.cfg.consensus_nudge}",
            ACTION_HOLD:              "no change",
        }


# ─────────────────────────────────────────────────────────────
# INTEGRATION PATH NOTES — read before moving to next phase
# ─────────────────────────────────────────────────────────────

INTEGRATION_NOTES = """
═══════════════════════════════════════════════════════════════
INTEGRATION PATH
═══════════════════════════════════════════════════════════════

PHASE 1 — Philosopher Cells (NOW)
─────────────────────────────────
    from philosopher_cells_mvp import PhilosopherCellsSim
    from quint_biorag import QuintBioRAGAgent
    from noesis_bridge import NoesisBridge

    sim   = PhilosopherCellsSim(n=64, k=3, seed=42)
    agent = QuintBioRAGAgent(seed=42)
    bridge = NoesisBridge(sim, agent)
    report = bridge.run(steps=500, target="default", verbose=True)

    What to look for:
    - Agent stops choosing HOLD after ~50 steps (learning)
    - Action distribution shifts toward domain-appropriate actions
    - Ship acts frequency increases as agent learns to boost throughput
    - PFC escalation rate drops as contexts become familiar
    - peek at bridge.get_cards() for full decision trail

PHASE 2 — Recorded Real Data Replay
─────────────────────────────────────
    Build a DataReplaySim class with the same API as PhilosopherCellsSim:
        .step() → metrics dict
        .immune_strength (float, read/write)
        .diff_U (float, read/write)
        etc.

    Feed it rows from a real dataset (medical records, legal cases, etc.)
    Map domain KPIs to the same metric keys:
        align      → user_satisfaction / consensus_score
        conflict   → disagreement_rate / escalation_rate
        throughput → outcome_quality / resolution_rate

    Bridge code: ZERO changes needed.

PHASE 3 — Live Data Stream
───────────────────────────
    Replace DataReplaySim with a LiveStreamAdapter:
        .step() pulls from a queue / API / websocket
        parameter writes become API calls / config pushes

    Bridge code: ZERO changes needed.

PHASE 4 — Multi-Agent + Pillar 7
──────────────────────────────────
    Run N bridges simultaneously, one per agent.
    After each agent step, collect social tuples:
        tuple = (domain, context_key, action, success, source="peer")

    Feed tuples to SocialPriorEngine (Pillar 7) for each other agent.
    Bridge becomes the social signal router.

    Changes needed:
        bridge.run() returns social_tuples list
        MultiAgentOrchestrator collects and routes them

NOESIS CARDS INTEGRATION
─────────────────────────
    Replace _append_card_to_file() with:
        noesis_cards.append({
            "card_id":   card.card_id,
            "type":      "bridge_decision",
            "data":      card.to_dict(),
            "timestamp": card.timestamp,
        })

    Every domain transition from domain_loader also gets a card.
    Every metacog trust adjustment gets an evidence card.
    Full provenance: every decision has a card. Every card has a hash.

WITCH BRIDGE CORTEX PANEL
──────────────────────────
    Feed bridge.get_report() to Neural Telemetry:
        ship_acts         → "ACTED" events count
        pfc_escalations   → escalation rate metric
        avg_reward        → system health score
        action_distribution → which levers the agent prefers
        peak_throughput   → luminous membrane proxy

    This is your live dashboard of the agent steering the sim.
═══════════════════════════════════════════════════════════════
"""


# ─────────────────────────────────────────────────────────────
# QUICK RUN — headless smoke test without real agent/sim
# ─────────────────────────────────────────────────────────────

class _MockSim:
    """Minimal sim for smoke testing the bridge without dependencies."""
    def __init__(self):
        self.immune_strength = 0.12
        self.diff_U          = 0.20
        self.decay_D         = 0.0002
        self.target_drift    = 0.004
        self._t = 0
        import random
        self._rng = random.Random(42)

    def step(self):
        self._t += 1
        r = self._rng
        align      = min(1.0, 0.3 + self._t * 0.0003 + r.gauss(0, 0.05))
        conflict   = max(0.0, 0.4 - self._t * 0.0002 + r.gauss(0, 0.03))
        throughput = min(1.0, 0.2 + self._t * 0.0002 + r.gauss(0, 0.04))
        return {
            "t":          self._t,
            "align":      align,
            "conflict":   conflict,
            "throughput": throughput,
            "E_mean":     0.55 + r.gauss(0, 0.03),
            "C_mean":     0.40 + r.gauss(0, 0.04),
            "T_mean":     0.75 + r.gauss(0, 0.02),
            "U_mean":     0.15 + r.gauss(0, 0.05),
            "D_mean":     0.05 + self._t * 0.00005,
            "acted":      align > 0.92 and conflict < 0.12 and throughput > 0.20,
        }


class _MockAgent:
    """Minimal agent for smoke testing without QuintBioRAG."""
    def __init__(self):
        import random
        self._rng = random.Random(99)
        self._counts: Dict[str, int] = {}

    def choose_action(self, context, actions):
        # Dumb heuristic: if conflict high → boost trust; else hold
        if context.get(CTX_CONFLICT) == "high":
            return ACTION_BOOST_TRUST, "heuristic"
        if context.get(CTX_THROUGHPUT) == "low":
            return ACTION_PUSH_CONSENSUS, "heuristic"
        return ACTION_HOLD, "heuristic"

    def update(self, context, action, success, step):
        self._counts[action] = self._counts.get(action, 0) + 1


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=100)
    ap.add_argument("--mock", action="store_true",
                    help="run with mock sim+agent (no dependencies)")
    ap.add_argument("--log", type=str, default=None,
                    help="path to write JSONL card log")
    args = ap.parse_args()

    print(INTEGRATION_NOTES)

    if args.mock:
        sim   = _MockSim()
        agent = _MockAgent()
        cfg   = BridgeConfig(log_every_n=10, sim_steps_per_agent_step=3)
        bridge = NoesisBridge(sim, agent, config=cfg)
        report = bridge.run(steps=args.steps, log_path=args.log, verbose=True)
        print(f"\nAction distribution: {bridge.get_action_distribution()}")
