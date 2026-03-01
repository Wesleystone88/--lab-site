"""
glyph_registry.py
==================
Python equivalent of glyph-system/ (TypeScript).

Mirrors the exact schemas from:
  glyph-system/types.ts
  glyph-system/schemas/glyph.schema.ts
  glyph-system/schemas/card.schema.ts
  glyph-system/glyphs.ts
  glyph-system/cards.ts
  glyph-system/bootstrap.ts

Purpose:
  DomainLoader reads from this registry to auto-configure domain profiles.
  You add glyphs and cards here — domain loader picks them up automatically.
  No full stack needed. Add rules, fiddle, iterate.

File layout (mirrors glyph-system/):
  glyph_registry.py          ← this file (types + registry + bootstrap)
  glyphs/                    ← optional: load from JSON files
      g-medical-policy.json
      g-legal-contract.json
      ...
  cards/                     ← optional: load from JSON files
      card-medical-review.json
      card-legal-check.json
      ...

Authority rules (same as TS):
  IMMUTABLE : id, authority, type, activation
  EDITABLE  : md, tags
  RESTRICTED: validation.rules (requires explicit unlock)
  NEW VERSION: any immutable change → new id with bumped semver
"""

import re
import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum


# ─────────────────────────────────────────────────────────────
# TYPES — mirrors types.ts exactly
# ─────────────────────────────────────────────────────────────

GLYPH_ID_PATTERN = re.compile(r'^g-[\w-]+@\d+\.\d+\.\d+$')

class GlyphType(str, Enum):
    CLAUSE     = "clause"
    POLICY     = "policy"
    CONTRACT   = "contract"
    STATE      = "state"
    OBSERVER   = "observer"
    CONSTRAINT = "constraint"
    VALIDATOR  = "validator"   # used in existing glyphs.ts

class GlyphAuthority(str, Enum):
    NORMATIVE      = "normative"
    OPERATIVE      = "operative"
    OBSERVATIONAL  = "observational"


@dataclass
class GlyphActivation:
    when: str   # expression string: 'tags.includes("multi-step")'


@dataclass
class GlyphValidation:
    rules: List[str]   # e.g. ["patches.must_be_patch_only", "no_absolute_paths"]


@dataclass
class GlyphJson:
    type:       str                          # GlyphType value
    authority:  str                          # GlyphAuthority value
    activation: Optional[GlyphActivation]   = None
    depends_on: List[str]                   = field(default_factory=list)
    validation: Optional[GlyphValidation]   = None

    # Domain loader extension fields
    # These are NOT in the original TS schema — we extend here
    # without breaking compatibility (extra fields are ignored by TS)
    domain:             Optional[str]   = None   # "medical" | "legal" | etc.
    pfc_overrides:      Optional[dict]  = None   # partial PFCConfig overrides
    metacog_overrides:  Optional[dict]  = None   # partial MetacogConfig overrides
    tfe_tau:            Optional[float] = None
    cme_explore_rate:   Optional[float] = None
    cme_reinforce_gain: Optional[float] = None
    biorag_confidence_max: Optional[float] = None


@dataclass
class GlyphEditability:
    can_edit_md:    bool = True
    can_edit_tags:  bool = True
    can_edit_rules: bool = False   # requires PIN:ALLOW_CONTRACT_EDIT
    can_edit_json:  bool = False


