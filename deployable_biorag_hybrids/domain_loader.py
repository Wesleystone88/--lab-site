"""
Domain Loader — Stem Cell Differentiation Engine
==================================================
The mechanism that makes QuintBioRAGAgent domain-adaptive.

Core principle:
  Same base substrate. Domain is just the load signal.
  The agent differentiates like a stem cell —
  reads the environment signal and becomes what the context requires.

What changes on domain load:
  ✓ PFC thresholds     (how cautious the impulse control is)
  ✓ Metacog thresholds (how fast pillar trust adjusts)
  ✓ TFE tau            (how fast temporal decay runs — medical=slower, coding=faster)
  ✓ CME parameters     (how aggressively constraints are enforced)
  ✓ BioRAG confidence  (how much episodic memory influences decisions)
  ✓ Domain tag         (stamped on every decision for Pillar 7 readiness)

What NEVER changes on domain load:
  ✗ Bandit posteriors  (learned action preferences survive)
  ✗ CME rule memory    (learned constraints survive)
  ✗ BioRAG hippocampus (episodic memory survives)
  ✗ Metacog trust      (pillar trust scores survive, unless hard_reset=True)

This is the key insight:
  The brain's KNOWLEDGE persists.
  The brain's GOVERNANCE ENVELOPE changes.

  Like a doctor becoming a legal consultant —
  their medical knowledge doesn't vanish.
  They just apply a different frame of authority to it.

Glyph integration:
  Glyphs are the domain signal source (from Witch Bridge).
  Each glyph carries domain tags in its json.
  DomainLoader reads those tags and selects the matching DomainProfile.
  Witness gate approval IS the differentiation trigger.

  Flow:
    Witness approves domain glyph patch
        ↓
    Witch Bridge calls agent.load_domain("medical")
        ↓
    DomainLoader.activate("medical", agent)
        ↓
    Agent is now operating in medical governance mode
        ↓
    NoesisCards CARD_001 records the domain transition
"""

import time
from dataclasses import dataclass, field
from typing import Dict, Optional, Any, List
from collections import deque

from pfc_engine import (
    PFCConfig,
    CODING_PFC_CONFIG, MEDICAL_PFC_CONFIG,
    LEGAL_PFC_CONFIG, FINANCIAL_PFC_CONFIG,
)
from metacognitive_monitor import (
    MetacogConfig,
    CODING_METACOG_CONFIG, MEDICAL_METACOG_CONFIG,
    LEGAL_METACOG_CONFIG, FINANCIAL_METACOG_CONFIG,
)
from glyph_registry import (
    GlyphRegistry, Glyph, Card,
    get_registry, bootstrap_registry,
)


# ─────────────────────────────────────────────────────────────
# DOMAIN PROFILE — everything a domain needs to configure
# ─────────────────────────────────────────────────────────────

@dataclass
class DomainProfile:
    """
    Complete configuration for one domain.

    A domain profile is the full governance envelope —
    every parameter that changes between domains lives here.
    The agent's learned knowledge (posteriors, rules, memory) never lives here.

    Fields:
        name             : domain identifier — stamped on every decision
        display_name     : human-readable for Witch Bridge UI
        description      : what this domain governs
        glyph_tags       : which glyph tags activate this domain
        pfc_config       : PFC impulse control thresholds
        metacog_config   : metacognitive self-calibration thresholds
        tfe_tau          : temporal decay constant (seconds)
                           medical: slow decay (3600*4) — history matters longer
                           coding:  fast decay (3600*0.5) — recency matters more
        cme_explore_rate : CME constraint exploration rate
                           medical: very low (0.01) — rarely probe dangerous actions
                           coding:  higher (0.05)   — explore more freely
        cme_reinforce_gain: how strongly CME reinforces constraint memory
        biorag_confidence_max: how much BioRAG can influence decisions
                           medical: lower (0.4) — don't over-trust episodic memory
                           coding:  higher (0.6) — episode recall is more reliable
        reset_context_memory: wipe PFC novelty history on load
                           True for radically different domains
                           False for similar domains (legal→finance)
        reset_metacog_trust: wipe metacog trust scores on load
                           True for fresh start
                           False to preserve trust earned across domains
    """
    name:                  str
    display_name:          str
    description:           str
    glyph_tags:            List[str]

    # Pillar 6 configs
    pfc_config:            PFCConfig
    metacog_config:        MetacogConfig

    # Pillar 3: TFE
    tfe_tau:               float = 3600.0   # default: 1 hour

    # Pillar 1: CME
    cme_explore_rate:      float = 0.02
    cme_reinforce_gain:    float = 0.25
    cme_decay_per_step:    float = 0.002

    # Pillar 5: BioRAG
    biorag_confidence_max: float = 0.5
    biorag_min_evidence:   int   = 3

    # Load behavior
    reset_context_memory:  bool  = False
    reset_metacog_trust:   bool  = False

    # Pillar 7 readiness — domain tag stamped on all social tuples
    domain_tag:            str   = ""

    def __post_init__(self):
        if not self.domain_tag:
            self.domain_tag = self.name


