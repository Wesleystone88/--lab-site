---
seed_identity:
  artifact_id: CARD-01
  seed_algo: sha256-v1
  seed: 466fa5b1d8e5b4c92bd47b67c9d6006c7ae7dc43f354127c219afc9fff4d9f36
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:41:16Z'
  status: locked
card:
  id: CARD-01
  name: Alignment Anchor
  namespace: noesis.conversation-grounding.exploration
  version: 1.0
  mode: EXPLORATION
suggested_patterns:
  often_paired_with:
  - CARD-02
  - CARD-03
  helpful_for:
  - starting_conversations
  - refocusing_drift
  - long_discussions
state_schema:
  alignment_statement: string
  collaboration_mode: string
  worth_it_if: string

---

# ============================================================
# Conversation Grounding Deck — Exploration Mode
# CARD-01 — ALIGNMENT ANCHOR
# Author: Timothy Wesley Stone
# License: Open / Shareable
# ============================================================

CardID: CARD-01
CardName: Alignment Anchor
Mode: Exploration
Status: draft
Owner: Timothy Wesley Stone

Purpose:
Hold the *current reason this conversation exists* so it doesn't silently drift
as topics expand, questions branch, or details accumulate.

This card answers:
"What are we actually trying to do together right now?"

Use When:
- A conversation is longer than a few turns
- You feel the assistant is optimizing the last message instead of the goal
- The discussion starts branching into multiple directions
- You catch yourself repeating "what I'm trying to do is…"

What This Card Holds:
- The current primary intent (not the final outcome)
- The reason this conversation is happening *at this moment*
- The frame of collaboration (explore, decide, plan, build, learn, vent, etc.)

**NOTE**: This is body content - we can add notes, examples, or explanations here 
without breaking the seed. The seed only tracks the spine (identity fields above).

What This Card Does NOT Do:
- It does not lock scope
- It does not define steps
- It does not enforce correctness
- It does not prevent evolution

This card is allowed to change over time.

Human-Filled Fields:
A) Current Alignment Statement (1–3 sentences):
- <plain language description of why this conversation exists>

B) Collaboration Mode (pick one or describe):
- explore ideas
- clarify understanding
- make a decision
- plan something
- build something
- reflect / think out loud
- other: <freeform>

C) What Would Make This Conversation "Worth It":
- <not success criteria — just a sanity check>

Assistant Behavior When This Card Is Active:
- Prefer responses that serve the Alignment Statement
- If a response would significantly diverge, flag it
- Ask for confirmation before shifting collaboration mode
- Reference this card implicitly when choosing depth and tone

Update Rules:
- The human may update this card at any time
- The assistant may suggest updates but may NOT change it unilaterally
- Old alignment statements may be preserved as history if helpful

Example (filled):
Alignment:
"I'm trying to design a lightweight system that keeps AI conversations coherent
without turning them into rigid workflows."

Collaboration Mode:
explore ideas

Worth It If:
"I leave with something I can actually use in real chats."

Notes:
This is usually the FIRST card introduced in a conversation,
but it can also be reintroduced later to re-center things.
