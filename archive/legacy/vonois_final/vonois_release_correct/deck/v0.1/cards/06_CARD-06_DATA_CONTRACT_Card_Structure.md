# CARD-06 — DATA CONTRACT (Card Structure)

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
