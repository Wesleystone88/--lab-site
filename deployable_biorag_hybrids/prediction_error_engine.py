"""
PREDICTION ERROR ENGINE (PEE)
==============================
Blueprint v0.1 — First Principles Implementation

BIOLOGICAL BASIS:
  The brain does not record what happened. It records the DELTA between
  what it expected and what actually happened. This is the dopaminergic
  prediction error signal — the mechanism behind why surprising events
  encode stronger memories than expected ones.

  Dopamine neurons fire:
    - MORE than baseline  → positive surprise (better than expected)
    - LESS than baseline  → negative surprise (worse than expected)
    - AT baseline         → expected outcome (weak or no encoding)

AXIOMS:
  PE1 (Precedence):    Expectation must be generated BEFORE outcome arrives.
  PE2 (Signed Error):  Positive surprise ≠ Negative surprise. Different signals,
                       different downstream effects.
  PE3 (Magnitude):     Error magnitude scales encoding strength.
                       High surprise → stronger trace in CME.
  PE4 (Confidence):    Surprise from a high-confidence prediction encodes
                       stronger than the same outcome from a low-confidence
                       prediction. Being wrong when certain matters more.
  PE5 (Calibration):   The system tracks how well it predicts over time.
                       Metacognitive — it knows how well it knows.
  PE6 (Determinism):   Same prediction + same outcome + same state →
                       same error signal. Fully testable.

SYSTEM BOUNDARIES:
  PEE IS:
    - A prediction generator (before outcome)
    - A surprise calculator (after outcome)
    - An encoding weight emitter (to CME)
    - An exploration boost emitter (to Bandit)
    - A calibration tracker (metacognition)

  PEE IS NOT:
    - A memory store (that's CME)
    - An action selector (that's Bandit)
    - A time tracker (that's TFE)
    - A rule inducer (that's CME)

POSITION IN UPDATE LOOP:
  1. predict()     — called BEFORE action, generates expectation
  2. [action taken, outcome observed]
  3. compute()     — called AFTER outcome, returns PESignal
  4. PESignal.encoding_weight → passed to CME.reinforce_memory()
  5. PESignal.exploration_boost → passed to Bandit prior adjustment
  6. PESignal.tfe_reset → optionally resets TFE staleness on surprise
"""

import math
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple
from collections import deque


# ============================================================
# STATE
# ============================================================

@dataclass
class ActionExpectation:
    """
    The prediction made BEFORE an outcome is observed.
    Frozen at prediction time — never modified after.
    """
    context_key: str
    action: str
    predicted_success_prob: float   # 0..1, estimated P(success)
    prediction_confidence: float    # 0..1, how sure we are of the estimate
    step: int


@dataclass
class PESignal:
    """
    The observable output of the Prediction Error Engine.
    Emitted AFTER outcome is observed.

    Downstream consumers:
      - CME:    multiply reinforce_gain by encoding_weight
      - Bandit: temporarily boost explore_rate by exploration_boost
      - TFE:    if tfe_reset=True, touch the key to reduce staleness
    """
    # Core signal
    error_magnitude: float          # 0..1, how surprised were we
    error_sign: int                 # +1 = positive surprise, -1 = negative surprise, 0 = expected

    # Downstream modifiers
    encoding_weight: float          # CME multiplier — how strongly to encode this
    exploration_boost: float        # Bandit additive boost to explore_rate
    tfe_reset: bool                 # TFE should treat this context as freshly relevant

    # Diagnostics
    predicted_prob: float           # What we expected
    actual_outcome: bool            # What happened
    prediction_confidence: float    # How confident we were in the prediction
    calibration_score: float        # Rolling accuracy of predictions (0..1, higher=better)
    step: int


@dataclass
class ContextActionStats:
    """
    Per context-action pair statistics.
    Tracks outcome history to form predictions.
    """
    # Outcome history (rolling window)
    successes: int = 0
    attempts: int = 0

    # Prediction history for calibration
    prediction_errors: deque = field(default_factory=lambda: deque(maxlen=50))

    # Surprise history — recent high-error events
    recent_surprises: deque = field(default_factory=lambda: deque(maxlen=20))

    def success_rate(self) -> float:
        """Empirical success rate — the raw prediction."""
        if self.attempts == 0:
            return 0.5  # Prior: assume 50/50 when no data
        return self.successes / self.attempts

    def prediction_confidence(self, min_attempts: int = 5) -> float:
        """
        Confidence in our success_rate estimate.
        Grows logarithmically with attempts.
        Low data = low confidence = surprise matters less.
        """
        if self.attempts == 0:
            return 0.0
        # Log curve: confidence plateaus after ~50 attempts
        return min(1.0, math.log(1 + self.attempts) / math.log(1 + min_attempts * 10))