# ─────────────────────────────────────────────────────────────
# BUILT-IN DOMAIN PROFILES
# ─────────────────────────────────────────────────────────────

DOMAIN_PROFILES: Dict[str, DomainProfile] = {

    "default": DomainProfile(
        name="default",
        display_name="General Purpose",
        description="Balanced configuration. No domain-specific bias.",
        glyph_tags=["general", "default"],
        pfc_config=PFCConfig(),
        metacog_config=MetacogConfig(),
        tfe_tau=3600.0,
        cme_explore_rate=0.02,
        cme_reinforce_gain=0.25,
        biorag_confidence_max=0.5,
    ),

    "coding": DomainProfile(
        name="coding",
        display_name="Software Development",
        description=(
            "Optimized for code generation and debugging. "
            "Higher exploration tolerance — mistakes are recoverable. "
            "Fast temporal decay — recent patterns matter most."
        ),
        glyph_tags=["coding", "software", "development", "engineering"],
        pfc_config=CODING_PFC_CONFIG,
        metacog_config=CODING_METACOG_CONFIG,
        tfe_tau=1800.0,          # 30 min — code patterns change fast
        cme_explore_rate=0.05,   # explore more freely
        cme_reinforce_gain=0.20, # softer constraint memory
        cme_decay_per_step=0.003,
        biorag_confidence_max=0.6,  # episode recall helps a lot in coding
        reset_context_memory=False,
    ),

    "medical": DomainProfile(
        name="medical",
        display_name="Medical / Clinical",
        description=(
            "Maximum caution. Errors cost lives. "
            "Very low exploration rate — almost never probe dangerous actions. "
            "Slow temporal decay — historical patterns matter longer. "
            "Aggressive constraint memory — learned dangers persist."
        ),
        glyph_tags=["medical", "clinical", "health", "diagnosis", "treatment"],
        pfc_config=MEDICAL_PFC_CONFIG,
        metacog_config=MEDICAL_METACOG_CONFIG,
        tfe_tau=14400.0,         # 4 hours — medical history matters longer
        cme_explore_rate=0.005,  # almost never probe flagged actions
        cme_reinforce_gain=0.40, # strong constraint memory
        cme_decay_per_step=0.001,# constraints decay very slowly
        biorag_confidence_max=0.4,  # don't over-trust episode recall in medicine
        biorag_min_evidence=5,      # require more evidence before trusting BioRAG
        reset_context_memory=True,  # medical contexts are distinct — fresh novelty slate
        reset_metacog_trust=False,  # preserve pillar trust from prior learning
    ),

    "legal": DomainProfile(
        name="legal",
        display_name="Legal / Compliance",
        description=(
            "High caution. Legal errors are expensive and hard to reverse. "
            "Moderate exploration — some discovery is necessary. "
            "Strong constraint memory — precedents matter."
        ),
        glyph_tags=["legal", "compliance", "contract", "regulation", "law"],
        pfc_config=LEGAL_PFC_CONFIG,
        metacog_config=LEGAL_METACOG_CONFIG,
        tfe_tau=7200.0,          # 2 hours
        cme_explore_rate=0.01,
        cme_reinforce_gain=0.35,
        cme_decay_per_step=0.0015,
        biorag_confidence_max=0.45,
        reset_context_memory=False,  # legal contexts often overlap with prior work
    ),

    "financial": DomainProfile(
        name="financial",
        display_name="Financial / Markets",
        description=(
            "Elevated caution with moderate speed. "
            "Markets change — temporal decay is moderate. "
            "Constraint memory is strong for risk management rules."
        ),
        glyph_tags=["financial", "finance", "markets", "trading", "risk"],
        pfc_config=FINANCIAL_PFC_CONFIG,
        metacog_config=FINANCIAL_METACOG_CONFIG,
        tfe_tau=3600.0,          # 1 hour — market conditions shift
        cme_explore_rate=0.015,
        cme_reinforce_gain=0.30,
        cme_decay_per_step=0.002,
        biorag_confidence_max=0.5,
        reset_context_memory=False,
    ),

    "research": DomainProfile(
        name="research",
        display_name="Research / Analysis",
        description=(
            "Balanced exploration and caution. "
            "Research benefits from novelty — higher exploration. "
            "Consequences are moderate — wrong analysis can be revised."
        ),
        glyph_tags=["research", "analysis", "science", "data", "academic"],
        pfc_config=PFCConfig(
            novelty_slow_threshold=0.65,
            novelty_escalate_threshold=0.9,
            uncertainty_slow_threshold=0.65,
            uncertainty_escalate_threshold=0.88,
            consequence_ceiling=0.80,
            slow_dampen_factor=0.45,
            high_stakes_cme_threshold=0.65,
        ),
        metacog_config=MetacogConfig(
            review_every_n_steps=20,
            fail_rate_threshold=0.48,
            win_rate_bonus_threshold=0.72,
            bandit_explore_stable_threshold=0.18,
        ),
        tfe_tau=3600.0,
        cme_explore_rate=0.04,
        cme_reinforce_gain=0.22,
        biorag_confidence_max=0.55,
    ),
}


