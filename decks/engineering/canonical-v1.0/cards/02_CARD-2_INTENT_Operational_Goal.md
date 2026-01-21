---
seed_identity:
  artifact_id: CARD-2
  seed_algo: sha256-v1
  seed: 6c2a7fe93ce51c68746cb2984427aa0d0e624de25bf2333ec79d816eab3a607b
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:42:08Z'
  status: locked
card:
  id: CARD-2
  name: Intent (Operational Goal)
  namespace: noesis.canonical.v1.0
  version: 1.0.0
  mode: ENGINEERING
  deck_mode: Canonical
dependencies:
  upstream:
  - CARD-0
  - CARD-1
  downstream:
  - CARD-3
  - CARD-4
  feeds_into:
  - CARD-3
  - CARD-4
  - CARD-5
  required_by:
  - CARD-3
gate:
  enforcement: strict
  rules:
  - ERROR if objectives undefined
  - ERROR if success criteria missing
  - ERROR if threats not identified
  blocks_downstream: true
ordering:
  position: 2
  required_after:
  - CARD-1
  required_before:
  - CARD-3

---

# CARD-2 — INTENT (Operational Goal)

DeckName: vóṇōs Canonical Deck
DeckMode: Canonical Deck (v1.0)

Purpose:
Convert narrative into executable purpose and boundaries.

Contains:
- Primary objective
- Non-goals
- Success criteria (measurable)
- Required capabilities
- Forbidden behaviors
- Acceptable compromises
- Explicit exclusions
- Priority ordering

Outputs:
- What must exist.
- What must never exist.

Gate:
- Must be internally consistent.
- Conflicts must be resolved or documented.
