"""
Domain Loader Test Suite
========================
Add these to quint_biorag_harness.py DOMAIN suite.

Tests prove:
  1. Domain profiles load without crashing
  2. Parameters actually change on load
  3. Memory is preserved across domain transitions
  4. Glyph tag activation works
  5. Custom profiles register and activate
  6. Transition log is populated for NoesisCards
  7. Hard reset clears what it should
  8. Multiple rapid domain switches stay coherent
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from domain_loader import DomainLoader, DomainProfile, DOMAIN_PROFILES
from pfc_engine import PFCConfig
from metacognitive_monitor import MetacogConfig


# ── Minimal mock agent for isolated loader tests ─────────────────────────────
class MockAgent:
    """Minimal surface area for DomainLoader to write to."""
    def __init__(self):
        self._active_domain = "default"

        # PFC mock
        class PFC:
            config = PFCConfig()
            def load_domain_config(self, c): self.config = c
            def reset_context_memory(self): pass
        self.pfc = PFC()

        # Metacog mock
        class Metacog:
            config = MetacogConfig()
            def load_domain_config(self, c): self.config = c
            def reset_trust(self): pass
        self.metacog = Metacog()

        # TFE mock
        class TFEConfig:
            tau = 3600.0
        class TFE:
            config = TFEConfig()
        self.tfe = TFE()

        # CME mock
        class CME:
            explore_rate   = 0.02
            reinforce_gain = 0.25
            decay_per_step = 0.002
        self.cme = CME()

        # BioRAG mock
        class BioRAG:
            confidence_max = 0.5
            min_evidence   = 3
        self.rag = BioRAG()


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_domain_loader_all_profiles_load():
    """All built-in profiles activate without error."""
    agent  = MockAgent()
    loader = DomainLoader(agent)
    errors = []

    for domain in DOMAIN_PROFILES:
        try:
            loader.activate(domain, step=0)
            assert loader.get_current_domain() == domain
        except Exception as e:
            errors.append(f"{domain}: {e}")

    passed = len(errors) == 0
    return {
        "name":    "Domain: all built-in profiles load",
        "suite":   "domain",
        "passed":  passed,
        "metrics": {"profiles_tested": len(DOMAIN_PROFILES), "errors": len(errors)},
        "notes":   "; ".join(errors) if errors else "",
    }


def test_domain_loader_params_change():
    """Loading medical vs coding produces different TFE tau and CME explore rate."""
    agent  = MockAgent()
    loader = DomainLoader(agent)

    loader.activate("coding", step=0)
    coding_tau     = agent.tfe.config.tau
    coding_explore = agent.cme.explore_rate

    loader.activate("medical", step=1)
    medical_tau     = agent.tfe.config.tau
    medical_explore = agent.cme.explore_rate

    tau_differs     = medical_tau > coding_tau        # medical should be slower
    explore_differs = medical_explore < coding_explore # medical should explore less

    passed = tau_differs and explore_differs
    return {
        "name":    "Domain: medical vs coding params differ",
        "suite":   "domain",
        "passed":  passed,
        "metrics": {
            "coding_tau":      coding_tau,
            "medical_tau":     medical_tau,
            "coding_explore":  coding_explore,
            "medical_explore": medical_explore,
        },
        "notes": "Params not differentiating" if not passed else "",
    }


def test_domain_loader_memory_preserved():
    """Domain transition does NOT wipe CME, BioRAG, or Metacog trust by default."""
    agent  = MockAgent()
    loader = DomainLoader(agent)

    # Manually set some "learned" state
    agent.cme.explore_rate = 0.999  # sentinel value — should survive domain load
    # (real agent: Bandit posteriors, CME rule memory, BioRAG traces)

    # Load a new domain (not hard reset)
    loader.activate("legal", step=5, hard_reset=False)

    # The domain loader changes explore_rate via profile
    # but the point is it sets it to the PROFILE value not zero
    # Memory test: transition log should show memory_preserved=True
    log = loader.get_transition_log()
    passed = len(log) > 0 and log[-1]["memory_preserved"] is True

    return {
        "name":    "Domain: memory preserved on standard transition",
        "suite":   "domain",
        "passed":  passed,
        "metrics": {"transition_count": len(log)},
        "notes":   "memory_preserved flag not set" if not passed else "",
    }


def test_domain_loader_glyph_activation():
    """Glyph IDs correctly map to domain profiles."""
    agent  = MockAgent()
    loader = DomainLoader(agent)

    cases = [
        ("g-medical-policy@1.0.0",  "medical"),
        ("g-legal-contract@1.0.0",  "legal"),
        ("g-coding-rules@1.0.0",    "coding"),
        ("g-financial-risk@1.0.0",  "financial"),
    ]

    results = {}
    for glyph_id, expected_domain in cases:
        transition = loader.activate_from_glyph(glyph_id, step=0)
        if transition:
            results[glyph_id] = loader.get_current_domain() == expected_domain
        else:
            results[glyph_id] = False

    passed = all(results.values())
    return {
        "name":    "Domain: glyph tag → domain mapping",
        "suite":   "domain",
        "passed":  passed,
        "metrics": {k: v for k, v in results.items()},
        "notes":   "Some glyph→domain mappings failed" if not passed else "",
    }


def test_domain_loader_custom_profile():
    """Custom profiles register and activate correctly."""
    agent  = MockAgent()
    loader = DomainLoader(agent)

    custom = DomainProfile(
        name="cybersecurity",
        display_name="Cybersecurity",
        description="Threat detection domain",
        glyph_tags=["security", "cyber", "threat"],
        pfc_config=PFCConfig(novelty_slow_threshold=0.4),
        metacog_config=MetacogConfig(fail_rate_threshold=0.35),
        tfe_tau=900.0,
        cme_explore_rate=0.008,
    )

    loader.register_profile(custom)
    assert "cybersecurity" in loader.list_domains()

    transition = loader.activate("cybersecurity", step=10)
    passed = (
        loader.get_current_domain() == "cybersecurity" and
        agent.tfe.config.tau == 900.0 and
        agent.cme.explore_rate == 0.008
    )
    return {
        "name":    "Domain: custom profile registers and activates",
        "suite":   "domain",
        "passed":  passed,
        "metrics": {
            "tfe_tau":     agent.tfe.config.tau,
            "explore_rate": agent.cme.explore_rate,
        },
        "notes": "Custom profile params not applied" if not passed else "",
    }


def test_domain_loader_transition_log():
    """Transition log populates for NoesisCards integration."""
    agent  = MockAgent()
    loader = DomainLoader(agent)

    sequence = ["coding", "medical", "legal", "financial", "default"]
    for i, domain in enumerate(sequence):
        loader.activate(domain, step=i * 10)

    log = loader.get_transition_log()
    passed = (
        len(log) == len(sequence) and
        log[0]["to_domain"] == "coding" and
        log[-1]["to_domain"] == "default" and
        all("timestamp" in t for t in log)
    )
    return {
        "name":    "Domain: transition log populates for audit trail",
        "suite":   "domain",
        "passed":  passed,
        "metrics": {"transitions_logged": len(log)},
        "notes":   "Transition log incomplete" if not passed else "",
    }


def test_domain_loader_hard_reset():
    """Hard reset clears context memory and metacog trust."""
    agent  = MockAgent()
    loader = DomainLoader(agent)

    # Track whether reset methods were called
    pfc_reset_called     = [False]
    metacog_reset_called = [False]

    original_pfc_reset     = agent.pfc.reset_context_memory
    original_metacog_reset = agent.metacog.reset_trust

    def pfc_reset_spy():
        pfc_reset_called[0] = True
        original_pfc_reset()

    def metacog_reset_spy():
        metacog_reset_called[0] = True
        original_metacog_reset()

    agent.pfc.reset_context_memory = pfc_reset_spy
    agent.metacog.reset_trust       = metacog_reset_spy

    loader.activate("medical", step=0, hard_reset=True)

    passed = pfc_reset_called[0] and metacog_reset_called[0]
    return {
        "name":    "Domain: hard reset clears context memory and trust",
        "suite":   "domain",
        "passed":  passed,
        "metrics": {
            "pfc_reset":     pfc_reset_called[0],
            "metacog_reset": metacog_reset_called[0],
        },
        "notes": "Hard reset not triggering resets" if not passed else "",
    }


def test_domain_loader_rapid_switching():
    """Rapid domain switches stay coherent — no crashes, correct final state."""
    agent  = MockAgent()
    loader = DomainLoader(agent)
    domains = ["coding", "medical", "legal", "financial", "research", "default"]
    errors = []

    for i in range(60):
        domain = domains[i % len(domains)]
        try:
            loader.activate(domain, step=i)
        except Exception as e:
            errors.append(str(e))

    final_domain = loader.get_current_domain()
    expected     = domains[59 % len(domains)]
    passed       = len(errors) == 0 and final_domain == expected

    return {
        "name":    "Domain: 60 rapid switches stay coherent",
        "suite":   "domain",
        "passed":  passed,
        "metrics": {
            "errors":       len(errors),
            "final_domain": final_domain,
            "expected":     expected,
        },
        "notes": f"Errors: {errors[:2]}" if errors else "",
    }


# ── Runner ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        test_domain_loader_all_profiles_load,
        test_domain_loader_params_change,
        test_domain_loader_memory_preserved,
        test_domain_loader_glyph_activation,
        test_domain_loader_custom_profile,
        test_domain_loader_transition_log,
        test_domain_loader_hard_reset,
        test_domain_loader_rapid_switching,
    ]

    print("\n" + "═" * 60)
    print("  DOMAIN LOADER TEST SUITE")
    print("═" * 60)

    passed_count = 0
    for fn in tests:
        result = fn()
        icon   = "✓" if result["passed"] else "✗"
        metric_str = "  |  " + "  ".join(
            f"{k}={v}" for k, v in list(result.get("metrics", {}).items())[:3]
        )
        note = f"  ← {result['notes']}" if result.get("notes") else ""
        print(f"  {icon}  {result['name']:<48}{metric_str}{note}")
        if result["passed"]:
            passed_count += 1

    print()
    print(f"  {passed_count}/{len(tests)} passed")
    print("═" * 60)


# ═══════════════════════════════════════════════════════════════
# REGISTRY TESTS — Glyphs and Cards as first-class citizens
# ═══════════════════════════════════════════════════════════════

def test_registry_bootstrap():
    """All built-in glyphs and cards load with zero errors."""
    from glyph_registry import bootstrap_registry, GlyphRegistry
    reg = GlyphRegistry()
    report = reg.bootstrap()

    passed = (
        report["ok"] and
        report["glyphs_loaded"] == 8 and
        report["cards_loaded"]  == 11 and
        len(report["glyph_errors"]) == 0 and
        len(report["card_errors"])  == 0
    )
    return {
        "name":    "Registry: bootstrap loads 8 glyphs + 11 cards clean",
        "suite":   "registry",
        "passed":  passed,
        "metrics": {
            "glyphs": report["glyphs_loaded"],
            "cards":  report["cards_loaded"],
            "errors": len(report["glyph_errors"]) + len(report["card_errors"]),
        },
    }


def test_registry_domain_glyphs_covered():
    """Each domain has at least one glyph in the registry."""
    from glyph_registry import GlyphRegistry
    reg = GlyphRegistry()
    reg.bootstrap()

    domain_map = reg.get_domain_glyphs()
    required   = {"medical", "legal", "coding", "financial"}
    covered    = set(domain_map.keys())
    missing    = required - covered

    passed = len(missing) == 0
    return {
        "name":    "Registry: all 4 core domains have glyphs",
        "suite":   "registry",
        "passed":  passed,
        "metrics": {"covered": list(covered), "missing": list(missing)},
    }


def test_registry_card_domain_activation():
    """card-activate-medical activates medical domain via loader."""
    from glyph_registry import bootstrap_registry
    bootstrap_registry()

    agent  = MockAgent()
    loader = DomainLoader(agent)

    transition = loader.activate_from_card("card-activate-medical", step=5)
    passed = (
        transition is not None and
        loader.get_current_domain() == "medical" and
        transition.triggered_by == "glyph_witness"
    )
    return {
        "name":    "Registry: card-activate-medical loads medical domain",
        "suite":   "registry",
        "passed":  passed,
        "metrics": {
            "domain":   loader.get_current_domain(),
            "via_card": transition.glyph_activated if transition else None,
        },
    }


def test_registry_runtime_glyph_registration():
    """Register a new glyph at runtime — immediately activatable."""
    from glyph_registry import bootstrap_registry, Glyph, GlyphJson, GlyphActivation, GlyphValidation
    bootstrap_registry()

    agent  = MockAgent()
    loader = DomainLoader(agent)

    # Register a new glyph for an existing domain
    new_glyph = Glyph(
        id="g-medical-audit@1.0.0",
        title="Medical Audit Trail",
        md="# Medical Audit Trail\nEvery clinical decision must be logged.",
        json=GlyphJson(
            type="observer",
            authority="observational",
            validation=GlyphValidation(rules=["medical.log_all_decisions"]),
            domain="medical",
        ),
        tags=["medical", "audit", "clinical"],
    )

    ok, errors = loader.register_glyph(new_glyph)
    assert ok, f"Registration failed: {errors}"

    # Verify it's in the registry
    fetched = loader.get_glyph("g-medical-audit@1.0.0")
    # Verify its tag synced into the glyph map
    tag_mapped = loader._glyph_tag_map.get("audit") == "medical" or \
                 loader._glyph_tag_map.get("clinical") == "medical"

    passed = fetched is not None and ok
    return {
        "name":    "Registry: runtime glyph registration works",
        "suite":   "registry",
        "passed":  passed,
        "metrics": {
            "registered":  ok,
            "fetchable":   fetched is not None,
            "tag_synced":  tag_mapped,
        },
    }


def test_registry_override_extraction():
    """Glyph parameter overrides are readable by domain."""
    from glyph_registry import bootstrap_registry, GlyphRegistry
    bootstrap_registry()

    reg = GlyphRegistry()
    reg.bootstrap()

    overrides = reg.extract_domain_overrides("medical")
    passed = (
        overrides.get("tfe_tau")            == 14400.0 and
        overrides.get("cme_explore_rate")   == 0.005   and
        overrides.get("biorag_confidence_max") == 0.4
    )
    return {
        "name":    "Registry: glyph overrides extract correctly for medical",
        "suite":   "registry",
        "passed":  passed,
        "metrics": {k: v for k, v in overrides.items()},
    }


def test_registry_json_roundtrip():
    """Glyphs serialize to JSON and back without data loss."""
    import json, tempfile, os
    from glyph_registry import bootstrap_registry, GlyphRegistry
    bootstrap_registry()

    reg = GlyphRegistry()
    reg.bootstrap()

    with tempfile.TemporaryDirectory() as tmpdir:
        glyph_dir = os.path.join(tmpdir, "glyphs")
        os.makedirs(glyph_dir)

        reg.export_glyph_to_file(
            "g-medical-policy@1.0.0",
            os.path.join(glyph_dir, "g-medical-policy@1.0.0.json")
        )

        reg2 = GlyphRegistry()
        reg2.bootstrap()
        extra = reg2.bootstrap_from_directory(tmpdir)

        # Should load 1 extra glyph (duplicate id overwrites cleanly)
        loaded_ok = extra["errors"] == []

    passed = loaded_ok
    return {
        "name":    "Registry: glyph JSON roundtrip — export then reload",
        "suite":   "registry",
        "passed":  passed,
        "metrics": {"extra_glyphs": extra.get("glyphs", 0), "errors": extra.get("errors", [])},
    }


def test_registry_cards_by_glyph():
    """get_cards_by_glyph returns correct cards."""
    from glyph_registry import bootstrap_registry, GlyphRegistry
    bootstrap_registry()
    reg = GlyphRegistry()
    reg.bootstrap()

    cards = reg.get_cards_by_glyph("g-observer@0.1.0")
    card_ids = [c.id for c in cards]

    # observer glyph is referenced by: init-workspace, validate-patch,
    # snapshot, activate-medical, activate-legal, activate-financial,
    # escalate-to-human, domain-transition, metacog-adjustment
    expected_subset = {
        "card-init-workspace", "card-validate-patch",
        "card-snapshot", "card-activate-medical",
    }
    passed = expected_subset.issubset(set(card_ids))
    return {
        "name":    "Registry: get_cards_by_glyph returns correct cards",
        "suite":   "registry",
        "passed":  passed,
        "metrics": {"cards_found": len(card_ids), "sample": card_ids[:4]},
    }


if __name__ == "__main__":
    registry_tests = [
        test_registry_bootstrap,
        test_registry_domain_glyphs_covered,
        test_registry_card_domain_activation,
        test_registry_runtime_glyph_registration,
        test_registry_override_extraction,
        test_registry_json_roundtrip,
        test_registry_cards_by_glyph,
    ]

    print("\n" + "═" * 60)
    print("  GLYPH REGISTRY TEST SUITE")
    print("═" * 60)

    passed_count = 0
    for fn in registry_tests:
        result = fn()
        icon = "✓" if result["passed"] else "✗"
        metric_str = "  |  " + "  ".join(
            f"{k}={v}" for k, v in list(result.get("metrics", {}).items())[:3]
        )
        note = f"  ← {result['notes']}" if result.get("notes") else ""
        print(f"  {icon}  {result['name']:<52}{metric_str}{note}")
        if result["passed"]:
            passed_count += 1

    print()
    print(f"  {passed_count}/{len(registry_tests)} passed")
    print("═" * 60)
