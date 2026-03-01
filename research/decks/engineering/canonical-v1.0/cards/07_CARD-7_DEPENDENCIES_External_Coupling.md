---
seed_identity:
  artifact_id: CARD-7
  seed_algo: sha256-v1
  seed: 8cb5babdb2aeca03c711b639d30e0fcb3a3cb92d553a3e5685e71db5ac120e8a
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:42:08Z'
  status: locked
card:
  id: CARD-7
  name: Dependencies (External Coupling)
  namespace: noesis.canonical.v1.0
  version: 1.0.0
  mode: ENGINEERING
  deck_mode: Canonical
dependencies:
  upstream:
  - CARD-0
  - CARD-6
  downstream:
  - CARD-8
  feeds_into:
  - CARD-8
  - CARD-11
gate:
  enforcement: strict
  rules:
  - ERROR if dependencies not listed
  - ERROR if versions unspecified
  blocks_downstream: true
ordering:
  position: 7
  required_after:
  - CARD-6
  required_before:
  - CARD-8

---

# CARD-7 — DEPENDENCIES (External Coupling)

DeckName: vóṇōs Canonical Deck
DeckMode: Canonical Deck (v1.0)

Purpose:
Expose external reliance and fragility.

Contains:
- Libraries
- Services
- Models
- Vendors
- Hardware
- Licenses
- Update risks
- Lock-in risks
- Replacement strategies

Outputs:
- Dependency risk map.

Gate:
- All dependencies must be justified.
