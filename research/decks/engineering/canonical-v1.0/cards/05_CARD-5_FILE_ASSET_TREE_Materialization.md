---
seed_identity:
  artifact_id: CARD-5
  seed_algo: sha256-v1
  seed: 7c0fed7690f3d7bd3bd9613a5cc811331fcd9150b5df82a8dfb707e251a252b2
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:42:08Z'
  status: locked
card:
  id: CARD-5
  name: File Tree (Materialization)
  namespace: noesis.canonical.v1.0
  version: 1.0.0
  mode: ENGINEERING
  deck_mode: Canonical
dependencies:
  upstream:
  - CARD-0
  - CARD-4
  downstream:
  - CARD-6
  feeds_into:
  - CARD-11
gate:
  enforcement: strict
  rules:
  - ERROR if directory structure undefined
  blocks_downstream: true
ordering:
  position: 5
  required_after:
  - CARD-4
  required_before:
  - CARD-6

---

# CARD-5 — FILE / ASSET TREE (Materialization)

DeckName: vóṇōs Canonical Deck
DeckMode: Canonical Deck (v1.0)

Purpose:
Translate structure into tangible organization.

Contains:
- Directory layout
- Naming conventions
- Ownership zones
- Generated vs hand-written separation
- Artifact lifecycles
- Versioning strategy
- Storage growth expectations
- Backup policy

Outputs:
- Physical build skeleton.

Gate:
- Must reflect CARD-4 structure.
