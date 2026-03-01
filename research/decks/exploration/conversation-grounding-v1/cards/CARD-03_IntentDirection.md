---
seed_identity:
  artifact_id: CARD-03
  seed_algo: sha256-v1
  seed: d8556b01abd6e54dd2c0a877a06495b562a666b19a8b7f773bfb446b181df9e0
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:41:55Z'
  status: locked
card:
  id: CARD-03
  name: Intent & Direction
  namespace: noesis.conversation-grounding.exploration
  version: 1.0
  mode: EXPLORATION
suggested_patterns:
  often_paired_with:
  - CARD-01
  - CARD-04
  helpful_for:
  - exploratory_conversations
  - unclear_goals
  - direction_setting
state_schema:
  current_intent: string
  direction_of_travel: string
  progress_looks_like: string
  not_goals: array<string>

---

# ============================================================
# Conversation Grounding Deck — Exploration Mode
# CARD-03 — INTENT & DIRECTION
# Author: Timothy Wesley Stone
# License: Open / Shareable
# ============================================================

CardID: CARD-03
CardName: Intent & Direction
Mode: Exploration
Status: draft
Owner: Timothy Wesley Stone

Purpose:
Anchor what the conversation is fundamentally trying to do *right now*,
without locking it into a final outcome.

This card answers:
"What are we aiming at, even if we don't know how yet?"

Use When:
- The conversation feels busy but unfocused
- The assistant optimizes for the last message instead of the bigger picture
- You want exploration, but with a direction
- You're unsure of the solution but clear on the problem space

What This Card Holds:
- Current intent (not final goals)
- Direction of exploration
- What progress looks like *for now*
- What would count as "useful movement"

What This Card Does NOT Do:
- It does not define steps
- It does not freeze decisions
- It does not block pivots
- It does not require precision

Human-Filled Fields:

A) Current Intent (plain language):
- <what you are trying to accomplish or understand>
Examples:
- "Figure out what kind of product this could become."
- "Explore whether this idea is worth pursuing."
- "Clarify the shape of the problem before solving it."

B) Direction of Travel:
- <where exploration should generally move>
Examples:
- "Toward clarity, not implementation."
- "Toward feasibility, not polish."
- "Toward understanding tradeoffs."

C) What Progress Looks Like:
- <signals that the conversation is helping>
Examples:
- "Fewer contradictions."
- "Clearer language."
- "Better questions than answers."

D) What Is Explicitly NOT the Goal (right now):
- <temporary non-goals>
Examples:
- "Not writing code yet."
- "Not deciding architecture."
- "Not naming things."

Assistant Behavior When This Card Is Active:
- Optimize responses toward the stated direction
- Avoid premature solutions
- Reflect intent drift if it appears
- Ask alignment questions when intent becomes unclear

Update Rules:
- Intent may change freely
- Old intent can be retained as history if useful
- Assistant may restate intent to check alignment, but not redefine it

Example (filled):
Intent:
- "Understand how this system should feel to use."

Direction:
- "Exploratory, conceptual."

Progress:
- "Cleaner mental model."

Not-Goals:
- "No implementation decisions yet."

Notes:
This card can coexist with uncertainty.
If intent feels fuzzy, that fuzziness belongs here rather than being ignored.
