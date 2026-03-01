"""
metabolic_residue.py — Standalone Metabolic Residue Mechanism (Spec v1.1)

Implements the "metabolic residue" intake side-channel as a bounded, decaying,
NON-BINDING audit trace.

This is a standalone module: no CME dependencies required.

Design anchor: your uploaded v1.1 fixed spec. :contentReference[oaicite:0]{index=0}
"""

from __future__ import annotations

import hashlib
import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, ClassVar, Dict, Iterable, List, Optional, Tuple


# =========================
# Enums / Reason Codes
# =========================

class CandidateType(str, Enum):
    CLAIM = "claim"
    CONSTRAINT = "constraint"
    SKILL = "skill"
    ENTITY = "entity"
    PROCEDURE = "procedure"
    EXAMPLE = "example"
    QUOTE = "quote"
    OTHER = "other"


class ReasonCode(str, Enum):
    REDUNDANT = "REDUNDANT"
    CONFLICTS_WITH_CONSTRAINT = "CONFLICTS_WITH_CONSTRAINT"
    LOW_EVIDENCE = "LOW_EVIDENCE"
    LOW_SALIENCE = "LOW_SALIENCE"
    TOO_SPECIFIC = "TOO_SPECIFIC"
    TOO_VAGUE = "TOO_VAGUE"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    UNSAFE_POLICY = "UNSAFE_POLICY"
    FORMAT_NOISE = "FORMAT_NOISE"
    DUPLICATE_IN_DOC = "DUPLICATE_IN_DOC"
    RATE_LIMITED = "RATE_LIMITED"
    UNKNOWN = "UNKNOWN"


class IntakeMode(str, Enum):
    EXPLORE = "explore"   # commit more, lower threshold
    COMMIT = "commit"     # baseline
    AUDIT = "audit"       # commit almost nothing, high threshold


class ReconsiderationTrigger(str, Enum):
    HUMAN_REQUEST = "HUMAN_REQUEST"
    CONTEXT_SCOPE_EXPANDED = "CONTEXT_SCOPE_EXPANDED"
    CONSTRAINT_CHANGED = "CONSTRAINT_CHANGED"
    RATE_LIMITED_RETRY = "RATE_LIMITED_RETRY"


# =========================
# Helpers
# =========================

def _now() -> float:
    return time.time()


def normalize_text(s: str) -> str:
    # Stable normalization for hashing; intentionally conservative.
    return " ".join(s.strip().lower().split())


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", errors="ignore")).hexdigest()


