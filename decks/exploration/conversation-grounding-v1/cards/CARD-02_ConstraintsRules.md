---
seed_identity:
  artifact_id: CARD-02
  seed_algo: sha256-v1
  seed: 11610f8f3e1c8fefdb2e9979fd930f7bdc6c3e92eed0506ca254f3ff0942ef01
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:41:55Z'
  status: locked
card:
  id: CARD-02
  name: Constraints & Rules
  namespace: noesis.conversation-grounding.exploration
  version: 1.0
  mode: EXPLORATION
suggested_patterns:
  often_paired_with:
  - CARD-01
  - CARD-09
  - CARD-13
  helpful_for:
  - preventing_repeated_corrections
  - establishing_boundaries
  - builds
state_schema:
  hard_constraints: array<string>
  soft_preferences: array<string>
  forbidden_behaviors: array<string>

---

# ============================================================
# Conversation Grounding Deck — Exploration Mode
# CARD-02 — CONSTRAINTS & RULES
# Author: Timothy Wesley Stone
# License: Open / Shareable
# ============================================================

CardID: CARD-02
CardName: Constraints & Rules
Mode: Exploration
Status: draft
Owner: Timothy Wesley Stone

Purpose:
Hold explicit rules, limits, and boundaries that the conversation must respect,
so they don't need to be repeated or rediscovered.

This card answers:
"What rules are we operating under?"

Use When:
- You keep correcting the assistant on the same behavior
- There are hard limits you don't want violated
- You want consistency across many turns
- The assistant keeps 'helpfully' doing things you don't want

What This Card Holds:
- Hard constraints (must not be violated)
- Soft preferences (should usually be followed)
- Behavioral rules for the assistant
- Scope limits that are *not* the same as intent

What This Card Does NOT Do:
- It does not define goals
- It does not define steps
- It does not require completeness
- It does not block exploration unless explicitly stated

Human-Filled Fields:

A) Hard Constraints (non-negotiable):
- <rules that must always be followed>
Examples:
- "Do not rewrite my text unless I ask."
- "Do not introduce frameworks unless requested."
- "One step per message."
- "Do not optimize for politeness over clarity."

B) Soft Preferences (guidelines):
- <rules that usually apply but may bend>
Examples:
- "Prefer concrete examples."
- "Ask before switching topics."
- "Keep explanations compact unless I say 'go deep'."

C) Forbidden Behaviors:
- <things the assistant should actively avoid>
Examples:
- "Don't summarize unless asked."
- "Don't auto-complete plans."
- "Don't skip steps."

Assistant Behavior When This Card Is Active:
- Treat Hard Constraints as inviolable
- Treat Soft Preferences as defaults
- Flag conflicts instead of guessing
- Ask for clarification when rules collide

Update Rules:
- Human may add, remove, or change constraints at any time
- Assistant may suggest constraints but never enforce new ones
- Old constraints may remain listed but marked inactive if needed

Example (filled):
Hard:
- "Only do one thing per message."
- "Do not assume my end goal."

Soft:
- "Prefer short answers unless I say 'expand'."

Forbidden:
- "Don't jump ahead in plans."

Notes:
This card is often introduced early,
but it becomes especially valuable once conversations get long.
