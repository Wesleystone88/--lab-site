# ============================================================
# vónoįs Artifact Deck v0.1
# Structured Emergence Protocol for Human + LLM Collaboration
# Owner: Timothy Wesley Stone
# License: Open / Shareable
# ============================================================

This deck defines a portable, human-first method for turning vague ideas into
structured, persistent artifacts that survive LLM context loss, model switching,
and team collaboration.

No engine is required to use this deck.
It can be used purely through copy/paste, Markdown files, and conversation flow.

============================================================
PACKAGE (Envelope — Context Selector, NOT a Card)
============================================================

PackageType:
- <Software | Research | Hardware | Knowledge | Simulation | Other>

OutputsEnabled:
- [ ] Code
- [ ] Documentation
- [ ] Models
- [ ] Experiments
- [ ] Schematics
- [ ] Other

Notes:
The PACKAGE determines which downstream cards are active.
The deck itself remains package-agnostic.

Gate:
- PACKAGE must be declared before CARD-01 exists.


============================================================
CARD-00 — DECK SCHEMA (Meta-Card)
============================================================
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


============================================================
CARD-01 — WRITE-UP (Raw Narrative Intake)
============================================================
CardID: CARD-01
CardName: Write-Up
Version: 0.1
Status: draft
Owner: Timothy Wesley Stone
UpstreamCards: [CARD-00]
DownstreamCards: [CARD-02]

Purpose:
Capture the messy human story before structure is imposed.

Inputs:
- Human notes, chats, brainstorming
- LLM conversation output

Outputs:
- Narrative source for Intent

Content:
Problem Story:
- Build a portable artifact deck that lets humans and LLMs collaborate
  without losing intent, structure, or decisions across sessions.

Why Now:
- LLM workflows drift.
- Context windows reset.
- Decisions get re-invented.
- Structure is implicit instead of explicit.

Examples:
1) Start with a vague idea, gradually fill cards with an LLM.
2) Lose a chat session, continue by pasting existing cards.
3) Switch models without losing project memory.
4) Collaborate asynchronously through shared cards.

Risks:
- Over-structure slows creativity.
- Card overlap creates confusion.
- Users treat deck as bureaucracy.

Assumptions:
- Humans remain decision owners.
- LLMs assist synthesis.
- Plain text portability matters.

Non-Goals:
- No heavy tooling required.
- No forced automation.
- No proprietary formats.

Gate:
- ERROR if empty.
- ERROR if fewer than 3 examples.


============================================================
CARD-02 — INTENT (Compiled Meaning)
============================================================
CardID: CARD-02
CardName: Intent
Version: 0.1
Status: draft
Owner: Timothy Wesley Stone
UpstreamCards: [CARD-01]
DownstreamCards: [CARD-03]

Purpose:
Stabilize meaning into explicit commitments.

Inputs:
- CARD-01 WRITE-UP

Outputs:
- Objectives
- Success criteria
- Scope and non-goals

Content:
Objectives:
O1. Provide a universal deck usable without tooling.
O2. Preserve intent across LLM sessions and models.
O3. Make structure explicit and shareable.
O4. Allow progressive refinement without drift.

Success Criteria:
SC1. Deck usable purely as Markdown templates.
SC2. Users can resume work by pasting cards.
SC3. Cards enforce clarity before implementation.

Actors:
- Human builder
- LLM collaborator
- Future contributors

Non-Goals:
- No locked ecosystem.
- No forced runtime engine.
- No opaque automation.

Scope:
- Human-first protocol.
- Optional automation later.

Gate:
- ERROR if objectives lack success criteria.


============================================================
CARD-03 — CONSTRAINTS (System Physics)
============================================================
CardID: CARD-03
CardName: Constraints
Version: 0.1
Status: draft
Owner: Timothy Wesley Stone
UpstreamCards: [CARD-02]
DownstreamCards: [CARD-04]

Purpose:
Define immutable laws.

Inputs:
- CARD-02 INTENT

Outputs:
- Hard invariants
- Soft targets

Content:
Hard Invariants:
I1. No silent decisions.
I2. Deck usable without software.
I3. Cards remain plain text.
I4. Structure is typed, not generic.
I5. Humans retain authority.

Soft Targets:
T1. Lightweight.
T2. Readable.
T3. Minimal ceremony.

Gate:
- ERROR if fewer than 3 invariants.


============================================================
CARD-04 — ARCHITECTURE (Conceptual System Shape)
============================================================
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


============================================================
CARD-05 — INTERFACE CONTRACT (Human IO)
============================================================
CardID: CARD-05
CardName: Interface Contract
Version: 0.1
Status: draft
Owner: Timothy Wesley Stone
UpstreamCards: [CARD-04]
DownstreamCards: [CARD-06]

Purpose:
Define how users interact with the deck.

Inputs:
- Card text

Outputs:
- Updated cards
- Shared artifacts

Content:
Interfaces:
- Copy / paste into LLM
- File editing
- Git sharing
- Text export

Errors:
- Missing cards
- Contradictions
- Skipped order

Gate:
- ERROR if interaction unclear.


============================================================
CARD-06 — DATA CONTRACT (Card Structure)
============================================================
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


============================================================
CARD-07 — DEPENDENCY CONTRACT
============================================================
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


============================================================
CARD-08 — SAFETY & SECURITY MODEL
============================================================
CardID: CARD-08
CardName: Safety Model
Version: 0.1
Status: draft
Owner: Timothy Wesley Stone
UpstreamCards: [CARD-07]
DownstreamCards: [CARD-09]

Purpose:
Protect integrity and prevent drift.

Threats:
- Hallucinated structure
- Silent edits
- Over-automation

Mitigations:
- Versioning
- Human review
- Explicit gates

Gate:
- ERROR if no threats listed.


============================================================
CARD-09 — PROJECT TOPOLOGY
============================================================
CardID: CARD-09
CardName: Project Topology
Version: 0.1
Status: draft
Owner: Timothy Wesley Stone
UpstreamCards: [CARD-08]
DownstreamCards: [CARD-10]

Purpose:
Define how cards are organized.

Content:
- Single file or folder of cards
- Numeric prefixes preserve order

Gate:
- WARNING if layout unclear.


============================================================
CARD-10 — TESTING STRATEGY
============================================================
CardID: CARD-10
CardName: Testing Strategy
Version: 0.1
Status: draft
Owner: Timothy Wesley Stone
UpstreamCards: [CARD-09]
DownstreamCards: [CARD-11]

Purpose:
Validate correctness manually or with tools.

Content:
Checklist review of cards and consistency.

Gate:
- WARNING if no review process.


============================================================
CARD-11 — DEPLOYMENT MODEL
============================================================
CardID: CARD-11
CardName: Deployment Model
Version: 0.1
Status: draft
Owner: Timothy Wesley Stone
UpstreamCards: [CARD-10]
DownstreamCards: [CARD-12]

Purpose:
Define how deck is shared.

Content:
- Git
- Gist
- PDF
- Copy/paste

Gate:
- WARNING if sharing path unclear.


============================================================
CARD-12 — STYLE & PRACTICES
============================================================
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


============================================================
CARD-13 — IMPLEMENTATION
============================================================
CardID: CARD-13
CardName: Implementation
Version: 0.1
Status: draft
Owner: Timothy Wesley Stone
UpstreamCards: [CARD-12]
DownstreamCards: []

Purpose:
The deck itself is the artifact.

Outputs:
- Shareable deck
- Templates
- Examples

Gate:
- ERROR if deck incomplete.
