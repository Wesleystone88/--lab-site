---
seed_identity:
  artifact_id: CARD-06
  seed_algo: sha256-v1
  seed: a607eec19652b0d70839517348259de0ef936066628a5db9815e13b8169f155e
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:41:55Z'
  status: locked
card:
  id: CARD-06
  name: Assumptions & Beliefs
  namespace: noesis.conversation-grounding.exploration
  version: 1.0
  mode: EXPLORATION
suggested_patterns:
  often_paired_with:
  - CARD-10
  - CARD-09
  helpful_for:
  - surfacing_hidden_assumptions
  - preventing_misalignment
  - clarity
state_schema:
  human_assumptions: array<string>
  assistant_assumptions: array<string>
  shared_assumptions: array<string>
  questioned_assumptions: array<string>

---

# ============================================================
# Conversation Grounding Deck — Exploration Mode
# CARD-06 — ASSUMPTIONS & BELIEFS
# Author: Timothy Wesley Stone
# License: Open / Shareable
# ============================================================

CardID: CARD-06
CardName: Assumptions & Beliefs
Mode: Exploration
Status: draft
Owner: Timothy Wesley Stone

Purpose:
Make hidden assumptions visible so the conversation doesn't quietly
build on shaky or unexamined foundations.

This card answers:
"What are we currently assuming to be true?"

Use When:
- Disagreements feel implicit rather than explicit
- The assistant or human keeps talking past each other
- You suspect different mental models are in play
- Something feels "off" but you can't pinpoint why
- You want to sanity-check the conversation's foundation

What This Card Holds:
- Assumptions (explicit or implicit)
- Beliefs guiding reasoning
- Working theories
- Default perspectives
- Temporary hypotheses

What This Card Does NOT Do:
- It does not declare truth
- It does not resolve disagreements
- It does not enforce correctness
- It does not freeze beliefs permanently

Human-Filled Fields:

A) Human Assumptions:
- <what you are assuming, knowingly or not>
Examples:
- "Most people don't want rigid systems."
- "Conversation drift is a real problem."
- "Lightweight tools outperform heavy frameworks."

B) Assistant Assumptions (as observed):
- <what the assistant seems to assume>
Examples:
- "Structure should be progressive."
- "Humans want optional guidance, not enforcement."

C) Shared Working Assumptions:
- <assumptions both sides seem aligned on>
Examples:
- "This deck is exploratory, not prescriptive."
- "Cards should reduce friction, not add it."

D) Questioned Assumptions:
- <assumptions under review>
Examples:
- "Do users actually want to manage cards?"
- "Is persistence more important than speed?"

Assistant Behavior When This Card Is Active:
- Surface assumptions explicitly
- Ask clarifying questions when assumptions conflict
- Avoid treating assumptions as facts
- Update this card when assumptions shift

Update Rules:
- Assumptions may change frequently
- Old assumptions can remain for historical context
- New assumptions should be dated or tagged if helpful

Relationship to Other Cards:
- Feeds into: Intent, Constraints, Decisions
- Often paired with: Scope & Alignment
- Useful before making commitments

Example (filled):
Human Assumption:
- "People will use this during thinking, not afterward."

Questioned:
- "Is this too abstract for everyday users?"

Notes:
This card prevents quiet divergence.
Most conversation failures start as unspoken assumptions.