# ============================================================
# PREDICTION ERROR ENGINE
# ============================================================

class PredictionErrorEngine:
    """
    Computes prediction error signals for context-action outcomes.

    Usage:
        pee = PredictionErrorEngine()

        # Before action:
        expectation = pee.predict(condition, action, step)

        # After outcome:
        signal = pee.compute(expectation, success, step)

        # Use signal:
        cme.reinforce_memory(..., encoding_weight=signal.encoding_weight)
        bandit.explore_boost(signal.exploration_boost)
    """

    def __init__(
        self,
        # Encoding weight range — how much surprise scales CME encoding
        min_encoding_weight: float = 0.2,   # Expected outcome → weak encoding
        max_encoding_weight: float = 3.0,   # Max surprise → strong encoding

        # Exploration boost — how much surprise opens up exploration
        max_explore_boost: float = 0.15,    # Max additive boost to explore_rate

        # Surprise threshold — below this, outcome is "expected"
        surprise_threshold: float = 0.15,   # Delta < this = no surprise signal

        # Calibration window
        calibration_window: int = 100,

        # Confidence confidence weight on error magnitude
        # High confidence surprise matters more than low confidence surprise
        confidence_weight: float = 0.7,
    ):
        self.min_encoding_weight = min_encoding_weight
        self.max_encoding_weight = max_encoding_weight
        self.max_explore_boost = max_explore_boost
        self.surprise_threshold = surprise_threshold
        self.confidence_weight = confidence_weight

        # Per context-action pair stats
        # key: f"{context_key}|{action}"
        self.stats: Dict[str, ContextActionStats] = {}

        # Global calibration tracking
        self._calibration_window = deque(maxlen=calibration_window)

        # Pending predictions (context_key|action -> expectation)
        # Ensures prediction was made BEFORE outcome (PE1)
        self._pending: Dict[str, ActionExpectation] = {}

    def _stat_key(self, context_key: str, action: str) -> str:
        return f"{context_key}|{action}"

    def _get_stats(self, context_key: str, action: str) -> ContextActionStats:
        k = self._stat_key(context_key, action)
        if k not in self.stats:
            self.stats[k] = ContextActionStats()
        return self.stats[k]

    def _context_key(self, condition: Dict[str, str]) -> str:
        return "|".join(f"{k}={v}" for k, v in sorted(condition.items()))

    # ----------------------------------------------------------
    # PREDICT (called BEFORE outcome — PE1)
    # ----------------------------------------------------------

    def predict(
        self,
        condition: Dict[str, str],
        action: str,
        step: int,
    ) -> ActionExpectation:
        """
        Generate prediction for this context-action pair.
        Must be called BEFORE the action is taken and outcome observed.

        Returns ActionExpectation which is passed to compute() after outcome.
        """
        ctx_key = self._context_key(condition)
        stats = self._get_stats(ctx_key, action)

        prob = stats.success_rate()
        conf = stats.prediction_confidence()

        expectation = ActionExpectation(
            context_key=ctx_key,
            action=action,
            predicted_success_prob=prob,
            prediction_confidence=conf,
            step=step,
        )

        # Store pending (PE1 enforcement)
        pk = self._stat_key(ctx_key, action)
        self._pending[pk] = expectation

        return expectation

    # ----------------------------------------------------------
    # COMPUTE (called AFTER outcome — PE2, PE3, PE4)
    # ----------------------------------------------------------

    def compute(
        self,
        expectation: ActionExpectation,
        success: bool,
        step: int,
    ) -> PESignal:
        """
        Compute prediction error after outcome is observed.

        PE2: Sign — was this better or worse than expected?
        PE3: Magnitude — how surprised are we?
        PE4: Confidence weighting — being wrong when certain matters more.
        """
        ctx_key = expectation.context_key
        action = expectation.action
        stats = self._get_stats(ctx_key, action)

        # --- Update outcome history ---
        stats.attempts += 1
        if success:
            stats.successes += 1

        # --- Compute raw error ---
        # actual = 1.0 if success else 0.0
        # error = actual - predicted (signed)
        actual = 1.0 if success else 0.0
        raw_error = actual - expectation.predicted_success_prob

        # --- PE2: Sign ---
        if abs(raw_error) < self.surprise_threshold:
            error_sign = 0       # Expected — no significant surprise
        elif raw_error > 0:
            error_sign = 1       # Positive surprise (did better than expected)
        else:
            error_sign = -1      # Negative surprise (did worse than expected)

        # --- PE3: Magnitude (0..1) ---
        error_magnitude = min(1.0, abs(raw_error))

        # --- PE4: Confidence weighting ---
        # High confidence + high error = more significant surprise
        # Low confidence + high error = less significant (we didn't expect to know)
        conf = expectation.prediction_confidence
        weighted_magnitude = error_magnitude * (
            self.confidence_weight * conf + (1.0 - self.confidence_weight)
        )

        # --- Encoding weight for CME (PE3) ---
        # Expected outcome → min_encoding_weight (still encode, just weakly)
        # Max surprise → max_encoding_weight
        if error_sign == 0:
            encoding_weight = self.min_encoding_weight
        else:
            encoding_weight = self.min_encoding_weight + (
                self.max_encoding_weight - self.min_encoding_weight
            ) * weighted_magnitude

        # --- Exploration boost for Bandit ---
        # Negative surprise only — positive surprise means we found something good,
        # no need to explore. Negative surprise means our model is wrong, explore more.
        if error_sign == -1:
            exploration_boost = self.max_explore_boost * weighted_magnitude
        else:
            exploration_boost = 0.0

        # --- TFE reset signal ---
        # High surprise means the environment has changed — TFE staleness on this
        # context should be reset (it's freshly relevant again, for better or worse)
        tfe_reset = weighted_magnitude > 0.5

        # --- PE5: Update calibration ---
        # Calibration = how accurately we predicted (1.0 = perfect, 0.0 = always wrong)
        prediction_accuracy = 1.0 - error_magnitude
        self._calibration_window.append(prediction_accuracy)
        stats.prediction_errors.append(error_magnitude)

        # Rolling calibration score
        calibration_score = (
            sum(self._calibration_window) / len(self._calibration_window)
            if self._calibration_window else 0.5
        )

        # Log surprise for this context-action pair
        stats.recent_surprises.append(weighted_magnitude)

        # Clean up pending
        pk = self._stat_key(ctx_key, action)
        self._pending.pop(pk, None)

        return PESignal(
            error_magnitude=round(weighted_magnitude, 4),
            error_sign=error_sign,
            encoding_weight=round(encoding_weight, 4),
            exploration_boost=round(exploration_boost, 4),
            tfe_reset=tfe_reset,
            predicted_prob=expectation.predicted_success_prob,
            actual_outcome=success,
            prediction_confidence=conf,
            calibration_score=round(calibration_score, 4),
            step=step,
        )

    # ----------------------------------------------------------
    # DIAGNOSTICS
    # ----------------------------------------------------------

    def get_calibration(self) -> float:
        """Global calibration score across all context-action pairs."""
        if not self._calibration_window:
            return 0.5
        return sum(self._calibration_window) / len(self._calibration_window)

    def get_surprise_profile(self, condition: Dict[str, str], action: str) -> Dict:
        """How surprising has this context-action pair been recently?"""
        ctx_key = self._context_key(condition)
        stats = self._get_stats(ctx_key, action)
        recent = list(stats.recent_surprises)
        return {
            "mean_surprise": sum(recent) / len(recent) if recent else 0.0,
            "max_surprise": max(recent) if recent else 0.0,
            "attempts": stats.attempts,
            "success_rate": stats.success_rate(),
            "prediction_confidence": stats.prediction_confidence(),
        }


