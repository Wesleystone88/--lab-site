---
seed_identity:
  artifact_id: CARD-9
  seed_algo: sha256-v1
  seed: 046343131ea8df89a780fe9863bfa501cd53d083a18e788218ce5d5ac6edb939
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:42:08Z'
  status: locked
card:
  id: CARD-9
  name: Failure & Recovery (Resilience)
  namespace: noesis.canonical.v1.0
  version: 1.0.0
  mode: ENGINEERING
  deck_mode: Canonical
dependencies:
  upstream:
  - CARD-0
  - CARD-8
  downstream:
  - CARD-10
  guards:
  - CARD-11
gate:
  enforcement: strict
  rules:
  - ERROR if failure modes undefined
  - ERROR if recovery procedures missing
  blocks_downstream: true
ordering:
  position: 9
  required_after:
  - CARD-8
  required_before:
  - CARD-10

---

# CARD-9 — FAILURE & RECOVERY (Resilience)

DeckName: vóṇōs Canonical Deck
DeckMode: Canonical Deck (v1.0)

Purpose:
Define how the system fails and heals.

Contains:
- Failure modes
- Silent failure risks
- Partial failure behavior
- Data corruption risks
- Human error risks
- Detection mechanisms
- Recovery strategies
- Rollback procedures

Outputs:
- Operational resilience plan.

Gate:
- Critical failures must have recovery paths.
