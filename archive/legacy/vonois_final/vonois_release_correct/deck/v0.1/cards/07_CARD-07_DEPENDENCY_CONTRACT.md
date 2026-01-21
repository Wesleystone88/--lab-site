# CARD-07 — DEPENDENCY CONTRACT

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
