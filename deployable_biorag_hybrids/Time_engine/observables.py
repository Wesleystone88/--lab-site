"""
TFE Observables (§7 Blueprint v0.2)
Output data structures emitted by the engine.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from .state import GapClass, KeyStateClass, TempoBucket

@dataclass
class DurationPrediction:
    p50: float
    p90: float
    conf: float
    calibrated: bool

@dataclass
class AnomalySummary:
    negative_dt_count: int = 0 # Tracked in engine local, summed to state anomalies
    dt_overflow_total: float = 0.0
    outliers_clamped_total: int = 0
    tasks_dropped_on_restart: int = 0
    config_conflict_count: int = 0
    key_expired_count: int = 0

@dataclass
class KeyLifecycleEvent:
    key: str
    status: str # open/closed/expired
    elapsed_total: float
    episode_id: int
    outcome: Optional[str] = None

@dataclass
class TFEObservables:
    # O1-O3 Time
    dt_seconds: float
    elapsed_total_seconds: float
    dt_human: str 
    
    # O4-O6 Structure
    gap_class: GapClass
    episode_id: int
    episode_age_seconds: float
    reentry_mode: bool
    
    # O7-O8 Drift (Snapshots)
    staleness_global: float
    urgency_global: float
    
    # O9 Tempo
    tempo_bucket: TempoBucket
    event_rate_ema: float
    
    # O10 Duration Predictions (on demand or broadcast?)
    # Usually accessed via method, but can be snapshot.
    # For now, we'll keep this separate or include specific requested sigs.
    
    # O11 Stall
    stall_detected: bool
    stall_signatures: List[str]
    
    # O12 Anomalies
    anomaly_summary: AnomalySummary
    
    # O13 Key Classes (Map) - Expensive to emit all every tick? 
    # Blueprint says "Emit on every update tick".
    # We will emit a map for OPEN keys.
    key_states: Dict[str, KeyStateClass] = field(default_factory=dict)

    # O14 Lifecycle events (Transient)
    lifecycle_events: List[KeyLifecycleEvent] = field(default_factory=list)
