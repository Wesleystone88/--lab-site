---
seed_identity:
  artifact_id: CARD-05
  seed_algo: sha256-v1
  seed: 5d9c5f09dce708780b51dad81a9845a431936ef947e429e20ee8ac6f4aee804d
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:42:03Z'
  status: locked
card:
  id: CARD-05
  name: Interface Contract (Human I/O)
  namespace: noesis.emergence.v0.1
  version: 0.1.0
  mode: ENGINEERING
  deck_mode: Emergence
dependencies:
  upstream:
  - CARD-00
  - CARD-04
  downstream:
  - CARD-06
  feeds_into:
  - CARD-06
  - CARD-13
gate:
  enforcement: diagnostic
  rules:
  - WARNING if no input/output defined
  blocks_downstream: false
ordering:
  position: 5
  required_after:
  - CARD-04
  required_before:
  - CARD-06

---

# CARD-05 — INTERFACE CONTRACT (Human IO)
DeckName: vóṇōs Emergence Deck
DeckMode: Emergence Deck (v0.1)CardID: CARD-05
CardName: Interface Contract
Version: 0.1
Status: draft
Owner: Timothy Wesley Stone
UpstreamCards: [CARD-04]
DownstreamCards: [CARD-06]

Purpose:
Define how users interact with the deck.

Inputs:
- Card text

Outputs:
- Updated cards
- Shared artifacts

Content:
Interfaces:
- Copy / paste into LLM
- File editing
- Git sharing
- Text export

Errors:
- Missing cards
- Contradictions
- Skipped order

Gate:
- ERROR if interaction unclear.
