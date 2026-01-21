---
seed_identity:
  artifact_id: CARD-06
  seed_algo: sha256-v1
  seed: 920bf420f74a5ac1730cf34ecc21a7e42c83ff77b493a1492f087ef9df180ee1
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:42:03Z'
  status: locked
card:
  id: CARD-06
  name: Data Contract (Card Structure)
  namespace: noesis.emergence.v0.1
  version: 0.1.0
  mode: ENGINEERING
  deck_mode: Emergence
dependencies:
  upstream:
  - CARD-00
  - CARD-04
  - CARD-05
  downstream:
  - CARD-07
  feeds_into:
  - CARD-13
gate:
  enforcement: diagnostic
  rules:
  - WARNING if schemas undefined
  blocks_downstream: false
ordering:
  position: 6
  required_after:
  - CARD-05
  required_before:
  - CARD-07

---

# CARD-06 — DATA CONTRACT (Card Structure)

DeckName: vóṇōs Emergence Deck
DeckMode: Emergence Deck (v0.1)
CardID: CARD-06
CardName: Data Contract
Version: 0.1
Status: draft
Owner: Timothy Wesley Stone
UpstreamCards: [CARD-05]
DownstreamCards: [CARD-07]

Purpose:
Define what a card and deck look like as data.

Inputs:
- Deck Schema

Outputs:
- Portable card template

Content:
Card = Header + Sections  
Deck = Package + Ordered Cards  
LintReport = Findings list

Plain text only.

Gate:
- ERROR if non-portable formats required.
