# CARD-00 — DECK SCHEMA (Meta-Card)

CardID: CARD-00
CardName: Deck Schema
Version: 0.1
Status: locked
Owner: Timothy Wesley Stone
UpstreamCards: []
DownstreamCards: [CARD-01..CARD-13]

Purpose:
Define what a card is, how cards are ordered, how validation works,
and how humans/LLMs interact with the deck.

Inputs:
- PACKAGE

Outputs:
- Canonical card list
- Ordering rules
- Validation semantics
- LLM interaction policy

Content:

Required Card Header Fields:
- CardID
- CardName
- Version
- Status
- Owner
- UpstreamCards
- DownstreamCards

Required Card Sections:
- Purpose
- Inputs
- Outputs
- Content
- Gate (Validation Rules)
- Notes (optional)

Canonical Card Set:
CARD-01 WRITE-UP  
CARD-02 INTENT  
CARD-03 CONSTRAINTS  
CARD-04 ARCHITECTURE  
CARD-05 INTERFACE CONTRACT  
CARD-06 DATA CONTRACT  
CARD-07 DEPENDENCY CONTRACT  
CARD-08 SAFETY & SECURITY MODEL  
CARD-09 PROJECT TOPOLOGY  
CARD-10 TESTING STRATEGY  
CARD-11 DEPLOYMENT MODEL  
CARD-12 STYLE & PRACTICES  
CARD-13 IMPLEMENTATION  

Ordering:
WRITE-UP → INTENT → CONSTRAINTS → ARCHITECTURE → INTERFACE → DATA → DEPENDENCY → SAFETY → TOPOLOGY → TESTING → DEPLOYMENT → STYLE → IMPLEMENTATION

Reference Rules:
- Upstream references allowed.
- Same-level references require explicit declaration.
- Downstream references prohibited.

Validation Severity:
- ERROR = blocks downstream cards
- WARNING = logged but allowed
- INFO = advisory

LLM Rules:
LLMs may draft, summarize, and suggest.
LLMs may NOT change ordering, gates, or constraints without human approval.

Specification Depth Requirement:
All cards must contain full, explicit specification trees:
- Concrete rules
- Decision logic
- Operational constraints
- Failure modes where applicable
- Explicit assumptions and tradeoffs

Cards must be sufficient for implementation without guesswork.

Gate:
- ERROR if any required section missing.
- ERROR if ordering violated.
- ERROR if card lacks concrete operational detail.
