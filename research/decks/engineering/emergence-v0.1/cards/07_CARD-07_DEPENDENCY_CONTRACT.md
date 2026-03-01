---
seed_identity:
  artifact_id: CARD-07
  seed_algo: sha256-v1
  seed: c109b840a39498e32dd5098fd4a1190e138c32e76dd7537da321285f0bbc2ea7
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:42:03Z'
  status: locked
card:
  id: CARD-07
  name: Dependency Contract
  namespace: noesis.emergence.v0.1
  version: 0.1.0
  mode: ENGINEERING
  deck_mode: Emergence
dependencies:
  upstream:
  - CARD-00
  - CARD-06
  downstream:
  - CARD-08
  feeds_into:
  - CARD-11
  - CARD-13
gate:
  enforcement: diagnostic
  rules:
  - WARNING if external dependencies not listed
  blocks_downstream: false
ordering:
  position: 7
  required_after:
  - CARD-06
  required_before:
  - CARD-08

---

# CARD-07 — DEPENDENCY CONTRACT

DeckName: vóṇōs Emergence Deck
DeckMode: Emergence Deck (v0.1)
CardID: CARD-07
CardName: Dependency Contract
Version: 0.1
Status: draft
Owner: Timothy Wesley Stone
UpstreamCards: [CARD-06]
DownstreamCards: [CARD-08]

Purpose:
Make assumptions visible.

Inputs:
- Intent
- Constraints

Outputs:
- Declared assumptions

Content:
Dependencies:
- Text editor
- Optional LLM
- Optional version control

No required tooling.

Gate:
- ERROR if mandatory dependency introduced.