# ─────────────────────────────────────────────────────────────
# DOMAIN TRANSITION RECORD — for NoesisCards audit trail
# ─────────────────────────────────────────────────────────────

@dataclass
class DomainTransition:
    """
    Records a domain load event.
    Every transition becomes a NoesisCards evidence card.

    This is how regulated industries get their audit trail:
    "The agent was operating in medical mode from step 450 to step 892."
    """
    from_domain:        str
    to_domain:          str
    timestamp:          float
    step:               int
    glyph_activated:    Optional[str]   # which glyph triggered this
    triggered_by:       str             # "glyph_witness" | "manual" | "api"
    params_changed:     Dict[str, Any]  # what actually changed
    memory_preserved:   bool            # was learned knowledge kept?


# ─────────────────────────────────────────────────────────────
# DOMAIN LOADER
# ─────────────────────────────────────────────────────────────

class DomainLoader:
    """
    Stem cell differentiation engine for QuintBioRAGAgent.

    Instantiate once. Pass the agent reference.
    Call activate() when the Witness approves a domain glyph.

    Usage:
        loader = DomainLoader(agent)

        # From Witch Bridge Witness gate:
        loader.activate_from_glyph("g-medical-policy@1.0.0")

        # Direct API:
        loader.activate("medical", step=current_step)

        # Custom profile:
        loader.register_profile(my_custom_profile)
        loader.activate("my_custom", step=current_step)
    """

    def __init__(self, agent: Any):
        """
        Args:
            agent: QuintBioRAGAgent instance (or any agent with the right interface)
        """
        self.agent = agent
        self._profiles: Dict[str, DomainProfile] = dict(DOMAIN_PROFILES)
        self._current_domain: str = "default"
        self._transition_log: deque = deque(maxlen=100)
        self._load_count: int = 0

        # Glyph registry — live source of glyph and card definitions
        self.registry: GlyphRegistry = get_registry()

        # Glyph tag → domain name mapping
        # Built from all registered profiles AND registry glyph tags
        self._glyph_tag_map: Dict[str, str] = {}
        self._rebuild_glyph_map()
        self._sync_registry_tags()

    # ─────────────────────────────────────────────
    # PRIMARY API
    # ─────────────────────────────────────────────

    def activate(
        self,
        domain: str,
        step: int = 0,
        triggered_by: str = "api",
        glyph_activated: Optional[str] = None,
        hard_reset: bool = False,
    ) -> DomainTransition:
        """
        Load a domain profile into the agent.

        Args:
            domain        : domain name (must be in registered profiles)
            step          : current agent step (for audit trail)
            triggered_by  : "glyph_witness" | "manual" | "api"
            glyph_activated: which glyph triggered this (if from Witness)
            hard_reset    : True = also reset metacog trust and context memory
                            Overrides profile settings if True.

        Returns:
            DomainTransition record (log to NoesisCards)

        Raises:
            ValueError if domain not registered
        """
        if domain not in self._profiles:
            raise ValueError(
                f"Domain '{domain}' not registered. "
                f"Available: {list(self._profiles.keys())}"
            )

        profile  = self._profiles[domain]
        from_dom = self._current_domain
        params_changed = {}

        # ── 1. PFC — impulse control thresholds ───────────────────────
        if hasattr(self.agent, 'pfc'):
            self.agent.pfc.load_domain_config(profile.pfc_config)
            params_changed['pfc_config'] = profile.name

            reset_ctx = hard_reset or profile.reset_context_memory
            if reset_ctx:
                self.agent.pfc.reset_context_memory()
                params_changed['pfc_context_memory'] = 'reset'

        # ── 2. Metacog — self-calibration thresholds ──────────────────
        if hasattr(self.agent, 'metacog'):
            self.agent.metacog.load_domain_config(profile.metacog_config)
            params_changed['metacog_config'] = profile.name

            reset_trust = hard_reset or profile.reset_metacog_trust
            if reset_trust:
                self.agent.metacog.reset_trust()
                params_changed['metacog_trust'] = 'reset'

        # ── 3. TFE — temporal decay rate ──────────────────────────────
        # TFE tau controls how fast time-based decay runs
        # Different domains have different "memory horizons"
        if hasattr(self.agent, 'tfe') and hasattr(self.agent.tfe, 'config'):
            old_tau = getattr(self.agent.tfe.config, 'tau', None)
            if old_tau is not None:
                self.agent.tfe.config.tau = profile.tfe_tau
                params_changed['tfe_tau'] = {
                    'from': old_tau,
                    'to': profile.tfe_tau
                }

        # ── 4. CME — constraint memory parameters ─────────────────────
        if hasattr(self.agent, 'cme'):
            old_explore = getattr(self.agent.cme, 'explore_rate', None)
            old_gain    = getattr(self.agent.cme, 'reinforce_gain', None)
            old_decay   = getattr(self.agent.cme, 'decay_per_step', None)

            if old_explore is not None:
                self.agent.cme.explore_rate   = profile.cme_explore_rate
                self.agent.cme.reinforce_gain = profile.cme_reinforce_gain
                self.agent.cme.decay_per_step = profile.cme_decay_per_step
                params_changed['cme'] = {
                    'explore_rate':   {'from': old_explore, 'to': profile.cme_explore_rate},
                    'reinforce_gain': {'from': old_gain,    'to': profile.cme_reinforce_gain},
                    'decay_per_step': {'from': old_decay,   'to': profile.cme_decay_per_step},
                }

        # ── 5. BioRAG — episodic memory influence ─────────────────────
        if hasattr(self.agent, 'rag'):
            rag = self.agent.rag
            old_conf_max = getattr(rag, 'confidence_max', None)
            old_min_ev   = getattr(rag, 'min_evidence', None)

            if old_conf_max is not None:
                rag.confidence_max = profile.biorag_confidence_max
                params_changed['biorag_confidence_max'] = {
                    'from': old_conf_max,
                    'to': profile.biorag_confidence_max
                }
            if old_min_ev is not None:
                rag.min_evidence = profile.biorag_min_evidence
                params_changed['biorag_min_evidence'] = {
                    'from': old_min_ev,
                    'to': profile.biorag_min_evidence
                }

        # ── 6. Domain tag — Pillar 7 readiness ───────────────────────
        # Stamp the active domain on the agent so every decision
        # carries its domain tag (needed for social tuples in Pillar 7)
        self.agent._active_domain = profile.domain_tag
        params_changed['domain_tag'] = profile.domain_tag

        # ── 7. Update state ───────────────────────────────────────────
        self._current_domain = domain
        self._load_count += 1

        # ── 8. Build transition record ────────────────────────────────
        transition = DomainTransition(
            from_domain=from_dom,
            to_domain=domain,
            timestamp=time.time(),
            step=step,
            glyph_activated=glyph_activated,
            triggered_by=triggered_by,
            params_changed=params_changed,
            memory_preserved=not hard_reset,
        )
        self._transition_log.append(transition)

        return transition

    def activate_from_glyph(
        self,
        glyph_id: str,
        step: int = 0,
    ) -> Optional[DomainTransition]:
        """
        Activate domain from a glyph ID.
        Called by Witch Bridge after Witness approves a domain glyph patch.

        Glyph ID format: g-{name}@{semver}
        Example: g-medical-policy@1.0.0

        Maps glyph tags to domain profiles automatically.
        Returns None if no domain matches the glyph tags.

        Usage in Witch Bridge Executive loop:
            patch = witness.approve(plan)
            if patch.witness.approved:
                for glyph_id in patch.witness.glyphsActivated:
                    transition = domain_loader.activate_from_glyph(glyph_id, step)
                    if transition:
                        noesis_cards.create_card("domain_transition", transition)
        """
        # Extract name from glyph ID: g-medical-policy@1.0.0 → medical-policy
        try:
            raw = glyph_id.split('@')[0]  # g-medical-policy
            glyph_name = raw[2:] if raw.startswith('g-') else raw
        except Exception:
            return None

        # Check each tag word in the glyph name against our map.
        # Also check full domain names directly — e.g. "coding" in "coding-rules"
        # Priority: exact domain name match first, then tag word match
        words = glyph_name.split('-')

        # Pass 1: check if any word IS a registered domain name directly
        for word in words:
            if word in self._profiles:
                return self.activate(
                    domain=word,
                    step=step,
                    triggered_by="glyph_witness",
                    glyph_activated=glyph_id,
                )

        # Pass 2: check glyph tag map
        for word in words:
            if word in self._glyph_tag_map:
                domain = self._glyph_tag_map[word]
                return self.activate(
                    domain=domain,
                    step=step,
                    triggered_by="glyph_witness",
                    glyph_activated=glyph_id,
                )


        return None  # no matching domain for this glyph

    # ─────────────────────────────────────────────
    # PROFILE MANAGEMENT
    # ─────────────────────────────────────────────

    def register_profile(self, profile: DomainProfile) -> None:
        """
        Register a custom domain profile.

        Use this to add new domains at runtime without modifying
        the built-in registry. Witch Bridge can expose a UI for this.

        Example — adding a cybersecurity domain:
            loader.register_profile(DomainProfile(
                name="cybersecurity",
                display_name="Cybersecurity",
                description="...",
                glyph_tags=["security", "cyber", "threat"],
                pfc_config=PFCConfig(...),
                metacog_config=MetacogConfig(...),
                tfe_tau=1800.0,
                ...
            ))
            loader.activate("cybersecurity", step=current_step)
        """
        self._profiles[profile.name] = profile
        self._rebuild_glyph_map()

    def get_profile(self, domain: str) -> Optional[DomainProfile]:
        """Get a registered profile by name."""
        return self._profiles.get(domain)

    def list_domains(self) -> List[str]:
        """List all registered domain names."""
        return list(self._profiles.keys())

    def get_current_domain(self) -> str:
        """Current active domain name."""
        return self._current_domain

    def get_current_profile(self) -> DomainProfile:
        """Current active domain profile."""
        return self._profiles[self._current_domain]

    # ─────────────────────────────────────────────
    # SNAPSHOT — save/restore domain state
    # ─────────────────────────────────────────────

    def snapshot(self) -> Dict[str, Any]:
        """
        Capture current domain state for persistence.
        Include in agent.save_state() for full state preservation.
        """
        return {
            "current_domain": self._current_domain,
            "load_count":     self._load_count,
            "transition_log": [
                {
                    "from_domain":      t.from_domain,
                    "to_domain":        t.to_domain,
                    "timestamp":        t.timestamp,
                    "step":             t.step,
                    "glyph_activated":  t.glyph_activated,
                    "triggered_by":     t.triggered_by,
                    "memory_preserved": t.memory_preserved,
                }
                for t in self._transition_log
            ],
        }

    def restore(self, snapshot: Dict[str, Any]) -> None:
        """
        Restore domain loader state from snapshot.
        Call after agent.load_state().
        Does NOT re-apply domain configs (agent state already restored).
        Just restores the audit trail and current domain tracking.
        """
        self._current_domain = snapshot.get("current_domain", "default")
        self._load_count     = snapshot.get("load_count", 0)
        for t in snapshot.get("transition_log", []):
            self._transition_log.append(DomainTransition(
                from_domain=t["from_domain"],
                to_domain=t["to_domain"],
                timestamp=t["timestamp"],
                step=t["step"],
                glyph_activated=t.get("glyph_activated"),
                triggered_by=t["triggered_by"],
                params_changed={},
                memory_preserved=t["memory_preserved"],
            ))

    # ─────────────────────────────────────────────
    # DIAGNOSTICS
    # ─────────────────────────────────────────────

    def get_stats(self) -> Dict[str, Any]:
        """
        Telemetry for Witch Bridge.
        Feed into the Cortex panel alongside Pillar 6 stats.
        """
        profile = self.get_current_profile()
        return {
            "current_domain":       self._current_domain,
            "display_name":         profile.display_name,
            "total_transitions":    self._load_count,
            "registered_domains":   self.list_domains(),
            "last_transition":      self._format_transition(
                self._transition_log[-1]
            ) if self._transition_log else None,
        }

    def get_transition_log(self) -> List[Dict[str, Any]]:
        """
        Full transition log for NoesisCards audit trail.
        Every domain transition should become an evidence card.
        """
        return [
            {
                "from_domain":     t.from_domain,
                "to_domain":       t.to_domain,
                "timestamp":       t.timestamp,
                "step":            t.step,
                "glyph_activated": t.glyph_activated,
                "triggered_by":    t.triggered_by,
                "memory_preserved": t.memory_preserved,
            }
            for t in self._transition_log
        ]

    # ─────────────────────────────────────────────
    # REGISTRY API — glyphs and cards as first-class citizens
    # ─────────────────────────────────────────────

    def get_glyph(self, glyph_id: str) -> Optional[Glyph]:
        """Get a glyph by ID from the registry."""
        return self.registry.get_glyph(glyph_id)

    def get_card(self, card_id: str) -> Optional[Card]:
        """Get a card by ID from the registry."""
        return self.registry.get_card(card_id)

    def get_domain_cards(self, domain: str) -> list:
        """Get all cards that activate a given domain."""
        return self.registry.get_cards_by_domain(domain)

    def get_domain_glyphs(self, domain: str) -> list:
        """Get all glyphs for a given domain."""
        return self.registry.get_glyphs_by_domain(domain)

    def register_glyph(self, glyph: Glyph) -> tuple:
        """
        Register a new glyph and sync its tags into the domain map.
        Use this to add rules at runtime without restarting.
        """
        ok, errors = self.registry.register_glyph(glyph)
        if ok:
            self._sync_registry_tags()
        return ok, errors

    def register_card(self, card: Card) -> tuple:
        """Register a new card at runtime."""
        return self.registry.register_card(card)

    def load_glyphs_from_directory(self, path: str) -> dict:
        """
        Load glyphs and cards from a directory of JSON files.
        Immediately syncs tags so new domain glyphs are activatable.

        Drop JSON files in glyphs/ and cards/ subdirs, call this, done.
        """
        result = self.registry.bootstrap_from_directory(path)
        self._sync_registry_tags()
        return result

    def get_registry_stats(self) -> dict:
        """Registry telemetry — glyphs loaded, cards loaded, domains covered."""
        return self.registry.get_stats()

    def activate_from_card(
        self,
        card_id: str,
        step: int = 0,
    ) -> Optional[DomainTransition]:
        """
        Activate domain from a card ID.
        The card's glyphs determine which domain gets loaded.

        Usage:
            loader.activate_from_card("card-activate-medical", step=42)

        Returns None if no domain glyph found on the card.
        """
        card = self.registry.get_card(card_id)
        if not card:
            return None
        # Try each glyph on the card — first domain match wins
        for glyph_id in card.glyph_ids:
            transition = self.activate_from_glyph(glyph_id, step=step)
            if transition:
                return transition
        return None

    # ─────────────────────────────────────────────
    # INTERNALS
    # ─────────────────────────────────────────────

    def _rebuild_glyph_map(self) -> None:
        """Rebuild tag → domain mapping from all registered profiles."""
        self._glyph_tag_map = {}
        for domain_name, profile in self._profiles.items():
            for tag in profile.glyph_tags:
                # First registered profile wins for each tag
                if tag not in self._glyph_tag_map:
                    self._glyph_tag_map[tag] = domain_name

    def _sync_registry_tags(self) -> None:
        """
        Pull domain tags from registry glyphs into the glyph tag map.
        Called after any new glyph is registered.

        This means: add a glyph with domain="medical" tag,
        and activate_from_glyph() will immediately find it.
        """
        for glyph in self.registry.get_all_glyphs().values():
            domain = glyph.get_domain()
            if domain and domain in self._profiles:
                for tag in glyph.tags:
                    if tag not in self._glyph_tag_map:
                        self._glyph_tag_map[tag] = domain

    def _format_transition(self, t: DomainTransition) -> Dict[str, Any]:
        return {
            "from":             t.from_domain,
            "to":               t.to_domain,
            "step":             t.step,
            "triggered_by":     t.triggered_by,
            "glyph":            t.glyph_activated,
            "memory_preserved": t.memory_preserved,
        }