# ============================================================
# INTEGRATION HELPER
# ============================================================

class PEAwareCME:
    """
    Thin wrapper that connects PEE to CME.
    Passes encoding_weight into reinforce_memory so surprise
    scales how strongly failures get written to memory.

    Drop-in replacement for calling cme.reinforce_memory() directly.
    """

    def __init__(self, cme, pee: PredictionErrorEngine):
        self.cme = cme
        self.pee = pee

    def step(
        self,
        condition: Dict[str, str],
        actions,
        step: int,
    ):
        """
        Returns bias surface + a dict of predictions keyed by action.
        Call this BEFORE choosing and executing an action.
        """
        bias = self.cme.emit_bias(condition, actions)
        predictions = {
            a: self.pee.predict(condition, a, step)
            for a in actions
        }
        return bias, predictions

    def update(
        self,
        condition: Dict[str, str],
        action: str,
        success: bool,
        step: int,
        prediction: ActionExpectation,
    ) -> PESignal:
        """
        Call after outcome is known.
        Handles CME update with surprise-scaled encoding.
        Returns PESignal for downstream use (Bandit, TFE).
        """
        # Compute surprise
        signal = self.pee.compute(prediction, success, step)

        # Update CME — scale reinforce_gain by encoding_weight
        if not success:
            # Temporarily boost reinforce_gain by encoding_weight
            original_gain = self.cme.reinforce_gain
            self.cme.reinforce_gain = original_gain * signal.encoding_weight
            self.cme.reinforce_memory(
                mem_type="CONSTRAINT",
                condition_subset=condition,
                action=action,
                step=step,
            )
            self.cme.reinforce_gain = original_gain  # Restore

        self.cme.counter_evidence(
            condition=condition,
            action=action,
            success=success,
            step=step,
        )

        return signal


