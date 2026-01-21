# CARD-12 — STYLE & PRACTICES

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