# ─────────────────────────────────────────────────────────────
# INTEGRATION INTO QuintBioRAGAgent
# ─────────────────────────────────────────────────────────────

AGENT_INTEGRATION = """
# ADD to QuintBioRAGAgent.__init__():

self.domain_loader = DomainLoader(self)
self._active_domain = "default"  # stamped on every decision


# ADD convenience method to QuintBioRAGAgent:

def load_domain(
    self,
    domain: str,
    step: int = 0,
    triggered_by: str = "api",
    glyph_activated: str = None,
    hard_reset: bool = False,
) -> DomainTransition:
    '''
    Load a domain. The stem cell differentiation trigger.
    
    Returns DomainTransition — log this to NoesisCards.
    '''
    return self.domain_loader.activate(
        domain=domain,
        step=step,
        triggered_by=triggered_by,
        glyph_activated=glyph_activated,
        hard_reset=hard_reset,
    )

def load_domain_from_glyph(self, glyph_id: str, step: int = 0):
    '''Called by Witch Bridge after Witness approves a domain glyph.'''
    return self.domain_loader.activate_from_glyph(glyph_id, step)

def get_domain_stats(self) -> dict:
    '''Domain telemetry for Witch Bridge Cortex panel.'''
    return self.domain_loader.get_stats()
"""


# ─────────────────────────────────────────────────────────────
# WITCH BRIDGE EXECUTIVE LOOP INTEGRATION
# ─────────────────────────────────────────────────────────────

EXECUTIVE_LOOP_INTEGRATION = """
# In Witch Bridge Executive Console (after Witness approves a patch):

for glyph_id in patch.witness.glyphsActivated:
    transition = agent.load_domain_from_glyph(glyph_id, step=current_step)
    
    if transition:
        # Log to NoesisCards — every domain shift is an evidence card
        noesis_cards.append_card({
            "card_id": f"DOMAIN_{current_step}",
            "type": "domain_transition",
            "data": {
                "from_domain":      transition.from_domain,
                "to_domain":        transition.to_domain,
                "glyph_activated":  transition.glyph_activated,
                "memory_preserved": transition.memory_preserved,
                "params_changed":   transition.params_changed,
            },
            "timestamp": transition.timestamp,
        })

# Pillar 7 readiness: every choose() call now has domain tag
# agent._active_domain carries the current domain
# Social tuples will include this tag automatically
"""
