---
seed_identity:
  artifact_id: CARD-02
  seed_algo: sha256-v1
  seed: c4e332487698635fdd030d76ba026783fc843abc2afa2da5e1e901db9a610f92
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:42:03Z'
  status: locked
card:
  id: CARD-02
  name: Intent (Compiled Meaning)
  namespace: noesis.emergence.v0.1
  version: 0.1.0
  mode: ENGINEERING
  deck_mode: Emergence
dependencies:
  upstream:
  - CARD-00
  - CARD-01
  downstream:
  - CARD-03
  - CARD-04
  feeds_into:
  - CARD-03
  - CARD-04
  - CARD-05
  required_by:
  - CARD-03
gate:
  enforcement: diagnostic
  rules:
  - ERROR if fewer than 3 objectives
  - WARNING if no success criteria
  blocks_downstream: false
ordering:
  position: 2
  required_after:
  - CARD-01
  required_before:
  - CARD-03

---
# CARD-02 — INTENT (Compiled Meaning)

DeckName: vóṇōs Emergence Deck
DeckMode: Emergence Deck (v0.1)
CardID: CARD-02
CardName: Intent
Version: 0.1
Status: draft
Owner: Timothy Wesley Stone
UpstreamCards: [CARD-01]
DownstreamCards: [CARD-03]

Purpose:
Stabilize meaning into explicit commitments.

Inputs:
- CARD-01 WRITE-UP

Outputs:
- Objectives
- Success criteria
- Scope and non-goals

Content:
Objectives:
O1. Provide a universal deck usable without tooling.
O2. Preserve intent across LLM sessions and models.
O3. Make structure explicit and shareable.
O4. Allow progressive refinement without drift.

Success Criteria:
SC1. Deck usable purely as Markdown templates.
SC2. Users can resume work by pasting cards.
SC3. Cards enforce clarity before implementation.

Actors:
- Human builder
- LLM collaborator
- Future contributors

Non-Goals:
- No locked ecosystem.
- No forced runtime engine.
- No opaque automation.

Scope:
- Human-first protocol.
- Optional automation later.

Gate:
- ERROR if objectives lack success criteria.
