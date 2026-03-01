"""
Metrics — emergence signals, not test scores.

BCG  : Behavioral Compression Gain
       How much shorter are traces when the library is used?

ReuseRate : fraction of steps that invoke a library primitive

TimeToStability : episodes until per-episode reward stops changing

CounterfactualAvoidance : does the agent avoid previously-failed actions?
"""

import math
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class EpisodeRecord:
    episode_id: int
    total_reward: float
    trace: list[dict]          # list of {tier, payload, reward}
    library_snapshot: list     # LibraryEntry list at episode end
    library_used_ids: set = field(default_factory=set)


class MetricsTracker:
    def __init__(self):
        self.records: list[EpisodeRecord] = []
        self._failed_actions: list[dict] = []   # for counterfactual avoidance

    def record(self, rec: EpisodeRecord):
        self.records.append(rec)
        for step in rec.trace:
            if step["reward"] < 0:
                self._failed_actions.append(step["payload"])

    # ------------------------------------------------------------------
    # Reuse Rate
    # ------------------------------------------------------------------

    def reuse_rate(self, last_n: int = None) -> float:
        """Fraction of assembly steps that used a library primitive."""
        records = self.records[-last_n:] if last_n else self.records
        total_steps = 0
        reuse_steps = 0
        for rec in records:
            for step in rec.trace:
                total_steps += 1
                if step.get("used_library_primitive", False):
                    reuse_steps += 1
        return reuse_steps / total_steps if total_steps else 0.0

    # ------------------------------------------------------------------
    # Behavioral Compression Gain (BCG)
    # ------------------------------------------------------------------

    def bcg(self, last_n: int = None) -> float:
        """
        BCG = DL(trace | no library) - DL(trace | library)

        Approximation: description length = -log2 P(symbol)
        where P is empirical frequency over the trace vocabulary.
        """
        records = self.records[-last_n:] if last_n else self.records
        if not records:
            return 0.0

        all_base_actions = []
        all_library_actions = []

        for rec in records:
            for step in rec.trace:
                # Without library: encode as raw atoms
                raw = str(step.get("payload", ""))
                all_base_actions.append(raw)
                # With library: encode as primitive ID if used
                if step.get("used_library_primitive"):
                    all_library_actions.append(step.get("primitive_id", raw))
                else:
                    all_library_actions.append(raw)

        dl_base = self._description_length(all_base_actions)
        dl_lib  = self._description_length(all_library_actions)
        return max(0.0, dl_base - dl_lib)

    def _description_length(self, symbols: list[str]) -> float:
        if not symbols:
            return 0.0
        freq = defaultdict(int)
        for s in symbols:
            freq[s] += 1
        n = len(symbols)
        total_bits = 0.0
        for count in freq.values():
            p = count / n
            total_bits += count * (-math.log2(p))
        return total_bits

    # ------------------------------------------------------------------
    # Time to Stability
    # ------------------------------------------------------------------

    def time_to_stability(self, window: int = 10, threshold: float = 0.05) -> int:
        """
        Returns episode index where rolling reward variance drops below threshold.
        -1 if not yet stable.
        """
        rewards = [r.total_reward for r in self.records]
        if len(rewards) < window * 2:
            return -1
        for i in range(window, len(rewards)):
            window_rewards = rewards[i-window:i]
            variance = self._variance(window_rewards)
            if variance < threshold:
                return i
        return -1

    def _variance(self, vals: list[float]) -> float:
        if not vals:
            return 0.0
        mean = sum(vals) / len(vals)
        return sum((v - mean)**2 for v in vals) / len(vals)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self) -> dict:
        return {
            "episodes": len(self.records),
            "mean_reward": sum(r.total_reward for r in self.records) / max(1, len(self.records)),
            "reuse_rate": self.reuse_rate(last_n=20),
            "bcg": self.bcg(last_n=20),
            "time_to_stability": self.time_to_stability(),
        }
