"""
TFE State Definitions (§5 Blueprint v0.2)
Typed storage for all system state.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum

# Enums
class GapClass(str, Enum):
    IMMEDIATE = "immediate"
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"
    RESET = "reset"

class KeyStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    EXPIRED = "expired"

class TempoBucket(str, Enum):
    QUIET = "quiet"
    NORMAL = "normal"
    BUSY = "busy"

class KeyStateClass(str, Enum):
    HEALTHY = "healthy"
    PENDING = "pending"
    ABANDONED = "abandoned"
    ORPHANED = "orphaned"

@dataclass
class DurationStats:
    n: int = 0
    ema_mean: float = 0.0
    ema_var: float = 0.0
    # Derived snapshot values (for persistence/consistency)
    p50: float = 0.0
    p90: float = 0.0
    conf: float = 0.0
    calibrated: bool = False

@dataclass
class DurationAnomalies:
    outliers_clamped: int = 0
    interrupted_on_load: int = 0
    timeouts_fallback: int = 0

@dataclass
class KeyState:
    status: KeyStatus = KeyStatus.OPEN
    staleness: float = 0.0
    urgency: float = 0.0
    created_elapsed: float = 0.0
    last_event_elapsed: float = 0.0
    # Per-key overrides (optional)
    tau_override: Optional[float] = None
    urgency_gain_override: Optional[float] = None

@dataclass
class TFEState:
    # S0: Core Time Anchors
    t_last: float = 0.0
    elapsed_total: float = 0.0
    dt_last: float = 0.0
    anomalies_count: int = 0
    dt_overflow_total: float = 0.0
    
    # S1: Episode Structure
    episode_id: int = 0
    episode_age: float = 0.0
    last_boundary_reason: str = "init"
    gap_class: GapClass = GapClass.IMMEDIATE
    
    # S2: Drift Fields (Keys)
    keys: Dict[str, KeyState] = field(default_factory=dict)
    
    # S3: Tempo
    event_rate_ema: float = 0.0
    last_event_time: float = 0.0
    tempo_bucket: TempoBucket = TempoBucket.NORMAL
    
    # S4: Task Timing
    active_task: Optional[str] = None # Current task key
    running_tasks: Dict[str, float] = field(default_factory=dict) # signature -> start_time
    duration_stats: Dict[str, DurationStats] = field(default_factory=dict)
    duration_anomalies: Dict[str, DurationAnomalies] = field(default_factory=dict)
    
    # S5: Persistence
    state_version: str = "v0.2"
    last_saved_elapsed: float = 0.0
    restart_count: int = 0
    last_restart_elapsed: float = 0.0
    tasks_dropped_on_restart: int = 0
    config_conflict_count: int = 0
    key_expired_count: int = 0
    
    snapshot_config_at_save: Dict = field(default_factory=dict)
