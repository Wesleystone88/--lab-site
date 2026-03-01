---
seed_identity:
  artifact_id: CARD-3
  seed_algo: sha256-v1
  seed: 668bc232c47d915f2056506a051aa58137b9bf6ea23d6cc91604b603b07ee58c
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:42:08Z'
  status: locked
card:
  id: CARD-3
  name: Constraints (System Physics)
  namespace: noesis.canonical.v1.0
  version: 1.0.0
  mode: ENGINEERING
  deck_mode: Canonical
dependencies:
  upstream:
  - CARD-0
  - CARD-2
  downstream:
  - CARD-4
  guards:
  - CARD-4
  - CARD-6
  - CARD-7
  - CARD-8
  required_by:
  - CARD-4
gate:
  enforcement: strict
  rules:
  - ERROR if empty
  - ERROR if fewer than 3 constraints
  - Must be respected by downstream cards
  blocks_downstream: true
ordering:
  position: 3
  required_after:
  - CARD-2
  required_before:
  - CARD-4

---

# CARD-3 — CONSTRAINTS (System Physics)

DeckName: vóṇōs Canonical Deck
DeckMode: Canonical Deck (v1.0)

Purpose:
Define the immutable realities governing the system.

Contains:
- Budget limits
- Time constraints
- Hardware limits
- Latency ceilings
- API quotas
- Skill constraints
- Regulatory limits
- Data limits
- Energy / compute limits

Outputs:
- Feasible design envelope.

Gate:
- Constraints must be respected by downstream cards.
