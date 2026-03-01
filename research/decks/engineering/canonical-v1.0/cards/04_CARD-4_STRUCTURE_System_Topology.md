---
seed_identity:
  artifact_id: CARD-4
  seed_algo: sha256-v1
  seed: fcd0a8f484f657852e8c56fd74fd1cfa0a88e62f3cb74bf8946ba61118ada119
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:42:08Z'
  status: locked
card:
  id: CARD-4
  name: Structure (System Topology)
  namespace: noesis.canonical.v1.0
  version: 1.0.0
  mode: ENGINEERING
  deck_mode: Canonical
dependencies:
  upstream:
  - CARD-0
  - CARD-2
  - CARD-3
  downstream:
  - CARD-5
  - CARD-6
  feeds_into:
  - CARD-5
  - CARD-6
  required_by:
  - CARD-5
gate:
  enforcement: strict
  rules:
  - ERROR if structure undefined
  - ERROR if components not named
  blocks_downstream: true
ordering:
  position: 4
  required_after:
  - CARD-3
  required_before:
  - CARD-5

---

# CARD-4 — STRUCTURE (System Topology)

DeckName: vóṇōs Canonical Deck
DeckMode: Canonical Deck (v1.0)

Purpose:
Define what exists and how it connects.

Contains:
- Component inventory
- Responsibility boundaries
- Data flows
- Control flows
- State ownership
- Trust boundaries
- Coupling points
- Failure propagation paths

Outputs:
- Conceptual architecture map.

Gate:
- No undefined responsibilities or orphan components.
