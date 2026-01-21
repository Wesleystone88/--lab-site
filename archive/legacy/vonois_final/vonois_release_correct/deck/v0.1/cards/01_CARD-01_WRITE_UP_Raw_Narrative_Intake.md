# CARD-01 — WRITE-UP (Raw Narrative Intake)

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
