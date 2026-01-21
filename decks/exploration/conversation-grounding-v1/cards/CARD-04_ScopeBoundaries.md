---
seed_identity:
  artifact_id: CARD-04
  seed_algo: sha256-v1
  seed: 4f62bf1bab9249529a25975f295a4087057ed844f399ad3eac285a43806f170b
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:41:55Z'
  status: locked
card:
  id: CARD-04
  name: Scope & Boundaries
  namespace: noesis.conversation-grounding.exploration
  version: 1.0
  mode: EXPLORATION
suggested_patterns:
  often_paired_with:
  - CARD-03
  - CARD-05
  helpful_for:
  - preventing_sprawl
  - focus_depth
  - cognitive_overload
state_schema:
  in_scope: array<string>
  out_of_scope: array<string>
  soft_boundaries: array<string>
  hard_boundaries: array<string>

---

# ============================================================
# Conversation Grounding Deck — Exploration Mode
# CARD-04 — SCOPE & BOUNDARIES
# Author: Timothy Wesley Stone
# License: Open / Shareable
# ============================================================

CardID: CARD-04
CardName: Scope & Boundaries
Mode: Exploration
Status: draft
Owner: Timothy Wesley Stone

Purpose:
Define what the conversation *is* and *is not* allowed to touch,
so exploration stays meaningful instead of sprawling.

This card answers:
"What territory are we exploring — and what is outside the fence for now?"

Use When:
- The conversation starts expanding too fast
- Too many ideas compete for attention
- You feel cognitive overload or dilution
- You want depth over breadth
- You need to park ideas without losing them

What This Card Holds:
- In-scope topics
- Out-of-scope topics (temporary or permanent)
- Soft boundaries (discouraged areas)
- Hard boundaries (do not cross)
- Parking rules for off-topic ideas

What This Card Does NOT Do:
- It does not decide priorities
- It does not rank ideas
- It does not block curiosity forever
- It does not enforce structure rigidly

Human-Filled Fields:

A) In-Scope (actively explored):
- <topics/questions that belong here>
Examples:
- "Conversation grounding methods."
- "Everyday-user cognitive support."
- "Non-technical card systems."

B) Out-of-Scope (for now):
- <explicit exclusions>
Examples:
- "Implementation details."
- "LLM internals."
- "Business scaling."

C) Soft Boundaries:
- <allowed but discouraged unless relevant>
Examples:
- "Technical jargon."
- "Premature optimization."
- "Tool comparisons."

D) Hard Boundaries:
- <do-not-cross lines>
Examples:
- "No code."
- "No monetization talk yet."
- "No agent frameworks."

E) Parking Rule:
- <what to do when ideas fall outside scope>
Examples:
- "Summarize and park in a Notes or Parking card."
- "Acknowledge briefly, then return to scope."

Assistant Behavior When This Card Is Active:
- Keep responses within scope
- Flag boundary crossings gently
- Offer to park ideas rather than pursue them
- Help narrow when scope starts to blur

Update Rules:
- Scope can be adjusted at any time
- Out-of-scope items can be promoted later
- Assistant may suggest scope tightening but not enforce it

Example (filled):
In-Scope:
- "Designing conversational grounding cards."

Out-of-Scope:
- "Full product spec."

Soft Boundary:
- "Market talk."

Hard Boundary:
- "No implementation."

Parking:
- "Create a parking note."

Notes:
This card is about *focus*, not restriction.
Good exploration needs fences to go deep.
