---
seed_identity:
  artifact_id: CARD-01
  seed_algo: sha256-v1
  seed: 754b5406e0287bc9836aa71f4c3d48e5cecb27272cb444d5b86a201b8601f23e
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:42:03Z'
  status: locked
card:
  id: CARD-01
  name: Write-Up (Raw Narrative Intake)
  namespace: noesis.emergence.v0.1
  version: 0.1.0
  mode: ENGINEERING
  deck_mode: Emergence
dependencies:
  upstream:
  - CARD-00
  downstream:
  - CARD-02
  feeds_into:
  - CARD-02
  - CARD-03
  required_by:
  - CARD-02
gate:
  enforcement: diagnostic
  rules:
  - ERROR if empty
  - ERROR if shorter than 50 words
  blocks_downstream: false
ordering:
  position: 1
  required_after:
  - CARD-00
  required_before:
  - CARD-02

---

# CARD-01 — WRITE-UP (Raw Narrative Intake)

DeckName: vóṇōs Emergence Deck
DeckMode: Emergence Deck (v0.1)
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
