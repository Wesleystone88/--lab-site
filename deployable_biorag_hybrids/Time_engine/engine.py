
"""
Time Field Engine (Main Class)
Combines all sub-modules into the full runtime system.
"""

import time
from typing import Dict, List, Optional, Set, Union
from .config import TFEConfig
from .state import TFEState, KeyState, GapClass, KeyStatus, TempoBucket
from .observables import TFEObservables, AnomalySummary, KeyStateClass
from . import clock, dynamics, duration, persistence

class TimeFieldEngine:
    def __init__(self, config: Optional[TFEConfig] = None):
        if config is None:
            config = TFEConfig()
        self.config = config
        self.state = TFEState()
        
        # Initialize t_last to now to avoid massive jump on first tick
        self.state.t_last = time.monotonic()
        
        # Transient event buffer (not persisted)
        self._pending_lifecycle_events: List['KeyLifecycleEvent'] = []
        
        # Sub-modules
        self.clock = clock.EngineClock(clock.ClockConfig(dt_max=self.config.dt_max))

    def update(self, dt_override: Optional[float] = None) -> TFEObservables:
        """
        Main Engine Tick.
        Advances Clock -> Dynamics -> Observables.
        """
        now = time.monotonic()
        # ... (rest of update is same, just using _emit_observables which now reads the buffer)
        
        # 1. Clock & Sanitization
        if dt_override is not None:
            dt_raw = dt_override
            self.state.t_last = now # Sync logic clock
        else:
            dt_raw, anomaly = clock.measure_dt(self.state.t_last, now)
            self.state.anomalies_count += anomaly
            self.state.t_last = now
            
        dt_eff, overflow = self.clock.clamp_dt(dt_raw, self.config.dt_max)
        self.state.dt_overflow_total += overflow
        
        self.state.dt_last = dt_raw
        self.state.elapsed_total += dt_raw
        self.state.episode_age += dt_raw
        
        # 2. Episode Logic (Gap Classification)
        gap = dynamics.classify_gap(dt_raw, self.config.theta)
        self.state.gap_class = gap
        
        if gap in [GapClass.LONG, GapClass.RESET]:
            self.state.episode_id += 1
            self.state.episode_age = 0.0
            self.state.last_boundary_reason = f"gap:{gap.value}"
            
        # 3. Drift Dynamics (Keys)
        self.state.state_version = "v0.2" # Ensure version
        
        # Auto-Expiry Check
        keys_to_expire = []
        for key, kstate in self.state.keys.items():
            if kstate.status == KeyStatus.OPEN:
                idle_time = self.state.elapsed_total - kstate.last_event_elapsed
                if idle_time > self.config.t_expire:
                    keys_to_expire.append(key)
        
        for key in keys_to_expire:
            self._close_key_internal(key, "expired")
            self.state.key_expired_count += 1
            
        # Evolution (Staleness/Urgency)
        for key, kstate in self.state.keys.items():
            if kstate.status != KeyStatus.OPEN:
                continue
                
            tau = kstate.tau_override if kstate.tau_override else self.config.tau_staleness
            gain = kstate.urgency_gain_override if kstate.urgency_gain_override else self.config.urgency_gain
            
            # Update
            kstate.staleness = dynamics.evolve_staleness(kstate.staleness, dt_eff, tau)
            kstate.urgency = dynamics.evolve_urgency(kstate.urgency, dt_eff, gain)
            
        # 4. Observables Generation
        obs = self._emit_observables(dt_raw)
        return obs

    # --- Event Interface ---

    def open_key(self, key: str, tau_override: Optional[float] = None, urgency_gain_override: Optional[float] = None):
        """Register a key."""
        if key not in self.state.keys:
            self.state.keys[key] = KeyState()
            self.state.keys[key].created_elapsed = self.state.elapsed_total
            
        k = self.state.keys[key]
        if k.status != KeyStatus.OPEN:
             k.status = KeyStatus.OPEN
             k.staleness = 0.0
             k.urgency = 0.0
             
             # O14 Event
             from .observables import KeyLifecycleEvent
             self._pending_lifecycle_events.append(KeyLifecycleEvent(
                 key=key, status="open", elapsed_total=self.state.elapsed_total,
                 episode_id=self.state.episode_id, outcome=None
             ))
             
        k.last_event_elapsed = self.state.elapsed_total
        k.tau_override = tau_override
        k.urgency_gain_override = urgency_gain_override

    def close_key(self, key: str, outcome: str = "closed"):
        """Deregister a key."""
        self._close_key_internal(key, outcome)

    def _close_key_internal(self, key: str, outcome: str):
        if key in self.state.keys:
            k = self.state.keys[key]
            if k.status == KeyStatus.OPEN: # Only emit if it was open
                # O14 Event
                from .observables import KeyLifecycleEvent
                status_str = "expired" if outcome == "expired" else "closed"
                self._pending_lifecycle_events.append(KeyLifecycleEvent(
                    key=key, status=status_str, elapsed_total=self.state.elapsed_total,
                    episode_id=self.state.episode_id, outcome=outcome
                ))
            
            k.status = KeyStatus.EXPIRED if outcome == "expired" else KeyStatus.CLOSED
            k.last_event_elapsed = self.state.elapsed_total

    def boundary(self, kind: str = "manual"):
        """
        §4 I2 Boundary Event.
        Forces an episode boundary.
        """
        # Close all open keys implies a reset or major transition?
        # Blueprint says "Forces episode boundary".
        # We'll increment episode_id and reset age.
        self.state.episode_id += 1
        self.state.episode_age = 0.0
        self.state.last_boundary_reason = f"event:{kind}"
        self.state.gap_class = GapClass.RESET # Treat as reset gap

    def annotation(self, text: str):
        """
        §4 I2 Annotation Event.
        No-op for state, but useful for logs/debug.
        """
        pass

    def touch_key(self, key: str, magnitude: float = 1.0):
        """Reinforce a key."""
        if key in self.state.keys:
            k = self.state.keys[key]
            if k.status == KeyStatus.OPEN:
                 k.staleness = dynamics.reinforce(k.staleness, magnitude, self.config.r_s)
                 k.urgency = dynamics.reinforce(k.urgency, magnitude, self.config.r_u)
                 
                 # UPDATE TEMPO (§6.5)
                 dt_since = self.state.elapsed_total - k.last_event_elapsed
                 if dt_since > 0:
                     new_ema, _ = dynamics.update_tempo(
                         self.state.event_rate_ema, dt_since, 
                         self.config.alpha_tempo, (0.0, 0.0) # limits handled below
                     )
                     self.state.event_rate_ema = new_ema
                     
                     # Classify
                     if new_ema < self.config.tempo_limits[0]:
                         self.state.tempo_bucket = TempoBucket.QUIET
                     elif new_ema > self.config.tempo_limits[1]:
                         self.state.tempo_bucket = TempoBucket.FAST
                     else:
                         self.state.tempo_bucket = TempoBucket.NORMAL
                         
                 k.last_event_elapsed = self.state.elapsed_total
                 
    def start_task(self, signature: str):
        """Begin tracking a task duration."""
        self.state.running_tasks[signature] = time.monotonic()
        self.state.active_task = signature
        # Initialize stats if needed
        if signature not in self.state.duration_stats:
             from .state import DurationStats, DurationAnomalies
             self.state.duration_stats[signature] = DurationStats()
             self.state.duration_anomalies[signature] = DurationAnomalies()

    def end_task(self, signature: str, outcome: str = "ok", dur_override: Optional[float] = None):
        """End tracking a task duration."""
        if signature in self.state.running_tasks:
            start_time = self.state.running_tasks.pop(signature)
            now = time.monotonic()
            
            if self.state.active_task == signature:
                self.state.active_task = None
                
            if dur_override is not None:
                dur = dur_override
            else:
                dur = now - start_time
            
            # Update Stats
            if signature not in self.state.duration_stats:
                 return # Should exist if started, but safety
            
            stats = self.state.duration_stats[signature]
            anoms = self.state.duration_anomalies[signature]
            
            model = duration.DurationModel(config=self.config.duration, stats=stats)
            model.anomalies = anoms
            model.update(dur)
            self.state.duration_stats[signature] = model.stats

    # --- Persistence ---
    # --- Persistence ---
    def save_snapshot(self, path: str = None) -> Dict:
        """
        Save state to file (if path provided) and return dict.
        """
        self.state.last_saved_elapsed = self.state.elapsed_total
        
        import dataclasses
        import json
        
        # Serialize
        self.state.snapshot_config_at_save = dataclasses.asdict(self.config)
        data = persistence.save_snapshot(self.state)
        
        # Write to file if path
        target_path = path or self.config.save_path
        if target_path:
            with open(target_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        return data
        
    def load_snapshot(self, source: Union[Dict, str]):
        """
        Load state from dict or file path.
        """
        import json
        
        data = source
        if isinstance(source, str):
            with open(source, 'r') as f:
                data = json.load(f)
                
        # Handle restart logic here (Task drops)
        restored_state = persistence.load_snapshot(data)
        
        # Check for config conflict (S5 P9)
        # We compare critical params from snapshot vs current config
        snap_cfg = restored_state.snapshot_config_at_save
        if snap_cfg:
            # Simple check: if critical params differ
            # For now, simplistic check of existence implies we should check.
            # Test P9 expects conflict count increment.
            # Let's assume strict equality for now or key params.
            # Ideally verify 'tau_staleness', 'dt_max' etc.
            
            # For this test, we just check if they are different dicts?
            # Or reconstruct config?
            # Let's check a specific mismatch if possible, or just equality of dicts.
            import dataclasses
            current_cfg_dict = dataclasses.asdict(self.config)
            
            # Filter out save_path?
            
            if snap_cfg != current_cfg_dict:
                 restored_state.config_conflict_count += 1
        
        # Restart tracking
        restored_state.restart_count += 1
        restored_state.last_restart_elapsed = restored_state.elapsed_total
        
        # P1: Restart triggers an episode boundary
        restored_state.episode_id += 1
        restored_state.episode_age = 0.0
        from .state import GapClass
        restored_state.gap_class = GapClass.RESET
        restored_state.last_boundary_reason = "restart"
        
        # Drop tasks
        dropped = len(restored_state.running_tasks)
        restored_state.tasks_dropped_on_restart += dropped
        for sig in restored_state.running_tasks:
             if sig not in restored_state.duration_anomalies:
                 from .state import DurationAnomalies
                 restored_state.duration_anomalies[sig] = DurationAnomalies()
             restored_state.duration_anomalies[sig].interrupted_on_load += 1
        restored_state.running_tasks.clear()
        restored_state.active_task = None
        
        # Sync clock
        restored_state.t_last = time.monotonic()
        
        self.state = restored_state

    # --- Internals ---
    def _emit_observables(self, dt_raw: float) -> TFEObservables:
        # Build O13 Map
        key_states = {}
        # aggregates
        s_sum = 0.0
        u_sum = 0.0
        count = 0
        
        for k, v in self.state.keys.items():
            if v.status == KeyStatus.OPEN:
                cls = dynamics.classify_key_state(v.staleness, v.urgency)
                key_states[k] = cls
                s_sum += v.staleness
                u_sum += v.urgency
                count += 1
                
        s_global = s_sum / count if count > 0 else 0.0
        u_global = u_sum / count if count > 0 else 0.0
        
        # Stall Detection
        stall_detected = False
        stall_sigs = []
        now = time.monotonic()
        
        for sig, start_t in self.state.running_tasks.items():
            if sig in self.state.duration_stats:
                stats = self.state.duration_stats[sig]
                is_stall, fallback = duration.check_stall(start_t, now, stats, self.config.duration)
                if is_stall:
                    stall_detected = True
                    stall_sigs.append(sig)
                    # Note on blueprint anomaly counting: handled by caller/observer if needed
                    # but typically we avoid mutating state in the observable generation phase.
        
        # dt_human Logic (O3)
        if dt_raw < 60.0:
            dt_h = f"~{dt_raw:.1f}s"
        elif dt_raw < 3600.0:
            dt_h = f"~{dt_raw/60.0:.1f}m"
        else:
            dt_h = f"~{dt_raw/3600.0:.1f}h"
            
        # O14 Lifecycle Events (Consume buffer)
        events_this_tick = list(self._pending_lifecycle_events)
        self._pending_lifecycle_events.clear()
            
        return TFEObservables(
            dt_seconds=dt_raw,
            elapsed_total_seconds=self.state.elapsed_total,
            dt_human=dt_h,
            gap_class=self.state.gap_class,
            episode_id=self.state.episode_id,
            episode_age_seconds=self.state.episode_age,
            reentry_mode=(self.state.gap_class in [GapClass.LONG, GapClass.RESET]),
            staleness_global=s_global,
            urgency_global=u_global,
            tempo_bucket=self.state.tempo_bucket,
            event_rate_ema=self.state.event_rate_ema,
            stall_detected=stall_detected, 
            stall_signatures=stall_sigs,
            anomaly_summary=AnomalySummary(
                negative_dt_count=self.state.anomalies_count,
                dt_overflow_total=self.state.dt_overflow_total,
                key_expired_count=self.state.key_expired_count,
                tasks_dropped_on_restart=self.state.tasks_dropped_on_restart,
                config_conflict_count=self.state.config_conflict_count
            ),
            key_states=key_states,
            lifecycle_events=events_this_tick
        )
