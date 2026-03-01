---
seed_identity:
  artifact_id: CARD-04
  seed_algo: sha256-v1
  seed: d66609bbd3a14f38183d88388b5e623b5d21e3cf1d08707560da474cfdec3eb4
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:42:03Z'
  status: locked
card:
  id: CARD-04
  name: Architecture (Conceptual System Shape)
  namespace: noesis.emergence.v0.1
  version: 0.1.0
  mode: ENGINEERING
  deck_mode: Emergence
dependencies:
  upstream:
  - CARD-00
  - CARD-02
  - CARD-03
  downstream:
  - CARD-05
  - CARD-06
  feeds_into:
  - CARD-05
  - CARD-06
  - CARD-09
  required_by:
  - CARD-05
gate:
  enforcement: diagnostic
  rules:
  - ERROR if no components defined
  blocks_downstream: false
ordering:
  position: 4
  required_after:
  - CARD-03
  required_before:
  - CARD-05

---

# CARD-04 — ARCHITECTURE (Conceptual System Shape)

DeckName: vóṇōs Emergence Deck
DeckMode: Emergence Deck (v0.1)
CardID: CARD-04
CardName: Architecture
Version: 0.1
Status: draft
Owner: Timothy Wesley Stone
UpstreamCards: [CARD-03]
DownstreamCards: [CARD-05]

Purpose:
Define conceptual flow even without code.

Inputs:
- Intent
- Constraints

Outputs:
- Component roles
- Flow model

Content:
Components:
- Deck (cards)
- Human (controller)
- LLM (assistant)
- Optional tools

Flow:
Write-Up → Intent → Constraints → Structure → Implementation

Trust Boundary:
- LLM suggests.
- Human approves.

Gate:
- ERROR if flow unclear.
