# CARD-04 — ARCHITECTURE (Conceptual System Shape)

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
