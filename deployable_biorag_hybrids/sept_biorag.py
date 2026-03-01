"""
Sept-BioRAG Agent — The 7th Generation (Domain-Adaptive)
============================================================
Cognitive Architecture: 6 Pillars + Domain Loader

  Pillar 1 — CME     : Declarative Memory
  Pillar 2 — TS      : Procedural Instinct (Thompson Sampling)
  Pillar 3 — TFE     : Temporal Awareness
  Pillar 4 — PEE     : Dopamine System (Prediction Error)
  Pillar 5 — BioRAG  : Episodic Memory (Hopfield Attractors)
  Pillar 6 — PFC     : Impulse Control + Self-Calibration
  Domain   — Loader  : Stem Cell Differentiation Engine

Subclasses SextBioRAGAgent unchanged — all 6-pillar logic preserved.
Adds DomainLoader for runtime domain switching with full audit trail.

Key principle:
  Same brain. Different governance envelope.
  The agent's KNOWLEDGE persists (posteriors, rules, memory).
  Only the GOVERNANCE PARAMETERS change (thresholds, rates, decay).
"""

import sys
import os
from typing import Dict, List, Tuple, Optional, Any

# ── Path setup ──
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_SANDBOX  = os.path.join(os.path.dirname(_THIS_DIR), "sandbox_hybrid")
_PFC_DIR  = os.path.join(_SANDBOX, "pfc")
_DOM_DIR  = os.path.join(_PFC_DIR, "domain")

for _p in [_THIS_DIR, _SANDBOX, _PFC_DIR, _DOM_DIR]:
    if _p not in sys.path:
        pass  # sys.path.insert block removed for deployability

# ── Core import ──
from sext_biorag import SextBioRAGAgent, RAGInterface, PFCConfig, MetacogConfig

# ── Domain imports ──
from domain_loader import DomainLoader, DomainProfile, DomainTransition


# ============================================================
# SEPT-BIORAG AGENT (6 Pillars + Domain Loader)
# ============================================================

class SeptBioRAGAgent(SextBioRAGAgent):
    """
    Domain-adaptive agent. Drop-in replacement for SextBioRAGAgent.

    Adds:
      DomainLoader — runtime domain switching with audit trail
      Glyph integration — activate domains from glyph IDs
      Domain telemetry — current domain, transition history

    Usage:
        agent = SeptBioRAGAgent()

        # Switch to medical mode
        transition = agent.load_domain("medical", step=42)

        # Switch from glyph activation (Witch Bridge flow)
        transition = agent.load_domain_from_glyph("g-medical-policy@1.0.0", step=50)

        # Check current domain
        print(agent.get_domain_stats())
    """

    def __init__(
        self,
        seed: int = 42,
        tfe_tau: float = 3600.0,
        pee_kwargs: Optional[dict] = None,
        rag: Optional[RAGInterface] = None,
        sham_pe: bool = False,
        biorag_kwargs: Optional[dict] = None,
        residue_config=None,
        adaptive_encoding_enabled: bool = False,
        pfc_config: Optional[PFCConfig] = None,
        metacog_config: Optional[MetacogConfig] = None,
        # Domain config
        initial_domain: Optional[str] = None,
    ):
        # Initialize the 6-pillar base
        super().__init__(
            seed=seed,
            tfe_tau=tfe_tau,
            pee_kwargs=pee_kwargs,
            rag=rag,
            sham_pe=sham_pe,
            biorag_kwargs=biorag_kwargs,
            residue_config=residue_config,
            adaptive_encoding_enabled=adaptive_encoding_enabled,
            pfc_config=pfc_config,
            metacog_config=metacog_config,
        )

        # ── Domain Loader — Stem Cell Differentiation Engine ──
        self._active_domain = "default"
        self.domain_loader = DomainLoader(self)

        # Activate initial domain if specified
        if initial_domain and initial_domain != "default":
            self.domain_loader.activate(initial_domain, step=0, triggered_by="init")

    # ─────────────────────────────────────────────
    # DOMAIN API — overrides SextBioRAGAgent.load_domain()
    # ─────────────────────────────────────────────

    def load_domain(
        self,
        domain: str,
        step: int = 0,
        triggered_by: str = "api",
        glyph_activated: Optional[str] = None,
        hard_reset: bool = False,
    ) -> DomainTransition:
        """
        Load a domain. The stem cell differentiation trigger.

        Returns DomainTransition — log this to NoesisCards.
        """
        return self.domain_loader.activate(
            domain=domain,
            step=step,
            triggered_by=triggered_by,
            glyph_activated=glyph_activated,
            hard_reset=hard_reset,
        )

    def load_domain_from_glyph(
        self,
        glyph_id: str,
        step: int = 0,
    ) -> Optional[DomainTransition]:
        """
        Activate domain from a glyph ID.
        Called by Witch Bridge after Witness approves a domain glyph patch.

        Returns None if no domain matches the glyph tags.
        """
        return self.domain_loader.activate_from_glyph(glyph_id, step=step)

    def load_domain_from_card(
        self,
        card_id: str,
        step: int = 0,
    ) -> Optional[DomainTransition]:
        """
        Activate domain from a card ID.
        Card's glyphs determine which domain gets loaded.
        """
        return self.domain_loader.activate_from_card(card_id, step=step)

    def register_domain(self, profile: DomainProfile) -> None:
        """Register a custom domain profile at runtime."""
        self.domain_loader.register_profile(profile)

    # ─────────────────────────────────────────────
    # DIAGNOSTICS — extended with domain info
    # ─────────────────────────────────────────────

    def get_domain_stats(self) -> Dict[str, Any]:
        """Domain telemetry — current domain, transitions, registered domains."""
        return self.domain_loader.get_stats()

    def get_all_stats(self) -> Dict[str, Any]:
        """Combined telemetry: all 6 pillars + domain."""
        stats = {}
        stats['domain'] = self.get_domain_stats()
        stats['pillar6'] = self.get_pillar6_stats()
        stats['pee'] = self.get_pe_stats()
        return stats

    def diagnose_last_decision(self) -> Dict[str, Any]:
        """Extended diagnostics including active domain."""
        base = super().diagnose_last_decision()
        base['active_domain'] = self._active_domain
        return base
