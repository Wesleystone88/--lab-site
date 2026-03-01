"""
TFE Persistence Module (§9 Blueprint v0.2)
Handles Snapshot serialization and restoration.
"""

import json
import dataclasses
from typing import Dict, Any
from .state import TFEState, KeyState, DurationStats, DurationAnomalies, GapClass, KeyStatus, TempoBucket
from .config import TFEConfig

class TFEJSONEncoder(json.JSONEncoder):
    """Custom encoder for TFE State types."""
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if hasattr(o, "value"): # Enum
            return o.value
        return super().default(o)

def save_snapshot(state: TFEState) -> Dict[str, Any]:
    """
    Serialize state to dict structure.
    """
    # Use dataclasses.asdict but might need custom handling for complex types if any
    return dataclasses.asdict(state)

def load_snapshot(data: Dict[str, Any]) -> TFEState:
    """
    Deserialize dict to TFEState.
    Reconstructs nested dataclasses and Enums.
    """
    # Reconstruct Keys
    keys = {}
    for k, v in data.get("keys", {}).items():
        keys[k] = KeyState(
            status=KeyStatus(v["status"]),
            staleness=v["staleness"],
            urgency=v["urgency"],
            created_elapsed=v["created_elapsed"],
            last_event_elapsed=v["last_event_elapsed"],
            tau_override=v.get("tau_override"),
            urgency_gain_override=v.get("urgency_gain_override")
        )

    # Reconstruct Duration Stats
    dur_stats = {}
    for k, v in data.get("duration_stats", {}).items():
        dur_stats[k] = DurationStats(**v)

    # Reconstruct Anomalies
    dur_anom = {}
    for k, v in data.get("duration_anomalies", {}).items():
        dur_anom[k] = DurationAnomalies(**v)

    return TFEState(
        t_last=data["t_last"],
        elapsed_total=data["elapsed_total"],
        dt_last=data["dt_last"],
        anomalies_count=data["anomalies_count"],
        dt_overflow_total=data["dt_overflow_total"],
        
        episode_id=data["episode_id"],
        episode_age=data["episode_age"],
        last_boundary_reason=data["last_boundary_reason"],
        gap_class=GapClass(data["gap_class"]),
        
        keys=keys,
        
        event_rate_ema=data["event_rate_ema"],
        last_event_time=data["last_event_time"],
        tempo_bucket=TempoBucket(data["tempo_bucket"]),
        
        running_tasks=data.get("running_tasks", {}),
        duration_stats=dur_stats,
        duration_anomalies=dur_anom,
        
        state_version=data["state_version"],
        last_saved_elapsed=data["last_saved_elapsed"],
        restart_count=data["restart_count"],
        last_restart_elapsed=data["last_restart_elapsed"],
        tasks_dropped_on_restart=data["tasks_dropped_on_restart"],
        config_conflict_count=data["config_conflict_count"],
        key_expired_count=data.get("key_expired_count", 0),
        snapshot_config_at_save=data.get("snapshot_config_at_save", {}),
        active_task=data.get("active_task")
    )
