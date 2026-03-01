import math
import random
from typing import Dict, List, Tuple, Optional
from collections import deque
from dataclasses import dataclass

from tri_hybrid_v3 import TriHybridAgentV3
from Bandit_engine.state import BetaParams
from Time_engine.state import KeyStateClass


@dataclass
class QuadSignal:
    error_magnitude: float
    error_sign: int
    encoding_weight: float
    exploration_boost: float
    tfe_reset: bool
    predicted_prob: float
    prediction_confidence: float


class QuadPEE:
    """
    Optimized Prediction Error Engine.
    Reads expectations directly from the Bandit's Beta distribution,
    eliminating redundant outcome tracking and history tables.
    """
    def __init__(self,
                 min_weight: float = 1.0,
                 max_weight: float = 3.0,
                 max_explore_boost: float = 0.0,
                 surprise_threshold: float = 0.15,
                 confidence_weight: float = 0.7):
        self.min_weight = min_weight
        self.max_weight = max_weight
        self.max_explore_boost = max_explore_boost
        self.surprise_threshold = surprise_threshold
        self.confidence_weight = confidence_weight
        self._calibration = deque(maxlen=100)

    def predict_from_beta(self, alpha: float, beta: float, total_prior: float = 2.0) -> Tuple[float, float]:
        """
        Derive prediction and confidence directly from Bandit priors.
        """
        prob = alpha / (alpha + beta)
        attempts = (alpha + beta) - total_prior
        if attempts <= 0:
            return prob, 0.0
        # Confidence scales logarithmically with attempts, plateauing around 50
        conf = min(1.0, math.log(1 + attempts) / math.log(1 + 50))
        return prob, conf

    def compute(self, prob: float, conf: float, success: bool) -> QuadSignal:
        actual = 1.0 if success else 0.0
        raw_error = actual - prob

        if abs(raw_error) < self.surprise_threshold:
            sign = 0
        elif raw_error > 0:
            sign = 1
        else:
            sign = -1

        mag = min(1.0, abs(raw_error))
        
        # High confidence predictions scale surprise up. Low confidence scales it down.
        weighted_mag = mag * (self.confidence_weight * conf + (1.0 - self.confidence_weight))

        if sign == 0:
            weight = self.min_weight
        else:
            weight = self.min_weight + (self.max_weight - self.min_weight) * weighted_mag

        # Only boost exploration on negative surprise
        explore_boost = self.max_explore_boost * weighted_mag if sign == -1 else 0.0
        
        # Extreme surprise triggers TFE environment-shift reset
        tfe_reset = weighted_mag > 0.5

        accuracy = 1.0 - mag
        self._calibration.append(accuracy)

        return QuadSignal(
            error_magnitude=round(weighted_mag, 4),
            error_sign=sign,
            encoding_weight=round(weight, 4),
            exploration_boost=round(explore_boost, 4),
            tfe_reset=tfe_reset,
            predicted_prob=prob,
            prediction_confidence=conf
        )

    def get_calibration(self) -> float:
        if not self._calibration:
            return 0.5
        return sum(self._calibration) / len(self._calibration)