def clamp(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x


# =========================
# Core Data Structures
# =========================

@dataclass(frozen=True)
class Candidate:
    """
    Candidate is ephemeral during intake. You can create these from any parser.
    """
    id: str
    type: CandidateType
    content: str
    doc_id: str
    span: Optional[Tuple[int, int]] = None
    features: Dict[str, Any] = field(default_factory=dict)

    @property
    def content_hash(self) -> str:
        return sha256_hex(normalize_text(self.content))


@dataclass(frozen=True)
class ScoreBreakdown:
    """
    Raw components are non-negative. Phi is normalized [0,1] via divisive normalization.
    """
    U_raw: float
    K_raw: float
    D_raw: float
    E_raw: float
    Phi: float

    @staticmethod
    def compute(U_raw: float, K_raw: float, D_raw: float, E_raw: float, eps: float = 1e-9) -> "ScoreBreakdown":
        U = max(0.0, float(U_raw))
        K = max(0.0, float(K_raw))
        D = max(0.0, float(D_raw))
        E = max(0.0, float(E_raw))
        C = K + D + E
        gain = 1.0 / (1.0 + C + eps)
        phi = clamp(U * gain, 0.0, 1.0)
        return ScoreBreakdown(U, K, D, E, phi)


@dataclass
class ResidueContext:
    project: str = "default"
    task_signature: str = "default"
    intake_mode: IntakeMode = IntakeMode.COMMIT
    key: Optional[str] = None   # CME-style key, if you have one


@dataclass
class ResidueRecord:
    """
    The residue trace is NON-BINDING and TTL-capped.
    Default: store hash + tiny snippet only (optional).
    """
    residue_id: str
    doc_id: str
    candidate_hash: str
    candidate_type: CandidateType
    snippet: Optional[str]
    scores: ScoreBreakdown
    reasons: List[Tuple[ReasonCode, float]]  # top-k reason vector
    context: ResidueContext

    created_at: float = field(default_factory=_now)
    last_seen_at: float = field(default_factory=_now)

    # decay state
    half_life_sec: float = 300.0
    weight0: float = 1.0
    current_weight: float = 1.0

    # reconsideration locks
    reconsideration_count: int = 0
    last_reconsidered_at: Optional[float] = None

    def age_sec(self, now: Optional[float] = None) -> float:
        t = _now() if now is None else now
        return max(0.0, t - self.created_at)

    def update_weight(self, now: Optional[float] = None) -> None:
        t = _now() if now is None else now
        dt = max(0.0, t - self.created_at)
        # weight(t) = weight0 * 2^(-t/h)
        if self.half_life_sec <= 0:
            self.current_weight = 0.0
            return
        self.current_weight = self.weight0 * (2.0 ** (-dt / self.half_life_sec))


# =========================
# Config
# =========================

@dataclass(frozen=True)
class ResidueConfig:
    # Reservoir caps
    max_items: int = 5_000
    max_bytes: int = 2_000_000   # approximate cap (very rough)
    epsilon_purge: float = 1e-3

    # Snippet policy
    store_snippet: bool = True
    max_snippet_chars: int = 180

    # Commit thresholds by mode (Phi in [0,1])
    tau_by_mode: Dict[IntakeMode, float] = field(default_factory=lambda: {
        IntakeMode.EXPLORE: 0.35,
        IntakeMode.COMMIT: 0.55,
        IntakeMode.AUDIT: 0.85,
    })

    # TTL by mode
    ttl_by_mode_sec: Dict[IntakeMode, int] = field(default_factory=lambda: {
        IntakeMode.EXPLORE: 900,   # 15 min
        IntakeMode.COMMIT:  3600,  # 1 hr
        IntakeMode.AUDIT:   7200,  # 2 hr
    })

    # Half-lives by reason code (seconds)
    base_half_life_sec: Dict[ReasonCode, int] = field(default_factory=lambda: {
        ReasonCode.UNSAFE_POLICY: 30,
        ReasonCode.REDUNDANT: 60,
        ReasonCode.OUT_OF_SCOPE: 60,
        ReasonCode.LOW_EVIDENCE: 120,
        ReasonCode.FORMAT_NOISE: 120,
        ReasonCode.DUPLICATE_IN_DOC: 120,
        ReasonCode.LOW_SALIENCE: 300,
        ReasonCode.TOO_SPECIFIC: 300,
        ReasonCode.TOO_VAGUE: 300,
        ReasonCode.CONFLICTS_WITH_CONSTRAINT: 600,
        ReasonCode.RATE_LIMITED: 1800,
        ReasonCode.UNKNOWN: 300,
    })

    # Reconsideration locks
    max_reconsiderations: int = 2
    reconsideration_cooldown_sec: int = 300
    allowed_triggers: Tuple[ReconsiderationTrigger, ...] = (
        ReconsiderationTrigger.HUMAN_REQUEST,
        ReconsiderationTrigger.CONTEXT_SCOPE_EXPANDED,
        ReconsiderationTrigger.CONSTRAINT_CHANGED,
        ReconsiderationTrigger.RATE_LIMITED_RETRY,
    )

    # Non-binding firewall
    forbid_content_search: bool = True  # Enforces "no RAG" — no content-based retrieval API surface


# =========================
# Half-life aggregation (weighted harmonic mean)
# =========================

def choose_half_life_sec(
    reasons: List[Tuple[ReasonCode, float]],
    base_half_life_sec: Dict[ReasonCode, int],
    default_half_life_sec: float = 300.0
) -> float:
    if not reasons:
        return float(default_half_life_sec)

    # Weighted harmonic mean: h = sum(w) / sum(w / h_i)
    numer = 0.0
    denom = 0.0
    for code, w in reasons:
        weight = max(0.0, float(w))
        if weight == 0.0:
            continue
        h_i = float(base_half_life_sec.get(code, int(default_half_life_sec)))
        h_i = max(1.0, h_i)
        numer += weight
        denom += weight / h_i
    if denom <= 0.0:
        return float(default_half_life_sec)
    return max(1.0, numer / denom)


# =========================
# Pressure Field (diagnostic only)
# =========================

@dataclass
class PressureField:
    """
    Homeostatic diagnostic signal.
    MUST NOT influence commit decisions unless explicitly wired in elsewhere.
    """
    leak_lambda: float = 0.05  # per second-ish; tune to taste (small)
    p_constraint: float = 0.0
    p_budget: float = 0.0
    p_extraction: float = 0.0
    last_tick_at: float = field(default_factory=_now)

    T1_warning: float = 5.0
    T2_critical: float = 10.0

    def tick(self, now: Optional[float] = None) -> None:
        t = _now() if now is None else now
        dt = max(0.0, t - self.last_tick_at)
        self.last_tick_at = t
        # Exponential decay toward 0
        decay = math.exp(-self.leak_lambda * dt) if dt > 0 else 1.0
        self.p_constraint *= decay
        self.p_budget *= decay
        self.p_extraction *= decay

    def observe_reasons(self, reasons: List[Tuple[ReasonCode, float]], now: Optional[float] = None) -> None:
        self.tick(now=now)
        # Accumulate based on dominating rejection pattern
        weight_by = {code: w for code, w in reasons}
        conflict = weight_by.get(ReasonCode.CONFLICTS_WITH_CONSTRAINT, 0.0)
        rate = weight_by.get(ReasonCode.RATE_LIMITED, 0.0)
        low_e = weight_by.get(ReasonCode.LOW_EVIDENCE, 0.0) + weight_by.get(ReasonCode.FORMAT_NOISE, 0.0)

        # Small increments; adjust α/β/γ as needed.
        self.p_constraint += 1.0 * float(conflict)
        self.p_budget += 1.0 * float(rate)
        self.p_extraction += 1.0 * float(low_e)

    def alert_level(self) -> str:
        m = max(self.p_constraint, self.p_budget, self.p_extraction)
        if m >= self.T2_critical:
            return "CRITICAL"
        if m >= self.T1_warning:
            return "WARNING"
        return "NOMINAL"


# =========================
# Reservoir
# =========================

@dataclass
class ResidueSummary:
    total_items: int
    total_docs: int
    reason_histogram: Dict[ReasonCode, int]
    avg_phi: float
    near_miss_count: int
    alert_level: str


class ResidueReservoir:
    """
    Bounded TTL store for residue traces.
    NON-BINDING by contract:
      - no content-based retrieval surface
      - TTL + cap enforced
      - decay tick purges aggressively
    """

    def __init__(self, config: ResidueConfig):
        self.cfg = config
        self._by_id: Dict[str, ResidueRecord] = {}
        self._by_hash: Dict[str, str] = {}  # candidate_hash -> residue_id
        self._by_doc: Dict[str, List[str]] = {}  # doc_id -> [residue_id]
        self._approx_bytes: int = 0
        self.pressure = PressureField()

    # ---------- Non-binding firewall ----------
    def find_by_content(self, _query: str) -> List[ResidueRecord]:
        if self.cfg.forbid_content_search:
            raise RuntimeError("Forbidden: residue store is non-binding and cannot be searched by content.")
        return []

    # ---------- Core operations ----------
    def record(
        self,
        candidate: Candidate,
        scores: ScoreBreakdown,
        reasons: List[Tuple[ReasonCode, float]],
        context: ResidueContext,
        residue_id: Optional[str] = None,
        now: Optional[float] = None
    ) -> ResidueRecord:
        t = _now() if now is None else now

        rid = residue_id or sha256_hex(f"{candidate.doc_id}:{candidate.content_hash}:{t}")
        snippet = None
        if self.cfg.store_snippet:
            s = candidate.content.strip()
            snippet = (s[: self.cfg.max_snippet_chars] + "…") if len(s) > self.cfg.max_snippet_chars else s

        h = choose_half_life_sec(reasons, self.cfg.base_half_life_sec)

        rec = ResidueRecord(
            residue_id=rid,
            doc_id=candidate.doc_id,
            candidate_hash=candidate.content_hash,
            candidate_type=candidate.type,
            snippet=snippet,
            scores=scores,
            reasons=reasons[:],
            context=context,
            created_at=t,
            last_seen_at=t,
            half_life_sec=h,
            weight0=1.0,
            current_weight=1.0,
        )

        # If same hash exists, update it (refresh last_seen, bump counters)
        existing_id = self._by_hash.get(rec.candidate_hash)
        if existing_id and existing_id in self._by_id:
            old = self._by_id[existing_id]
            old.last_seen_at = t
            old.reasons = rec.reasons
            old.scores = rec.scores
            old.half_life_sec = rec.half_life_sec
            old.update_weight(t)
            # Pressure observes patterns (diagnostic only)
            self.pressure.observe_reasons(rec.reasons, now=t)
            return old

        # New insert
        self._insert(rec)
        self.pressure.observe_reasons(rec.reasons, now=t)
        self.decay_tick(now=t)  # enforce caps/TTL early
        return rec

    def _insert(self, rec: ResidueRecord) -> None:
        self._by_id[rec.residue_id] = rec
        self._by_hash[rec.candidate_hash] = rec.residue_id
        self._by_doc.setdefault(rec.doc_id, []).append(rec.residue_id)
        self._approx_bytes += self._estimate_bytes(rec)

    def _estimate_bytes(self, rec: ResidueRecord) -> int:
        # rough accounting; good enough for cap protection
        base = 200
        snippet_bytes = len(rec.snippet.encode("utf-8")) if rec.snippet else 0
        reasons_bytes = 40 * len(rec.reasons)
        return base + snippet_bytes + reasons_bytes

    def get(self, residue_id: str) -> Optional[ResidueRecord]:
        return self._by_id.get(residue_id)

    def items_for_doc(self, doc_id: str) -> List[ResidueRecord]:
        ids = self._by_doc.get(doc_id, [])
        return [self._by_id[i] for i in ids if i in self._by_id]

    def decay_tick(self, now: Optional[float] = None) -> None:
        t = _now() if now is None else now

        # Pressure tick (diagnostic)
        self.pressure.tick(now=t)

        # TTL per mode can vary; compute per record
        purge_ids: List[str] = []
        for rid, rec in list(self._by_id.items()):
            ttl = int(self.cfg.ttl_by_mode_sec.get(rec.context.intake_mode, 3600))
            rec.update_weight(t)

            if rec.current_weight < self.cfg.epsilon_purge:
                purge_ids.append(rid)
                continue
            if (t - rec.created_at) > ttl:
                purge_ids.append(rid)
                continue

        for rid in purge_ids:
            self._purge(rid)

        # Enforce caps (items + approx bytes)
        self._enforce_caps()

    def _enforce_caps(self) -> None:
        # If within caps, done
        if len(self._by_id) <= self.cfg.max_items and self._approx_bytes <= self.cfg.max_bytes:
            return

        # Purge oldest/lowest weight first
        recs = list(self._by_id.values())
        recs.sort(key=lambda r: (r.current_weight, r.created_at))  # lowest weight first
        while (len(self._by_id) > self.cfg.max_items) or (self._approx_bytes > self.cfg.max_bytes):
            if not recs:
                break
            victim = recs.pop(0)
            self._purge(victim.residue_id)

    def _purge(self, residue_id: str) -> None:
        rec = self._by_id.pop(residue_id, None)
        if not rec:
            return
        # indexes
        if self._by_hash.get(rec.candidate_hash) == residue_id:
            self._by_hash.pop(rec.candidate_hash, None)
        ids = self._by_doc.get(rec.doc_id)
        if ids:
            try:
                ids.remove(residue_id)
            except ValueError:
                pass
            if not ids:
                self._by_doc.pop(rec.doc_id, None)
        self._approx_bytes = max(0, self._approx_bytes - self._estimate_bytes(rec))

    # ---------- Reconsideration (controlled) ----------
    def eligible_for_reconsideration(
        self,
        rec: ResidueRecord,
        trigger: ReconsiderationTrigger,
        now: Optional[float] = None
    ) -> bool:
        t = _now() if now is None else now
        if trigger not in self.cfg.allowed_triggers:
            return False
        if rec.reconsideration_count >= self.cfg.max_reconsiderations:
            return False
        if rec.last_reconsidered_at is not None:
            if (t - rec.last_reconsidered_at) < self.cfg.reconsideration_cooldown_sec:
                return False
        # Must still be alive in reservoir (TTL/caps)
        if rec.residue_id not in self._by_id:
            return False
        # If UNSAFE_POLICY is among reasons, we generally should not reconsider
        for code, _w in rec.reasons:
            if code == ReasonCode.UNSAFE_POLICY:
                return False
        return True

    def mark_reconsidered(self, residue_id: str, now: Optional[float] = None) -> None:
        t = _now() if now is None else now
        rec = self._by_id.get(residue_id)
        if not rec:
            return
        rec.reconsideration_count += 1
        rec.last_reconsidered_at = t
        if rec.reconsideration_count >= self.cfg.max_reconsiderations:
            # Hard cap: purge to prevent implicit retrieval loops
            self._purge(residue_id)

    # ---------- Metrics ----------
    def summary(self, near_miss_delta: float = 0.05) -> ResidueSummary:
        total = len(self._by_id)
        docs = len(self._by_doc)
        hist: Dict[ReasonCode, int] = {}
        phi_sum = 0.0
        near_miss = 0
        for rec in self._by_id.values():
            phi_sum += rec.scores.Phi
            tau = self.cfg.tau_by_mode.get(rec.context.intake_mode, 0.55)
            if (tau - near_miss_delta) <= rec.scores.Phi < tau:
                near_miss += 1
            # count dominant reason (first reason)
            if rec.reasons:
                dom = rec.reasons[0][0]
            else:
                dom = ReasonCode.UNKNOWN
            hist[dom] = hist.get(dom, 0) + 1
        avg_phi = (phi_sum / total) if total else 0.0
        return ResidueSummary(
            total_items=total,
            total_docs=docs,
            reason_histogram=hist,
            avg_phi=avg_phi,
            near_miss_count=near_miss,
            alert_level=self.pressure.alert_level(),
        )


# =========================
# Standalone intake utility
# =========================

@dataclass
class IntakeDecision:
    committed: bool
    tau: float
    scores: ScoreBreakdown


def decide_commit(scores: ScoreBreakdown, mode: IntakeMode, cfg: ResidueConfig) -> IntakeDecision:
    tau = float(cfg.tau_by_mode.get(mode, 0.55))
    return IntakeDecision(committed=(scores.Phi >= tau), tau=tau, scores=scores)


# =========================
# Minimal test harness (unittest)
# =========================

def _scale_invariance_phi_demo():
    # Demonstrates that scaling cost terms doesn't explode Phi if U is fixed and costs scale similarly.
    # (Phi will change if costs change; the point is interpretability and boundedness, not invariance to arbitrary changes.)
    s1 = ScoreBreakdown.compute(U_raw=1.0, K_raw=1.0, D_raw=1.0, E_raw=1.0)
    s2 = ScoreBreakdown.compute(U_raw=1.0, K_raw=10.0, D_raw=10.0, E_raw=10.0)
    return s1.Phi, s2.Phi


if __name__ == "__main__":
    # Example usage: record residue for rejected candidates
    cfg = ResidueConfig()
    reservoir = ResidueReservoir(cfg)

    ctx = ResidueContext(project="P1", task_signature="demo", intake_mode=IntakeMode.COMMIT)

    # Fake "scoring" — you’d wire your real functions here:
    c1 = Candidate(id="c1", type=CandidateType.CLAIM, content="The system should never store discarded text fully.", doc_id="docA")
    scores1 = ScoreBreakdown.compute(U_raw=0.4, K_raw=0.2, D_raw=0.5, E_raw=0.1)  # Phi computed inside
    decision1 = decide_commit(scores1, ctx.intake_mode, cfg)

    if not decision1.committed:
        reservoir.record(
            candidate=c1,
            scores=scores1,
            reasons=[(ReasonCode.CONFLICTS_WITH_CONSTRAINT, 0.7), (ReasonCode.LOW_SALIENCE, 0.3)],
            context=ctx,
        )

    c2 = Candidate(id="c2", type=CandidateType.PROCEDURE, content="Add a search API over residue so it can answer questions.", doc_id="docA")
    scores2 = ScoreBreakdown.compute(U_raw=0.7, K_raw=0.1, D_raw=0.0, E_raw=0.8)
    decision2 = decide_commit(scores2, ctx.intake_mode, cfg)

    if not decision2.committed:
        reservoir.record(
            candidate=c2,
            scores=scores2,
            reasons=[(ReasonCode.UNSAFE_POLICY, 1.0)],  # treat "turn residue into memory" as forbidden
            context=ctx,
        )

    reservoir.decay_tick()
    print("Residue summary:", reservoir.summary())

    # Non-binding firewall demo:
    try:
        reservoir.find_by_content("store discarded")
    except RuntimeError as e:
        print("Expected firewall:", e)

    # Divisive normalization sanity:
    phi1, phi2 = _scale_invariance_phi_demo()
    print("Phi demo:", phi1, phi2)