@dataclass
class Glyph:
    """
    Python equivalent of Glyph type from types.ts.

    id      : g-{name}@{major}.{minor}.{patch}  — IMMUTABLE
    title   : human-readable name
    md      : markdown description (EDITABLE)
    json    : machine constraints (RESTRICTED for rules)
    tags    : category labels (EDITABLE)
    editable: editability constraints
    """
    id:       str
    title:    str
    md:       str
    json:     GlyphJson
    tags:     List[str]             = field(default_factory=list)
    editable: GlyphEditability      = field(default_factory=GlyphEditability)

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate this glyph. Returns (ok, errors)."""
        errors = []
        if not GLYPH_ID_PATTERN.match(self.id):
            errors.append(f"id '{self.id}' must match g-{{name}}@{{semver}}")
        if not self.title.strip():
            errors.append("title is empty")
        if not self.md.strip():
            errors.append("md is empty")
        if self.json.type not in [e.value for e in GlyphType]:
            errors.append(f"json.type '{self.json.type}' not valid")
        if self.json.authority not in [e.value for e in GlyphAuthority]:
            errors.append(f"json.authority '{self.json.authority}' not valid")
        return len(errors) == 0, errors

    def get_domain(self) -> Optional[str]:
        """Extract domain from glyph — checks json.domain then tags."""
        if self.json.domain:
            return self.json.domain
        # Infer from tags — first tag that matches a known domain
        known = {"medical", "legal", "financial", "coding", "research", "default"}
        for tag in self.tags:
            if tag in known:
                return tag
        return None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "md": self.md,
            "json": {
                "type":       self.json.type,
                "authority":  self.json.authority,
                "activation": {"when": self.json.activation.when} if self.json.activation else None,
                "depends_on": self.json.depends_on,
                "validation": {"rules": self.json.validation.rules} if self.json.validation else None,
                "domain":     self.json.domain,
                "pfc_overrides":    self.json.pfc_overrides,
                "metacog_overrides": self.json.metacog_overrides,
                "tfe_tau":          self.json.tfe_tau,
                "cme_explore_rate": self.json.cme_explore_rate,
                "cme_reinforce_gain": self.json.cme_reinforce_gain,
                "biorag_confidence_max": self.json.biorag_confidence_max,
            },
            "tags": self.tags,
        }


@dataclass
class Card:
    """
    Python equivalent of Card type from types.ts.

    id       : unique card identifier
    title    : human-readable name
    glyph_ids: references to glyphs this card activates (1+)
    inputs   : expected input parameters
    outputs  : produced output artifacts
    metadata : optional extra info (category, priority, etc.)
    """
    id:        str
    title:     str
    glyph_ids: List[str]                        # must all match GLYPH_ID_PATTERN
    inputs:    List[str]        = field(default_factory=list)
    outputs:   List[str]        = field(default_factory=list)
    metadata:  Dict[str, Any]   = field(default_factory=dict)

    def validate(self, known_glyphs: Dict[str, Glyph]) -> Tuple[bool, List[str]]:
        """Validate this card. Returns (ok, errors)."""
        errors = []
        if not self.id.strip():
            errors.append("id is empty")
        if not self.title.strip():
            errors.append("title is empty")
        if not self.glyph_ids:
            errors.append("glyphIds must have at least one entry")
        for gid in self.glyph_ids:
            if not GLYPH_ID_PATTERN.match(gid):
                errors.append(f"glyphId '{gid}' must match g-{{name}}@{{semver}}")
            elif gid not in known_glyphs:
                errors.append(f"glyphId '{gid}' not found in registry")
        return len(errors) == 0, errors

    def get_domains(self, glyph_registry: Dict[str, "Glyph"]) -> List[str]:
        """Get all domains this card touches via its glyphs."""
        domains = set()
        for gid in self.glyph_ids:
            g = glyph_registry.get(gid)
            if g:
                d = g.get_domain()
                if d:
                    domains.add(d)
        return list(domains)

    def to_dict(self) -> dict:
        return {
            "id":       self.id,
            "title":    self.title,
            "glyphIds": self.glyph_ids,
            "inputs":   self.inputs,
            "outputs":  self.outputs,
            "metadata": self.metadata,
        }


# ─────────────────────────────────────────────────────────────
# BUILT-IN GLYPHS — mirrors glyphs.ts BUILT_IN_GLYPHS
# ─────────────────────────────────────────────────────────────
# These are the 4 core governance glyphs from the TS system
# PLUS domain-specific glyphs for the domain loader.

BUILT_IN_GLYPHS: Dict[str, Glyph] = {

    # ── Core governance (from glyphs.ts) ─────────────────────

    "g-policy@0.1.0": Glyph(
        id="g-policy@0.1.0",
        title="Patch-Only Policy",
        md=(
            "# Patch-Only Policy (g-policy@0.1.0)\n\n"
            "Enforces strict governance: **patches are the only way state changes**.\n\n"
            "## Rules\n"
            "- Mutations must be patch ops: `mkdir`, `write_file`, or `set_state`\n"
            "- No delete, rename, or filesystem escape\n"
            "- All patches require Witness approval\n\n"
            "## Authority\n- **Normative**: applies to all patches"
        ),
        json=GlyphJson(
            type="validator",
            authority="normative",
            activation=GlyphActivation(when='tags.includes("multi-step")'),
            depends_on=[],
            validation=GlyphValidation(rules=[
                "patches.must_be_patch_only",
                "patches.no_absolute_paths",
            ]),
        ),
        tags=["core", "governance"],
        editable=GlyphEditability(can_edit_rules=False),
    ),

    "g-contract@0.1.0": Glyph(
        id="g-contract@0.1.0",
        title="Execution Contract",
        md=(
            "# Execution Contract (g-contract@0.1.0)\n\n"
            "Defines the boundary between Advisor (suggestions) and Builder (commitments).\n\n"
            "## Rules\n"
            "- Advisor can propose, cannot commit\n"
            "- Builder generates patches from cards, cannot validate\n"
            "- All ops must be deterministic"
        ),
        json=GlyphJson(
            type="contract",
            authority="operative",
            activation=GlyphActivation(when='stage === "BUILDER"'),
            depends_on=["g-policy@0.1.0"],
            validation=GlyphValidation(rules=[
                "builder.deterministic_only",
                "builder.patch_ops_only",
            ]),
        ),
        tags=["core", "execution"],
    ),

    "g-observer@0.1.0": Glyph(
        id="g-observer@0.1.0",
        title="Audit Observer",
        md=(
            "# Audit Observer (g-observer@0.1.0)\n\n"
            "Traces all state changes for accountability.\n\n"
            "## Rules\n"
            "- Every patch is logged with witness verdict\n"
            "- Ledger is append-only (immutable)\n"
            "- Timestamps are ISO 8601"
        ),
        json=GlyphJson(
            type="observer",
            authority="observational",
            activation=GlyphActivation(when='stage === "SCRIBE"'),
            depends_on=["g-policy@0.1.0"],
            validation=GlyphValidation(rules=[
                "ledger.append_only",
                "ledger.iso_timestamps",
            ]),
        ),
        tags=["core", "audit"],
    ),

    "g-artifact@0.1.0": Glyph(
        id="g-artifact@0.1.0",
        title="Artifact Materialization",
        md=(
            "# Artifact Materialization (g-artifact@0.1.0)\n\n"
            "Governs how artifacts are written to VFS.\n\n"
            "## Rules\n"
            "- All artifacts are JSON files\n"
            "- Artifacts are write-once (no mutations, only new versions)"
        ),
        json=GlyphJson(
            type="constraint",
            authority="normative",
            activation=GlyphActivation(when='path.includes("artifacts")'),
            depends_on=["g-policy@0.1.0", "g-observer@0.1.0"],
            validation=GlyphValidation(rules=[
                "artifacts.json_only",
                "artifacts.write_once",
            ]),
        ),
        tags=["core", "materialization"],
    ),

    # ── Domain glyphs — activate domain profiles ─────────────

    "g-medical-policy@1.0.0": Glyph(
        id="g-medical-policy@1.0.0",
        title="Medical Domain Policy",
        md=(
            "# Medical Domain Policy (g-medical-policy@1.0.0)\n\n"
            "Activates medical governance mode in the agent.\n\n"
            "## Rules\n"
            "- Maximum caution — errors cost lives\n"
            "- Very low exploration rate on dangerous actions\n"
            "- Strong constraint memory — learned dangers persist\n"
            "- Slow temporal decay — medical history matters longer\n\n"
            "## PFC Calibration\n"
            "- novelty_slow_threshold: 0.3 (any novelty = caution)\n"
            "- uncertainty_escalate: 0.7\n"
            "- consequence_ceiling: 0.5"
        ),
        json=GlyphJson(
            type="policy",
            authority="normative",
            activation=GlyphActivation(when='domain === "medical"'),
            depends_on=["g-policy@0.1.0"],
            validation=GlyphValidation(rules=[
                "medical.no_unverified_diagnosis",
                "medical.escalate_on_uncertainty",
                "medical.preserve_patient_context",
            ]),
            domain="medical",
            tfe_tau=14400.0,
            cme_explore_rate=0.005,
            cme_reinforce_gain=0.40,
            biorag_confidence_max=0.4,
        ),
        tags=["medical", "clinical", "health", "domain"],
    ),

    "g-legal-contract@1.0.0": Glyph(
        id="g-legal-contract@1.0.0",
        title="Legal Domain Contract",
        md=(
            "# Legal Domain Contract (g-legal-contract@1.0.0)\n\n"
            "Activates legal governance mode in the agent.\n\n"
            "## Rules\n"
            "- Legal errors are expensive and hard to reverse\n"
            "- Precedents matter — strong constraint memory\n"
            "- Escalate on novel legal territory\n\n"
            "## PFC Calibration\n"
            "- novelty_slow_threshold: 0.35\n"
            "- consequence_ceiling: 0.55"
        ),
        json=GlyphJson(
            type="contract",
            authority="normative",
            activation=GlyphActivation(when='domain === "legal"'),
            depends_on=["g-policy@0.1.0", "g-contract@0.1.0"],
            validation=GlyphValidation(rules=[
                "legal.cite_precedent",
                "legal.escalate_liability_risk",
                "legal.no_unauthorized_commitments",
            ]),
            domain="legal",
            tfe_tau=7200.0,
            cme_explore_rate=0.01,
            cme_reinforce_gain=0.35,
            biorag_confidence_max=0.45,
        ),
        tags=["legal", "compliance", "contract", "regulation", "domain"],
    ),

    "g-coding-rules@1.0.0": Glyph(
        id="g-coding-rules@1.0.0",
        title="Coding Domain Rules",
        md=(
            "# Coding Domain Rules (g-coding-rules@1.0.0)\n\n"
            "Activates software development governance mode.\n\n"
            "## Rules\n"
            "- Mistakes are recoverable — higher exploration tolerance\n"
            "- Recent patterns matter most — fast temporal decay\n"
            "- Episode recall is valuable in coding contexts\n\n"
            "## PFC Calibration\n"
            "- novelty_slow_threshold: 0.7\n"
            "- consequence_ceiling: 0.85"
        ),
        json=GlyphJson(
            type="policy",
            authority="operative",
            activation=GlyphActivation(when='domain === "coding"'),
            depends_on=["g-policy@0.1.0"],
            validation=GlyphValidation(rules=[
                "coding.prefer_reversible_ops",
                "coding.test_before_commit",
            ]),
            domain="coding",
            tfe_tau=1800.0,
            cme_explore_rate=0.05,
            cme_reinforce_gain=0.20,
            biorag_confidence_max=0.6,
        ),
        tags=["coding", "software", "development", "engineering", "domain"],
    ),

    "g-financial-risk@1.0.0": Glyph(
        id="g-financial-risk@1.0.0",
        title="Financial Risk Policy",
        md=(
            "# Financial Risk Policy (g-financial-risk@1.0.0)\n\n"
            "Activates financial governance mode.\n\n"
            "## Rules\n"
            "- Risk management rules must be respected\n"
            "- Market conditions shift — moderate temporal decay\n"
            "- Escalate on high-consequence financial decisions"
        ),
        json=GlyphJson(
            type="policy",
            authority="normative",
            activation=GlyphActivation(when='domain === "financial"'),
            depends_on=["g-policy@0.1.0"],
            validation=GlyphValidation(rules=[
                "financial.respect_risk_limits",
                "financial.log_all_transactions",
            ]),
            domain="financial",
            tfe_tau=3600.0,
            cme_explore_rate=0.015,
            cme_reinforce_gain=0.30,
            biorag_confidence_max=0.5,
        ),
        tags=["financial", "finance", "markets", "risk", "domain"],
    ),
}


# ─────────────────────────────────────────────────────────────
# BUILT-IN CARDS — mirrors cards.ts SAMPLE_CARDS
# ─────────────────────────────────────────────────────────────

BUILT_IN_CARDS: Dict[str, Card] = {

    # ── Core governance cards (from cards.ts) ────────────────

    "card-init-workspace": Card(
        id="card-init-workspace",
        title="Initialize Workspace",
        glyph_ids=["g-policy@0.1.0", "g-observer@0.1.0"],
        inputs=[],
        outputs=["workspace-initialized"],
        metadata={"category": "bootstrap", "priority": 1},
    ),

    "card-materialize-glyphs": Card(
        id="card-materialize-glyphs",
        title="Materialize Glyphs to VFS",
        glyph_ids=["g-policy@0.1.0", "g-artifact@0.1.0"],
        inputs=[],
        outputs=["glyphs-materialized"],
        metadata={"category": "bootstrap", "priority": 2},
    ),

    "card-validate-patch": Card(
        id="card-validate-patch",
        title="Validate Incoming Patch",
        glyph_ids=["g-contract@0.1.0", "g-observer@0.1.0"],
        inputs=["patch"],
        outputs=["patch-validated"],
        metadata={"category": "governance"},
    ),

    "card-snapshot": Card(
        id="card-snapshot",
        title="Capture State Snapshot",
        glyph_ids=["g-observer@0.1.0"],
        inputs=[],
        outputs=["snapshot-created"],
        metadata={"category": "audit"},
    ),

    # ── Domain activation cards ───────────────────────────────

    "card-activate-medical": Card(
        id="card-activate-medical",
        title="Activate Medical Domain",
        glyph_ids=["g-medical-policy@1.0.0", "g-observer@0.1.0"],
        inputs=["patient_context"],
        outputs=["domain-medical-active", "pfc-calibrated"],
        metadata={"category": "domain", "domain": "medical", "priority": 1},
    ),

    "card-activate-legal": Card(
        id="card-activate-legal",
        title="Activate Legal Domain",
        glyph_ids=["g-legal-contract@1.0.0", "g-observer@0.1.0"],
        inputs=["case_context"],
        outputs=["domain-legal-active", "pfc-calibrated"],
        metadata={"category": "domain", "domain": "legal", "priority": 1},
    ),

    "card-activate-coding": Card(
        id="card-activate-coding",
        title="Activate Coding Domain",
        glyph_ids=["g-coding-rules@1.0.0"],
        inputs=["project_context"],
        outputs=["domain-coding-active"],
        metadata={"category": "domain", "domain": "coding", "priority": 1},
    ),

    "card-activate-financial": Card(
        id="card-activate-financial",
        title="Activate Financial Domain",
        glyph_ids=["g-financial-risk@1.0.0", "g-observer@0.1.0"],
        inputs=["market_context"],
        outputs=["domain-financial-active", "pfc-calibrated"],
        metadata={"category": "domain", "domain": "financial", "priority": 1},
    ),

    # ── Agent-specific cards ──────────────────────────────────

    "card-escalate-to-human": Card(
        id="card-escalate-to-human",
        title="Escalate Decision to Human",
        glyph_ids=["g-contract@0.1.0", "g-observer@0.1.0"],
        inputs=["pfc_signal", "context", "action"],
        outputs=["human-decision", "escalation-logged"],
        metadata={"category": "oversight", "triggers": "PFCVerdict.ESCALATE"},
    ),

    "card-domain-transition": Card(
        id="card-domain-transition",
        title="Record Domain Transition",
        glyph_ids=["g-observer@0.1.0", "g-artifact@0.1.0"],
        inputs=["from_domain", "to_domain", "glyph_activated"],
        outputs=["transition-card-written"],
        metadata={"category": "audit", "noesis_card_type": "domain_transition"},
    ),

    "card-metacog-adjustment": Card(
        id="card-metacog-adjustment",
        title="Record Metacognitive Trust Adjustment",
        glyph_ids=["g-observer@0.1.0"],
        inputs=["pillar_name", "old_trust", "new_trust", "reason"],
        outputs=["adjustment-logged"],
        metadata={"category": "audit", "noesis_card_type": "evidence"},
    ),
}


# ─────────────────────────────────────────────────────────────
# GLYPH REGISTRY — the live store
# ─────────────────────────────────────────────────────────────

class GlyphRegistry:
    """
    Live registry of glyphs and cards.
    Mirrors bootstrap.ts bootstrapGlyphSystem() behavior.

    Eager loading: all glyphs and cards validated at startup.
    Self-healing: load errors are logged, not fatal.
    Extensible: register new glyphs/cards at runtime or from JSON files.
    """

    def __init__(self):
        self._glyphs: Dict[str, Glyph] = {}
        self._cards:  Dict[str, Card]  = {}
        self._errors: List[str]        = []

    # ── Bootstrap ─────────────────────────────────────────────

    def bootstrap(self) -> dict:
        """
        Load and validate all built-in glyphs and cards.
        Returns a BootstrapReport dict (mirrors bootstrap.ts).

        Call once at startup.
        """
        report = {
            "ok": True,
            "glyphs_loaded": 0,
            "glyph_errors":  [],
            "cards_loaded":  0,
            "card_errors":   [],
            "details":       "",
        }

        # Load glyphs
        for glyph_id, glyph in BUILT_IN_GLYPHS.items():
            ok, errors = glyph.validate()
            if ok:
                self._glyphs[glyph_id] = glyph
                report["glyphs_loaded"] += 1
            else:
                report["ok"] = False
                for e in errors:
                    msg = f"Glyph {glyph_id}: {e}"
                    report["glyph_errors"].append(msg)
                    self._errors.append(msg)

        # Load cards
        for card_id, card in BUILT_IN_CARDS.items():
            ok, errors = card.validate(self._glyphs)
            if ok:
                self._cards[card_id] = card
                report["cards_loaded"] += 1
            else:
                report["ok"] = False
                for e in errors:
                    msg = f"Card {card_id}: {e}"
                    report["card_errors"].append(msg)
                    self._errors.append(msg)

        report["details"] = (
            f"Glyphs: {report['glyphs_loaded']} loaded, "
            f"{len(report['glyph_errors'])} errors | "
            f"Cards: {report['cards_loaded']} loaded, "
            f"{len(report['card_errors'])} errors"
        )
        return report

    def bootstrap_from_directory(self, path: str) -> dict:
        """
        Load additional glyphs and cards from a directory of JSON files.

        Directory layout:
            path/
              glyphs/
                g-my-rule@1.0.0.json
              cards/
                card-my-action.json

        JSON format matches glyph.example.json and card.example.json exactly.
        """
        loaded = {"glyphs": 0, "cards": 0, "errors": []}

        glyph_dir = os.path.join(path, "glyphs")
        if os.path.isdir(glyph_dir):
            for fname in os.listdir(glyph_dir):
                if fname.endswith(".json"):
                    fpath = os.path.join(glyph_dir, fname)
                    try:
                        glyph = self._load_glyph_from_file(fpath)
                        ok, errors = glyph.validate()
                        if ok:
                            self._glyphs[glyph.id] = glyph
                            loaded["glyphs"] += 1
                        else:
                            loaded["errors"].extend(errors)
                    except Exception as e:
                        loaded["errors"].append(f"{fname}: {e}")

        card_dir = os.path.join(path, "cards")
        if os.path.isdir(card_dir):
            for fname in os.listdir(card_dir):
                if fname.endswith(".json"):
                    fpath = os.path.join(card_dir, fname)
                    try:
                        card = self._load_card_from_file(fpath)
                        ok, errors = card.validate(self._glyphs)
                        if ok:
                            self._cards[card.id] = card
                            loaded["cards"] += 1
                        else:
                            loaded["errors"].extend(errors)
                    except Exception as e:
                        loaded["errors"].append(f"{fname}: {e}")

        return loaded

    # ── Glyph access ──────────────────────────────────────────

    def get_glyph(self, glyph_id: str) -> Optional[Glyph]:
        return self._glyphs.get(glyph_id)

    def get_glyphs_by_domain(self, domain: str) -> List[Glyph]:
        return [g for g in self._glyphs.values() if g.get_domain() == domain]

    def get_glyphs_by_tag(self, tag: str) -> List[Glyph]:
        return [g for g in self._glyphs.values() if tag in g.tags]

    def get_all_glyphs(self) -> Dict[str, Glyph]:
        return dict(self._glyphs)

    def register_glyph(self, glyph: Glyph) -> Tuple[bool, List[str]]:
        """Register a new glyph at runtime. Returns (ok, errors)."""
        ok, errors = glyph.validate()
        if ok:
            self._glyphs[glyph.id] = glyph
        return ok, errors

    # ── Card access ───────────────────────────────────────────

    def get_card(self, card_id: str) -> Optional[Card]:
        return self._cards.get(card_id)

    def get_cards_by_domain(self, domain: str) -> List[Card]:
        return [c for c in self._cards.values()
                if domain in c.get_domains(self._glyphs)]

    def get_cards_by_glyph(self, glyph_id: str) -> List[Card]:
        return [c for c in self._cards.values() if glyph_id in c.glyph_ids]

    def get_all_cards(self) -> Dict[str, Card]:
        return dict(self._cards)

    def register_card(self, card: Card) -> Tuple[bool, List[str]]:
        """Register a new card at runtime. Returns (ok, errors)."""
        ok, errors = card.validate(self._glyphs)
        if ok:
            self._cards[card.id] = card
        return ok, errors

    # ── Domain extraction ─────────────────────────────────────

    def get_domain_glyphs(self) -> Dict[str, List[Glyph]]:
        """Returns {domain: [glyphs]} for all domain-tagged glyphs."""
        result: Dict[str, List[Glyph]] = {}
        for g in self._glyphs.values():
            d = g.get_domain()
            if d:
                result.setdefault(d, []).append(g)
        return result

    def extract_domain_overrides(self, domain: str) -> dict:
        """
        Read all glyphs for a domain and collect their parameter overrides.
        Used by DomainLoader to build profiles from glyphs dynamically.

        Returns merged overrides dict — last writer wins per field.
        """
        overrides = {}
        for glyph in self.get_glyphs_by_domain(domain):
            j = glyph.json
            if j.tfe_tau is not None:
                overrides["tfe_tau"] = j.tfe_tau
            if j.cme_explore_rate is not None:
                overrides["cme_explore_rate"] = j.cme_explore_rate
            if j.cme_reinforce_gain is not None:
                overrides["cme_reinforce_gain"] = j.cme_reinforce_gain
            if j.biorag_confidence_max is not None:
                overrides["biorag_confidence_max"] = j.biorag_confidence_max
            if j.pfc_overrides:
                overrides.setdefault("pfc_overrides", {}).update(j.pfc_overrides)
            if j.metacog_overrides:
                overrides.setdefault("metacog_overrides", {}).update(j.metacog_overrides)
        return overrides

    # ── File I/O ──────────────────────────────────────────────

    def _load_glyph_from_file(self, path: str) -> Glyph:
        with open(path) as f:
            data = json.load(f)
        j = data.get("json", data.get("envelope", {}))
        return Glyph(
            id=data["id"],
            title=data["title"],
            md=data.get("md", data.get("markdown", "")),
            json=GlyphJson(
                type=j.get("type", "policy"),
                authority=j.get("authority", "normative"),
                activation=GlyphActivation(j["activation"]["when"])
                           if j.get("activation") else None,
                depends_on=j.get("depends_on", []),
                validation=GlyphValidation(j["validation"]["rules"])
                           if j.get("validation") else None,
                domain=j.get("domain"),
                pfc_overrides=j.get("pfc_overrides"),
                metacog_overrides=j.get("metacog_overrides"),
                tfe_tau=j.get("tfe_tau"),
                cme_explore_rate=j.get("cme_explore_rate"),
                cme_reinforce_gain=j.get("cme_reinforce_gain"),
                biorag_confidence_max=j.get("biorag_confidence_max"),
            ),
            tags=data.get("tags", []),
        )

    def _load_card_from_file(self, path: str) -> Card:
        with open(path) as f:
            data = json.load(f)
        return Card(
            id=data["id"],
            title=data["title"],
            glyph_ids=data.get("glyphIds", data.get("glyph_ids", [])),
            inputs=data.get("inputs", []),
            outputs=data.get("outputs", []),
            metadata=data.get("metadata", {}),
        )

    def export_glyph_to_file(self, glyph_id: str, path: str) -> None:
        """Export a glyph to JSON file (for sharing with Witch Bridge)."""
        glyph = self._glyphs.get(glyph_id)
        if not glyph:
            raise KeyError(f"Glyph {glyph_id} not found")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(glyph.to_dict(), f, indent=2)

    def export_card_to_file(self, card_id: str, path: str) -> None:
        """Export a card to JSON file."""
        card = self._cards.get(card_id)
        if not card:
            raise KeyError(f"Card {card_id} not found")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(card.to_dict(), f, indent=2)

    # ── Diagnostics ───────────────────────────────────────────

    def get_stats(self) -> dict:
        domain_map = self.get_domain_glyphs()
        return {
            "glyphs_total":      len(self._glyphs),
            "cards_total":       len(self._cards),
            "domains_covered":   list(domain_map.keys()),
            "glyphs_per_domain": {d: len(gs) for d, gs in domain_map.items()},
            "errors":            self._errors,
        }


# ─────────────────────────────────────────────────────────────
# SINGLETON — one registry for the whole process
# ─────────────────────────────────────────────────────────────

_REGISTRY: Optional[GlyphRegistry] = None

def get_registry() -> GlyphRegistry:
    """Get or create the global registry singleton."""
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = GlyphRegistry()
        _REGISTRY.bootstrap()
    return _REGISTRY

def bootstrap_registry(extra_path: Optional[str] = None) -> dict:
    """
    Bootstrap the global registry.
    Call once at app startup — mirrors bootstrapGlyphSystem() from TS.

    Args:
        extra_path: optional directory of custom glyphs/cards to load after built-ins
    """
    global _REGISTRY
    _REGISTRY = GlyphRegistry()
    report = _REGISTRY.bootstrap()
    if extra_path:
        extra = _REGISTRY.bootstrap_from_directory(extra_path)
        report["extra_glyphs"] = extra["glyphs"]
        report["extra_cards"]  = extra["cards"]
        report["extra_errors"] = extra["errors"]
    return report
