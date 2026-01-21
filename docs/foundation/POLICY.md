# νόησις Artifact Deck — Governance Policy

Author: Timothy Wesley Stone  
License: Open / Shareable

This document defines the authoritative governance rules for the νόησις Artifact Deck.
It establishes naming conventions, deck semantics, promotion policy, gate enforcement,
and template interpretation.

This file is the canonical source of truth.
Operational guides and tooling instructions must defer to this policy.


## Deck Identity Model

The νόησις framework uses paired naming:

**Human-readable Name + Technical Version**

Names communicate intent and usage mode.
Versions communicate evolution and compatibility.


## Deck Lines

### νόησις Emergence Deck (v0.x)
- **Purpose**: Exploration, ideation, structural discovery.
- **Stability**: Experimental. Backward compatibility not guaranteed.
- **Allowed**: Partial cards, unresolved questions, speculative structure.
- **Gates**: Diagnostic. Violations signal design risk but do not block progress.
- **Change Tolerance**: High. Breaking changes acceptable.

### νόησις Canonical Deck (v1.x)
- **Purpose**: Authoritative specification and long-term preservation.
- **Stability**: Stable. Backward compatibility expected.
- **Required**: Complete cards with resolved logic and explicit decisions.
- **Gates**: Binding. Violations block downstream cards and releases.
- **Change Tolerance**: Low. Breaking changes require migration notes.


## Terminology Rules

Public-facing references should always use paired naming:
- "Emergence Deck (v0.1)"
- "Canonical Deck (v1.0)"

Version numbers alone may be used internally when context is unambiguous.


## Promotion Workflow (Emergence → Canonical)

Promotion is a deliberate act, not automatic.

### Minimum requirements:
1. All cards complete and internally consistent.
2. All gates pass under Canonical enforcement.
3. Ambiguities resolved or explicitly documented.
4. Risk analysis reviewed.
5. Version increment assigned.

### Promotion steps:
- Copy Emergence deck into Canonical directory.
- Update DeckMode headers in all cards.
- Re-run gate validation with strict enforcement.
- Record promotion note in CHANGELOG.md.

**Human approval is mandatory.**


## Gate Interpretation

Same gate rules exist in both decks.
Enforcement posture differs:

### Emergence:
- Gates warn and guide.
- Violations allowed but tracked.

### Canonical:
- Gates block progression.
- Violations must be resolved before downstream work.


## Template Interpretation

Templates are deck-agnostic.

### Usage semantics:
- **Emergence Deck**: Partial filling allowed.
- **Canonical Deck**: Complete filling required.

Templates must not encode deck-specific assumptions.


## Card Identity Rule

All cards must include:
- `DeckName`
- `DeckMode` (paired name + version)

If a card moves between decks, the DeckMode must be updated and revalidated.


## Authority

Human maintainers retain final authority.
LLMs may assist but cannot override policy or gates.
