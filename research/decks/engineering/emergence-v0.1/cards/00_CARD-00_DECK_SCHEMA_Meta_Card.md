---
seed_identity:
  artifact_id: CARD-00
  seed_algo: sha256-v1
  seed: 5937c764fd45b0e696068945a2a56a9b39f2d205e6f428d1f80478ad788ad17d
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:42:03Z'
  status: locked
card:
  id: CARD-00
  name: Deck Schema (Meta-Card)
  namespace: noesis.emergence.v0.1
  version: 0.1.0
  mode: ENGINEERING
  deck_mode: Emergence
dependencies:
  upstream: []
  downstream:
  - CARD-01
  - CARD-02
  - CARD-03
  - CARD-04
  - CARD-05
  - CARD-06
  - CARD-07
  - CARD-08
  - CARD-09
  - CARD-10
  - CARD-11
  - CARD-12
  - CARD-13
  required_by:
  - CARD-01
gate:
  enforcement: strict
  blocks_downstream: true
ordering:
  position: 0
  required_before:
  - CARD-01

---

# CARD-00 — DECK SCHEMA (Meta-Card)

DeckName: vóṇōs Emergence Deck
DeckMode: Emergence Deck (v0.1)
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
