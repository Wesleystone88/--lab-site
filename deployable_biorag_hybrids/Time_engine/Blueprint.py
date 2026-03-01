TIME FIELD ENGINE (TFE) - FIRST-PRINCIPLES BLUEPRINT (REVISED)
Version: 0.2 "Existence Complete Candidate"
Incorporates: Blueprint Review fixes + warnings resolved
Framing: Control theory + thermodynamics + biology (field physics as regulated flows)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CHANGELOG v0.1 → v0.2 (WHAT WAS FIXED)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Added key lifecycle: OPEN / CLOSE + auto-expiry T_expire
✓ Promoted per-key state from "recommended" → REQUIRED; added key_status + key_created_elapsed
✓ Resolved dt_raw vs dt_eff ambiguity with explicit assignment table
✓ Strengthened duration model: variance floor + conf-gated stall detection + fallback timeout
✓ Defined winsorization precisely
✓ Added calibrated flag to duration_prediction observable
✓ Made in-flight task drops on restart observable: synthetic END_TASK(interrupted) + anomaly counter
✓ Added restart tracking fields: restart_count, last_restart_elapsed
✓ Added combined-state observable O13 key_state_class
✓ Added missing config params: C6b/C6c/C6d/C9
✓ Added missing tests TST11–TST14
✓ Tightened DONE criteria so "complete" cannot be claimed prematurely
✓ Clarified G4 applies to predictions, not measured dt humanizations

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
§0 - DEFINITIONS (LOCKED VOCAB)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Time (for TFE): Irreversible progression of system state measured by monotonic duration, not wall-clock.
• Field: Continuously evolving state governed by laws; accepts impulses (events) and emits observables.
• Observable: Measurable output of the field (safe for downstream consumption).
• Episode: Temporal chunk partitioning induced by gaps/boundaries.
• Key: A tracked temporal entity (goal/thread/task label) with lifecycle (open→closed/expired).
• Decay (staleness): Drift toward "stale" without reinforcement.
• Pressure (urgency): Drift toward "urgent" without progress/resolution.
• Calibration: Learning action duration distributions from measured runs.

Hard rule: TFE never asserts calendar facts. Only duration + time-derived observables.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
§1 - PURPOSE (COMPLETENESS REQUIREMENT)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The TFE exists to provide:
A) Duration sense (monotonic elapsed time, robust to clock jumps)
B) Temporal structure (episodes, gaps, re-entry flags)
C) Drift dynamics (staleness/forgetting and urgency/pressure that evolve in silence)
D) Expectation (duration prediction p50/p90/conf + calibration)
E) Falsifiability (deterministic under fake clock; tests define correctness)

