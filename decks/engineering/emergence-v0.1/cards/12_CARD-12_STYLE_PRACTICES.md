---
seed_identity:
  artifact_id: CARD-12
  seed_algo: sha256-v1
  seed: 59c77d5ff4be8c8d2f3cd9da3011c7da3587d71d016cf87b0516a59cb6eab4a1
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:42:03Z'
  status: locked
card:
  id: CARD-12
  name: Style & Practices
  namespace: noesis.emergence.v0.1
  version: 0.1.0
  mode: ENGINEERING
  deck_mode: Emergence
dependencies:
  upstream:
  - CARD-00
  - CARD-11
  downstream:
  - CARD-13
  guards:
  - CARD-13
gate:
  enforcement: diagnostic
  rules:
  - INFO style guide recommended
  blocks_downstream: false
ordering:
  position: 12
  required_after:
  - CARD-11
  required_before:
  - CARD-13

---

# CARD-12 — STYLE & PRACTICES

DeckName: vóṇōs Emergence Deck
DeckMode: Emergence Deck (v0.1)
CardID: CARD-12
CardName: Style & Practices
Version: 0.1
Status: draft
Owner: Timothy Wesley Stone
UpstreamCards: [CARD-11]
DownstreamCards: [CARD-13]

Purpose:
Maintain clarity, rigor, and depth of specification across all cards.

Inputs:
- All upstream cards

Outputs:
- Authoring standards

Content:

Style Rules:
- Plain language
- Explicit over clever
- Structured sections
- Avoid vague phrasing

Specification Depth Standards:
- Cards must include full decision trees where applicable.
- Avoid placeholders ("TBD", "later", etc.).
- Every rule specifies:
  - Condition
  - Action
  - Expected outcome
  - Failure behavior
- Tradeoffs documented explicitly.

Clarity Rules:
- Long cards acceptable when clarity improves.
- Subsections encouraged for readability.

LLM Usage:
- Drafts reviewed before locking.
- No blind auto-merging.

Gate:
- ERROR if card lacks operational depth.
- WARNING for readability issues.