# ============================================================
# TESTS
# ============================================================

def run_tests():
    """
    Validate core axioms with deterministic scenarios.
    """
    print("=" * 60)
    print("PREDICTION ERROR ENGINE — TEST SUITE")
    print("=" * 60)

    passed = 0
    failed = 0

    def check(name, condition, detail=""):
        nonlocal passed, failed
        if condition:
            print(f"  ✓ {name}")
            passed += 1
        else:
            print(f"  ✗ {name} {detail}")
            failed += 1

    pee = PredictionErrorEngine()
    condition = {"ctx": "X"}
    action = "A"

    # ----------------------------------------------------------
    # TEST 1: PE1 — Prediction precedes outcome
    # ----------------------------------------------------------
    print("\nTEST 1: PE1 — Prediction precedes outcome")
    exp = pee.predict(condition, action, step=1)
    check("Expectation generated before outcome", exp is not None)
    check("Initial prediction is 0.5 (no data)", abs(exp.predicted_success_prob - 0.5) < 0.01)
    check("Initial confidence is 0.0 (no data)", exp.prediction_confidence == 0.0)

    # ----------------------------------------------------------
    # TEST 2: PE2 — Sign is correct
    # ----------------------------------------------------------
    print("\nTEST 2: PE2 — Sign correctness")

    # Scenario: system expects 50/50, outcome is failure → negative surprise
    pee2 = PredictionErrorEngine()
    exp2 = pee2.predict({"ctx": "X"}, "A", step=1)
    sig2 = pee2.compute(exp2, success=False, step=1)
    check("Failure when expecting 50/50 → negative surprise", sig2.error_sign == -1,
          f"got {sig2.error_sign}")

    # Scenario: after many failures, system expects failure, gets success → positive surprise
    pee3 = PredictionErrorEngine()
    # Feed many failures to build expectation of failure
    for i in range(1, 20):
        e = pee3.predict({"ctx": "X"}, "A", step=i)
        pee3.compute(e, success=False, step=i)
    # Now expect failure, get success
    exp3 = pee3.predict({"ctx": "X"}, "A", step=20)
    check("System expects failure after many failures",
          exp3.predicted_success_prob < 0.2, f"got {exp3.predicted_success_prob:.3f}")
    sig3 = pee3.compute(exp3, success=True, step=20)
    check("Success when expecting failure → positive surprise", sig3.error_sign == 1,
          f"got {sig3.error_sign}")

    # ----------------------------------------------------------
    # TEST 3: PE3 — Encoding weight scales with surprise
    # ----------------------------------------------------------
    print("\nTEST 3: PE3 — Encoding weight scales with surprise")

    # Expected outcome should produce low encoding weight
    pee4 = PredictionErrorEngine()
    # Build strong expectation of success
    for i in range(1, 30):
        e = pee4.predict({"ctx": "X"}, "A", step=i)
        pee4.compute(e, success=True, step=i)
    # Now expected success happens
    e_expected = pee4.predict({"ctx": "X"}, "A", step=30)
    sig_expected = pee4.compute(e_expected, success=True, step=30)
    check("Expected outcome → low encoding weight",
          sig_expected.encoding_weight < 0.5, f"got {sig_expected.encoding_weight}")

    # Unexpected outcome should produce high encoding weight
    e_surprise = pee4.predict({"ctx": "X"}, "A", step=31)
    sig_surprise = pee4.compute(e_surprise, success=False, step=31)
    check("Unexpected failure → high encoding weight",
          sig_surprise.encoding_weight > 1.0, f"got {sig_surprise.encoding_weight}")
    check("Surprise encodes stronger than expected",
          sig_surprise.encoding_weight > sig_expected.encoding_weight,
          f"surprise={sig_surprise.encoding_weight}, expected={sig_expected.encoding_weight}")

    # ----------------------------------------------------------
    # TEST 4: PE4 — Confidence weighting
    # ----------------------------------------------------------
    print("\nTEST 4: PE4 — Confidence scales error significance")

    # Low confidence prediction error should encode weaker than
    # high confidence prediction error of same magnitude
    pee_low = PredictionErrorEngine()
    pee_high = PredictionErrorEngine()

    # pee_low: only 2 attempts (low confidence)
    for i in range(1, 3):
        e = pee_low.predict({"ctx": "X"}, "A", step=i)
        pee_low.compute(e, success=True, step=i)

    # pee_high: 50 attempts (high confidence)
    for i in range(1, 51):
        e = pee_high.predict({"ctx": "X"}, "A", step=i)
        pee_high.compute(e, success=True, step=i)

    # Same surprising failure in both
    e_low = pee_low.predict({"ctx": "X"}, "A", step=100)
    e_high = pee_high.predict({"ctx": "X"}, "A", step=100)
    sig_low = pee_low.compute(e_low, success=False, step=100)
    sig_high = pee_high.compute(e_high, success=False, step=100)

    check("High confidence prediction wrong → stronger signal",
          sig_high.encoding_weight > sig_low.encoding_weight,
          f"high={sig_high.encoding_weight}, low={sig_low.encoding_weight}")

    # ----------------------------------------------------------
    # TEST 5: Exploration boost only on negative surprise
    # ----------------------------------------------------------
    print("\nTEST 5: Exploration boost — negative surprise only")

    pee5 = PredictionErrorEngine()
    # Build expectation of success
    for i in range(1, 30):
        e = pee5.predict({"ctx": "X"}, "A", step=i)
        pee5.compute(e, success=True, step=i)

    # Positive surprise (expected failure, got success) — no boost
    for i in range(1, 20):
        e = pee5.predict({"ctx": "X"}, "B", step=i)
        pee5.compute(e, success=False, step=i)
    e_pos = pee5.predict({"ctx": "X"}, "B", step=100)
    sig_pos = pee5.compute(e_pos, success=True, step=100)
    check("Positive surprise → no exploration boost",
          sig_pos.exploration_boost == 0.0, f"got {sig_pos.exploration_boost}")

    # Negative surprise — should boost
    e_neg = pee5.predict({"ctx": "X"}, "A", step=101)
    sig_neg = pee5.compute(e_neg, success=False, step=101)
    check("Negative surprise → exploration boost > 0",
          sig_neg.exploration_boost > 0.0, f"got {sig_neg.exploration_boost}")

    # ----------------------------------------------------------
    # TEST 6: PE5 — Calibration tracks accuracy
    # ----------------------------------------------------------
    print("\nTEST 6: PE5 — Calibration score")

    pee6 = PredictionErrorEngine()
    # Perfect predictor: always predicts 50/50 with no data, alternates
    # Feed consistent signal
    for i in range(1, 51):
        e = pee6.predict({"ctx": "X"}, "A", step=i)
        pee6.compute(e, success=True, step=i)

    cal = pee6.get_calibration()
    check("Calibration score is a float 0..1", 0.0 <= cal <= 1.0, f"got {cal}")
    check("Calibration improves with consistent outcomes", cal > 0.5,
          f"got {cal}")

    # ----------------------------------------------------------
    # TEST 7: PE6 — Determinism
    # ----------------------------------------------------------
    print("\nTEST 7: PE6 — Determinism")

    def run_sequence(outcomes):
        p = PredictionErrorEngine()
        signals = []
        for i, outcome in enumerate(outcomes):
            e = p.predict({"ctx": "X"}, "A", step=i+1)
            s = p.compute(e, success=outcome, step=i+1)
            signals.append(s.encoding_weight)
        return signals

    seq = [True, True, False, True, False, False, True]
    run1 = run_sequence(seq)
    run2 = run_sequence(seq)
    check("Identical sequences produce identical signals", run1 == run2,
          f"run1={run1}, run2={run2}")

    # ----------------------------------------------------------
    # SUMMARY
    # ----------------------------------------------------------
    print(f"\n{'=' * 60}")
    print(f"TEST SUMMARY: {passed}/{passed+failed} passed")
    if failed == 0:
        print("✓ ALL TESTS PASSED — The signal holds.")
    else:
        print(f"✗ {failed} FAILURES — Review above.")
    print("=" * 60)

    return failed == 0