If any of A–E is missing, "time field existence" is incomplete.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
§2 - AXIOMS (INVARIANTS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
T1 Monotonicity: elapsed_total(t+Δ) >= elapsed_total(t) for Δ>=0; dt never negative after sanitization.
T2 Causality/Ordering: events are ordered; episode boundaries partition the event stream.
T3 No calendar dependence: dynamics depend only on dt + events + persisted state.
T4 Decay inevitable: without reinforcement, staleness non-decreases (in expectation).
T5 Pressure accumulates: without progress, urgency non-decreases until saturation.
T6 Truthfulness: measured durations are observations; predictions are explicitly labeled and uncertainty-bounded.
T7 Determinism: identical dt sequence + event sequence + seed → identical observables.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
§3 - SYSTEM BOUNDARY (IS / IS NOT)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TFE IS:
• a temporal field simulator (state + laws + persistence + tests)
• an estimator of durations + temporal drift
• a provider of time-derived control signals (re-entry, stall, staleness/urgency classes)

TFE IS NOT:
• a scheduler/controller for other modules
• a calendar/timezone service
• a language generator
• a store of conversation content

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
§4 - INPUTS (ALLOWED INGRESS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
I1 - Clock tick (required)
  now = monotonic_time_seconds()

I2 - Event impulses (minimum complete set; REQUIRED for full functionality)
Event types (schema-level required):

  KEY LIFECYCLE (REQUIRED)
  • OPEN(key, urgency_gain_override?=None, decay_tau_override?=None)
      Registers key. Initializes per-key state. Sets key_status=open.
  • CLOSE(key, outcome=ok|abandoned|failed|expired|interrupted)
      Deregisters key. Sets key_status=closed or expired. Emits final key closure observable.

  PROGRESS / REINFORCEMENT
  • PROGRESS(key, magnitude∈[0,1])
      Reduces urgency and staleness for that key (only if key_status=open).

  EPISODE CONTROL
  • BOUNDARY(kind)  # forces episode boundary; records reason

  TASK TIMING (for duration calibration)
  • START_TASK(signature, key?=None)
  • END_TASK(signature, outcome=ok|fail|interrupted, dur_override?=None)
      If dur_override is supplied (e.g., interrupted-on-load), use it as "unknown" placeholder.

  METADATA (NO-OP BY DEFAULT)
  • ANNOTATION(payload)
      Must not change field state unless explicitly configured (see TST14).

I3 - Configuration parameters (required)
  Set at initialization; may be updated only via explicit CONFIG_UPDATE event (optional feature).
  In v0.2 baseline: config is immutable after init (simplifies determinism).

Key auto-expiry (REQUIRED):
• If a key receives no events for T_expire seconds while open, auto-CLOSE with outcome=expired and raise anomaly.
• T_expire defined in §10 (C9).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
§5 - STATE (THE FIELD)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
S0 - Core time anchors
• t_last                 : float (monotonic seconds)
• elapsed_total          : float
• dt_last                : float
• anomalies_count         : int
• dt_overflow_total       : float (accumulated dt_raw - dt_eff when clamping)

S1 - Episode structure
• episode_id              : int
• episode_age             : float
• last_boundary_reason    : str|enum
• gap_class               : enum {immediate, short, medium, long, reset}

S2 - Drift fields (REQUIRED PER-KEY)
Per-key fields (REQUIRED):
• staleness[key]          : float in [0,1]
• urgency[key]            : float in [0,1]
• key_status[key]         : enum {open, closed, expired}
• key_created_elapsed[key]: float
• key_last_event_elapsed[key] : float
Optional global aggregates (RECOMMENDED, not required):
• staleness_global        : float in [0,1]
• urgency_global          : float in [0,1]

S3 - Tempo / event rate
• event_rate_ema          : float (events/sec)
• last_event_time         : float
• tempo_bucket            : enum {quiet, normal, busy}

S4 - Task timing + duration model (REQUIRED)
• running_tasks[signature] = start_time_monotonic
• duration_stats[signature]:
    n                    : int
    ema_mean             : float
    ema_var              : float
    p50                  : float
    p90                  : float
    conf                 : float
    calibrated           : bool  (derived; also emitted)
• duration_anomalies[signature]:
    outliers_clamped     : int
    interrupted_on_load  : int
    timeouts_fallback    : int

S5 - Persistence / restart tracking
• state_version           : str
• last_saved_elapsed      : float
• restart_count           : int
• last_restart_elapsed    : float
• tasks_dropped_on_restart: int
• snapshot_config_at_save : dict (audit)
• config_conflict_count   : int

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
§6 - LAWS OF MOTION (DYNAMICS / "PHYSICS")
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
§6.1 dt measurement + sanitization
dt_raw = now - t_last
if dt_raw < 0:
  dt_raw = 0
  anomalies_count += 1

dt_eff = min(dt_raw, dt_max)  # dt_max configurable (heartbeat stability)
dt_overflow_total += (dt_raw - dt_eff) if dt_raw > dt_eff else 0

t_last = now
elapsed_total += dt_raw
dt_last = dt_raw
episode_age += dt_raw

✗ FIX APPLIED - dt assignment table (MANDATORY)
• Episode gap classification (§6.2)  → dt_raw  (must see real gap)
• Decay / staleness         (§6.3)  → dt_eff  (clamped stability)
• Urgency / pressure        (§6.4)  → dt_eff
• Tempo / event density     (§6.5)  → dt_raw  (real interval)
• Key auto-expiry           (§6.8)  → dt_raw  (real elapsed)

§6.2 Episode gap classification (biology)
Given thresholds θ=(θ0, θ1, θ2, θ3) seconds:
  immediate if dt_raw < θ0
  short     if θ0 <= dt_raw < θ1
  medium    if θ1 <= dt_raw < θ2
  long      if θ2 <= dt_raw < θ3
  reset     if dt_raw >= θ3

If gap_class ∈ {long, reset}: start new episode:
  episode_id += 1
  episode_age = 0
  last_boundary_reason = "gap:"+gap_class

BOUNDARY(kind) event forces:
  episode_id += 1
  episode_age = 0
  last_boundary_reason = "boundary:"+kind

§6.3 Decay / staleness (thermodynamics)
For each key where key_status=open:
  staleness[key] ← 1 - (1 - staleness[key]) * exp(-dt_eff / τ_s(key))
where τ_s(key) is default τ_s unless overridden at OPEN.

PROGRESS(key, m):
  if key_status[key]=open:
    staleness[key] ← clip(staleness[key] - r_s * m, 0, 1)

§6.4 Urgency / pressure (control theory)
For each key where key_status=open:
  urgency[key] ← clip(urgency[key] + k_u(key) * dt_eff, 0, 1)

PROGRESS(key, m):
  if key_status[key]=open:
    urgency[key] ← clip(urgency[key] - r_u * m, 0, 1)

OPEN(key,...):
  initialize staleness[key]=0, urgency[key]=0
  key_status[key]=open
  key_created_elapsed[key]=elapsed_total
  key_last_event_elapsed[key]=elapsed_total

CLOSE(key,outcome):
  if key exists:
    key_status[key] = expired if outcome=expired else closed
    key_last_event_elapsed[key]=elapsed_total

§6.5 Tempo / event density (biology proxy)
On any event (excluding pure clock tick):
  rate = 1 / max(epsilon, now - last_event_time)
  event_rate_ema ← (1-α)*event_rate_ema + α*rate
  last_event_time = now
tempo_bucket derived from thresholds on event_rate_ema.

§6.6 Duration expectation model (learning / calibration)
On START_TASK(signature):
  running_tasks[signature]=now

On END_TASK(signature, outcome, dur_override?):
  if dur_override is not None:
    dur = dur_override
  else:
    dur = now - running_tasks[signature]

  remove running_tasks[signature] if present

  Update stats with winsorization + variance floor:

  • Compute provisional p50/p90 BEFORE update for outlier check if n>0; else use fallback p50/p90.
  • Outlier clamp (winsorization, DEFINED):
      if n>0 and dur > outlier_mult * p90:
          dur = outlier_mult * p90
          duration_anomalies[signature].outliers_clamped += 1

  EMA updates:
      ema_mean ← (1-β)*ema_mean + β*dur
      ema_var  ← (1-β)*ema_var  + β*(dur - ema_mean)^2

  Variance floor (FIXED):
      var_floor = (var_floor_mult * ema_mean)^2
      ema_var = max(ema_var, var_floor)

  Derived quantiles (baseline approx):
      p50 ≈ ema_mean
      p90 ≈ ema_mean + z90 * sqrt(ema_var)   (z90≈1.28)

  Confidence (gated by n):
      conf_raw = log(1+n)/log(1+n_ref)
      conf = clamp(conf_raw, 0, 1)
      calibrated = (conf >= conf_min_for_stall)

§6.7 Stall detection (control safety)
For each running task signature:
  running_time = now - running_tasks[signature]

  if duration_stats[signature].calibrated:
      stall_detected = (running_time > p90)
  else:
      stall_detected = (running_time > T_stall_fallback)
      if stall_detected:
          duration_anomalies[signature].timeouts_fallback += 1

  Additionally: stall detection is only actionable if conf >= conf_min_for_stall OR fallback triggered.

§6.8 Key auto-expiry (REQUIRED)
If key_status[key]=open and (elapsed_total - key_last_event_elapsed[key]) > T_expire:
  CLOSE(key, outcome=expired)
  anomalies_count += 1  (and increment key_expired_count anomaly)
  Emit closure observable (see §7 O14).

ANNOTATION(payload) (NO-OP baseline):
  Must not change any state variables (§11 TST14).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
§7 - OBSERVABLES (OUTPUT CONTRACT)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Emit on every update tick (clock or event):
O1 dt_seconds                    = dt_raw
O2 elapsed_total_seconds          = elapsed_total
O3 dt_human (MEASURED)            = humanize(dt_raw)  # observation, not prediction
O4 gap_class
O5 episode_id, episode_age_seconds
O6 reentry_mode                   = (gap_class in {long, reset})
O7 staleness_global (optional aggregate) + per-key bucket map
O8 urgency_global (optional aggregate) + per-key bucket map
O9 tempo_bucket + event_rate_ema

O10 duration_prediction(signature):
    {
      p50, p90, conf,
      calibrated: bool
    }
  NOTE: calibrated=false means p50/p90 must be treated as non-actionable guidance; stall uses fallback.

O11 stall_detected + stall_signatures

O12 anomaly_summary:
    {
      negative_dt_count,
      dt_overflow_total,
      outliers_clamped_total,
      tasks_dropped_on_restart,
      config_conflict_count,
      key_expired_count
    }

O13 key_state_class(key): enum { healthy | pending | abandoned | orphaned }
Derived from (staleness_bucket, urgency_bucket) for open keys:
  staleness low / urgency low  => healthy
  staleness low / urgency high => pending
  staleness high / urgency low => abandoned
  staleness high / urgency high=> orphaned

O14 key_lifecycle_event(key):
    { status: open|closed|expired, outcome?, elapsed_total, episode_id }
Emitted on OPEN/CLOSE/auto-expire.

Humanization rules:
  <60s: "~Xs"
  <3600s: "~Xm"
  else: "~X.Xh"
(O3 is derived from measured dt_raw; it is an observation.)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
§8 - HEARTBEAT (CONTINUITY)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Heartbeat mode required:
• run_forever(tick_interval_s)
Every tick:
  call update() with clock tick only
This guarantees drift evolves in silence.

dt_max clamping is allowed for dynamics, but episode boundaries MUST still fire on dt_raw.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
§9 - PERSISTENCE (STAND-ALONE REALNESS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
P1 Snapshot format (REQUIRED)
Snapshot contains:
• state_version, all state variables S0–S5, duration_stats/anomalies, keys, and snapshot_config_at_save.

P2 Save triggers
• periodic or explicit SAVE event.

P3 Load semantics (FIXED)
On load:
• restart_count += 1
• last_restart_elapsed = elapsed_total
• t_last resets to current monotonic now
• running_tasks handling (NO SILENT DROP):
    For each (signature,start_time) in running_tasks from snapshot:
      Fire synthetic END_TASK(signature, outcome=interrupted, dur_override=0)
      duration_anomalies[signature].interrupted_on_load += 1
      tasks_dropped_on_restart += 1
    Then clear running_tasks.
• Record restart boundary as episode boundary:
    episode_id += 1
    episode_age = 0
    last_boundary_reason = "restart"

Config conflict policy (FIXED):
• Runtime config takes precedence over snapshot config.
• If different, increment config_conflict_count and store snapshot_config_at_save for audit.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
§10 - CONFIGURATION (CLOSED SET)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
C0 gap thresholds θ0..θ3 (seconds)
C1 decay constants τ_s (global; optional per-key override at OPEN)
C2 urgency gain k_u (global; optional per-key override at OPEN)
C3 reinforcement coefficients r_s, r_u
C4 heartbeat tick interval
C5 dt_max clamp for dt_eff
C6 duration model params:
   β, outlier_mult, n_ref, z90
C6b var_floor_mult (default 0.1)
C6c conf_min_for_stall (default 0.5)
C6d T_stall_fallback (seconds, default 300)
C7 bucket thresholds for staleness/urgency/tempo
C8 persistence path + save cadence
C9 T_expire (seconds) - key auto-expiry threshold

Config is immutable after init in v0.2 baseline (simplifies determinism).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
§11 - TEST HARNESS (FALSIFIABILITY CONTRACT)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
A fake clock is mandatory for deterministic tests.

Existing tests (TST1–TST10) remain, with TST9 extended for restart task drops.

Added tests (FIXED):
TST11 - Key lifecycle
  OPEN(key) → key_status=open; CLOSE(key) → key_status=closed;
  advance fake time beyond T_expire → key_status=expired; anomaly key_expired_count increments; O14 emitted.

TST12 - Low-n stall gate
  n=1 (conf below threshold): run task past p90 → stall_detected FALSE unless > T_stall_fallback
  reach n>=~5 (conf >= conf_min_for_stall): repeat → stall_detected TRUE when running_time > p90

TST13 - dt_raw vs dt_eff fork
  Feed dt_raw >> dt_max:
    assert gap_class computed from dt_raw triggers episode boundary
    assert decay/urgency increments correspond to dt_eff (clamped), not dt_raw

TST14 - ANNOTATION no-op
  Fire ANNOTATION → assert all state vars unchanged; only tempo may update if you count it as an event.
  (Baseline: ANNOTATION must not change drift/episode/task state.)

TST9 extension (FIXED):
  start a task; save snapshot; load; assert tasks_dropped_on_restart > 0 in O12;
  assert interrupted_on_load incremented; assert running_tasks empty; restart boundary recorded.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
§12 - SAFETY / HONESTY GUARANTEES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
G1 Never produce calendar claims.
G2 Measured-duration statements (O3) derive strictly from dt_raw observation.
G3 Negative dt never propagates; clamp and report.
G4 Prediction honesty applies to O10:
   duration predictions always include {p50,p90,conf,calibrated}.
   Measured humanization (O3) is observation and may be stated plainly.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
§13 - FILE / COMPONENT MAP (IMPLEMENTATION-READY)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
/tfe
  clock.py
  config.py
  state.py
  dynamics.py
  duration.py
  engine.py
  persistence.py
  heartbeat.py
  events.py
  observables.py
  tests/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
§14 - "DONE" CRITERIA (LOCKED EXIT CONDITION)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Blueprint is finished ONLY when all are true:
☐ Key lifecycle OPEN/CLOSE + T_expire defined (§4, §10) and tested (TST11)
☐ Per-key state mandatory + key_status present (§5) and used in laws (§6)
☐ dt_raw vs dt_eff fork explicitly specified (§6.1 table) and tested (TST13)
☐ Duration model includes var_floor + conf gate + fallback stall (§6.6–§6.7) and tested (TST12)
☐ Winsorization precisely defined (§6.6)
☐ O10 includes calibrated flag (§7) and consumers can gate behavior
☐ Restart in-flight task drops observable (§9 P3 + TST9 extension)
☐ O13 key_state_class defined and emitted (§7)
☐ Tests TST1–TST14 present and passing (§11)
☐ Honesty guarantees consistent with observables (§12)

When all boxes are checked, "Existence Complete" is valid.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
§15 - OPTIONAL EXTENSIONS (NOT REQUIRED FOR EXISTENCE)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Subjective time warping τ̂ from tempo/engagement
• Multi-timescale decay layers
• Hierarchical episodes
• Bayesian duration model / quantile sketch
• Cross-device calibration profiles

END OF BLUEPRINT v0.2
