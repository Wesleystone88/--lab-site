---
seed_identity:
  artifact_id: CARD-1
  seed_algo: sha256-v1
  seed: 84ca2ef55223af43a9d6a184c2f77ec1d8762b870455aab99ce1df43c90b13d8
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:42:08Z'
  status: locked
card:
  id: CARD-1
  name: Write-Up (Narrative Anchor)
  namespace: noesis.canonical.v1.0
  version: 1.0.0
  mode: ENGINEERING
  deck_mode: Canonical
dependencies:
  upstream:
  - CARD-0
  downstream:
  - CARD-2
  feeds_into:
  - CARD-2
  - CARD-3
  required_by:
  - CARD-2
gate:
  enforcement: strict
  rules:
  - ERROR if empty
  - ERROR if no context provided
  blocks_downstream: true
ordering:
  position: 1
  required_after:
  - CARD-0
  required_before:
  - CARD-2

---

# CARD-1 — WRITE-UP (Narrative Anchor)

DeckName: vóṇōs Canonical Deck
DeckMode: Canonical Deck (v1.0)

Purpose:
Capture the raw human story before formalization.
Preserves meaning, motivation, and context.

Contains:
- Problem narrative
- Why this exists now
- Who benefits
- Emotional drivers
- Risks and fears
- Success vision
- Example scenarios
- Rough ideas and metaphors

Rules:
- Informal language allowed.
- Contradictions allowed.
- Versioned over time.

Outputs:
- Shared mental grounding.
- Vocabulary seed.

Gate:
- Must exist before CARD-2.