class QuadHybridAgent(TriHybridAgentV3):
    """
    Quad-Hybrid Architecture: CME (Memory) + Bandit (Logic) + TFE (Time/Physics) + PEE (Dopamine/Surprise)
    """

    def __init__(self, seed: int = 42, tfe_tau: float = 3600.0, pee_kwargs: dict = None, sham_pe: bool = False):
        super().__init__(seed=seed, tfe_tau=tfe_tau)
        pee_kwargs = pee_kwargs or {}
        self.pee = QuadPEE(**pee_kwargs)
        self.sham_pe = sham_pe
        self._sham_rng = random.Random(seed + 77777)
        self._pending_predictions = {}
        
        # Diagnostics
        self.surprise_count = 0
        self.total_encoding_weight = 0.0
        self.update_count = 0

    def choose_action(self, condition: Dict[str, str], actions: List[str]) -> Tuple[str, str]:
        ctx_key = self._context_key(condition)

        # 1. Open TFE keys
        for act in actions:
            self.tfe.open_key(f"{ctx_key}|{act}")

        # 2. PE1: Record predictions BEFORE action
        posteriors = self.bandit.state.posteriors.get(ctx_key, {})
        for act in actions:
            if act in posteriors:
                params = posteriors[act]
                prob, conf = self.pee.predict_from_beta(
                    params.alpha, params.beta,
                    total_prior=(self.bandit.config.prior_alpha + self.bandit.config.prior_beta)
                )
            else:
                prob, conf = 0.5, 0.0
            self._pending_predictions[f"{ctx_key}|{act}"] = (prob, conf)

        # 3. Compile Guidance (CME + TFE)
        bias = self.cme.emit_bias(condition, actions)
        obs = self.last_tfe_observables

        tfe_decays = {}
        for act in actions:
            tfe_key = f"{ctx_key}|{act}"
            decay_factor = 1.0

            if obs and tfe_key in obs.key_states:
                state_cls = obs.key_states[tfe_key]
                if state_cls == KeyStateClass.ORPHANED:
                    decay_factor *= 0.1
                    bias.weights[act] = 0.1
                elif state_cls == KeyStateClass.ABANDONED:
                    decay_factor *= 0.5
                    bias.weights[act] = 0.5
                elif state_cls == KeyStateClass.PENDING:
                    decay_factor *= 0.8

            if tfe_key in self.tfe.state.duration_anomalies:
                anoms = self.tfe.state.duration_anomalies[tfe_key]
                if anoms.timeouts_fallback > 0:
                    bias.weights[act] = 0.05

            tfe_decays[act] = decay_factor

        # 4. Bandit selects action
        action, source, _ = self.bandit.get_action(
            ctx_key, actions, bias.hard_blocks, bias.weights, tfe_decays
        )
        return action, source

    def update(self, condition: Dict[str, str], action: str, success: bool, step: int):
        ctx_key = self._context_key(condition)
        tfe_key = f"{ctx_key}|{action}"

        # 1. Retrieve prior prediction
        prob, conf = self._pending_predictions.pop(tfe_key, (0.5, 0.0))

        # 2. Compute Surprise
        signal = self.pee.compute(prob, conf, success)

        if self.sham_pe:
            # Random noise pretending to be dopamine
            signal.encoding_weight = self._sham_rng.uniform(1.0, 3.0)
            signal.tfe_reset = self._sham_rng.random() < 0.15

        # Record Diagnostics
        self.update_count += 1
        self.total_encoding_weight += signal.encoding_weight
        if signal.error_sign != 0:
            self.surprise_count += 1

        # 3. Bandit Update (Scaled by encoding weight)
        if ctx_key not in self.bandit.state.posteriors:
            self.bandit.state.posteriors[ctx_key] = {}
        if action not in self.bandit.state.posteriors[ctx_key]:
            self.bandit.state.posteriors[ctx_key][action] = BetaParams(
                self.bandit.config.prior_alpha, self.bandit.config.prior_beta
            )

        current = self.bandit.state.posteriors[ctx_key][action]
        
        # Here we scale BOTH positive and negative surprise. 
        # A surprising success cements the behavior massively.
        if success:
            updated = BetaParams(current.alpha + signal.encoding_weight, current.beta)
        else:
            updated = BetaParams(current.alpha, current.beta + signal.encoding_weight)

        self.bandit.state.posteriors[ctx_key][action] = updated
        self.bandit.state.total_updates += 1
        self.bandit.state.total_steps += 1

        # 4. CME Update
        if not success:
            original_gain = self.cme.reinforce_gain
            self.cme.reinforce_gain = original_gain * signal.encoding_weight
            self.cme.reinforce_memory(
                mem_type="CONSTRAINT", 
                condition_subset=condition, 
                action=action, 
                step=step
            )
            self.cme.reinforce_gain = original_gain

        self.cme.counter_evidence(condition=condition, action=action, success=success, step=step)

        # 5. TFE Touch (and optional Surprise Reset)
        if signal.tfe_reset:
            # Deep surprise indicates paradigm shift. Shock the TFE awake.
            self.tfe.touch_key(tfe_key, magnitude=1.0)
        else:
            self.tfe.touch_key(tfe_key, magnitude=1.0 if success else 0.1)

    def get_pe_stats(self):
        avg_w = self.total_encoding_weight / max(1, self.update_count)
        return {
            "surprise_events": self.surprise_count,
            "avg_encoding_weight": round(avg_w, 3),
            "calibration": round(self.pee.get_calibration(), 3),
        }
