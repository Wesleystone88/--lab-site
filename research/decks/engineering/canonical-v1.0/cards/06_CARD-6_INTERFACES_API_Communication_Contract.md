---
seed_identity:
  artifact_id: CARD-6
  seed_algo: sha256-v1
  seed: d09e277dd874cceceb4fcc2d60793ebeef69e886235e516835ecba4bea1ef10e
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:42:08Z'
  status: locked
card:
  id: CARD-6
  name: Interfaces (API Communication Contract)
  namespace: noesis.canonical.v1.0
  version: 1.0.0
  mode: ENGINEERING
  deck_mode: Canonical
dependencies:
  upstream:
  - CARD-0
  - CARD-4
  - CARD-5
  downstream:
  - CARD-7
  feeds_into:
  - CARD-11
gate:
  enforcement: strict
  rules:
  - ERROR if APIs undefined
  - ERROR if contracts incomplete
  blocks_downstream: true
ordering:
  position: 6
  required_after:
  - CARD-5
  required_before:
  - CARD-7

---
# CARD-6 — INTERFACES / API (Communication Contract)

DeckName: vóṇōs Canonical Deck
DeckMode: Canonical Deck (v1.0)

Purpose:
Define all communication boundaries.

Contains:
- Input schemas
- Output schemas
- Validation rules
- Error contracts
- Versioning policy
- Backward compatibility rules
- Authentication boundaries
- Performance expectations

Outputs:
- Interoperability guarantees.

Gate:
- No ambiguous interfaces.