# ============================================================
# DEMO: PEE integrated with CME
# ============================================================

def run_demo():
    """
    Show prediction error changing CME encoding in practice.
    Two scenarios:
      A) Expected failure — weakly encoded
      B) Surprising failure — strongly encoded
    """
    import sys
    import os
    from halcyon_research_demo import CME

    print("\n" + "=" * 60)
    print("DEMO: Prediction Error Modulating CME Encoding")
    print("=" * 60)

    ACTIONS = ["A", "B", "C"]
    CONDITION = {"ctx": "test"}

    # --- Scenario A: Expected failure ---
    print("\n[Scenario A] Expected failure (system already knows A fails)")
    cme_a = CME(seed=42)
    pee_a = PredictionErrorEngine()
    pe_cme_a = PEAwareCME(cme_a, pee_a)

    # First train the system — many A failures so it expects A to fail
    for step in range(1, 30):
        bias, preds = pe_cme_a.step(CONDITION, ACTIONS, step)
        sig = pe_cme_a.update(CONDITION, "A", success=False, step=step,
                               prediction=preds["A"])

    # Now one more expected A failure
    bias, preds = pe_cme_a.step(CONDITION, ACTIONS, step=30)
    sig_expected = pe_cme_a.update(CONDITION, "A", success=False, step=30,
                                    prediction=preds["A"])

    print(f"  Predicted P(success): {sig_expected.predicted_prob:.3f}")
    print(f"  Error magnitude:      {sig_expected.error_magnitude:.3f}")
    print(f"  Encoding weight:      {sig_expected.encoding_weight:.3f}  ← weak")
    print(f"  Exploration boost:    {sig_expected.exploration_boost:.3f}")

    # --- Scenario B: Surprising failure ---
    print("\n[Scenario B] Surprising failure (system expects A to succeed)")
    cme_b = CME(seed=42)
    pee_b = PredictionErrorEngine()
    pe_cme_b = PEAwareCME(cme_b, pee_b)

    # Train system that A succeeds
    for step in range(1, 30):
        bias, preds = pe_cme_b.step(CONDITION, ACTIONS, step)
        sig = pe_cme_b.update(CONDITION, "A", success=True, step=step,
                               prediction=preds["A"])

    # Now surprise — A fails when system expects success
    bias, preds = pe_cme_b.step(CONDITION, ACTIONS, step=30)
    sig_surprise = pe_cme_b.update(CONDITION, "A", success=False, step=30,
                                    prediction=preds["A"])

    print(f"  Predicted P(success): {sig_surprise.predicted_prob:.3f}")
    print(f"  Error magnitude:      {sig_surprise.error_magnitude:.3f}")
    print(f"  Encoding weight:      {sig_surprise.encoding_weight:.3f}  ← strong")
    print(f"  Exploration boost:    {sig_surprise.exploration_boost:.3f}  ← opens exploration")
    print(f"  TFE reset signal:     {sig_surprise.tfe_reset}  ← environment changed")

    print(f"\n  Encoding difference: {sig_surprise.encoding_weight / max(sig_expected.encoding_weight, 0.01):.1f}x stronger on surprise")

    # --- Calibration ---
    print(f"\n  Calibration (A): {pee_b.get_calibration():.3f}")
    profile = pee_b.get_surprise_profile(CONDITION, "A")
    print(f"  Surprise profile: {profile}")

    print("\n✓ Demo complete.")


if __name__ == "__main__":
    tests_passed = run_tests()
    if tests_passed:
        run_demo()
