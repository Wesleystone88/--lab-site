---
seed_identity:
  artifact_id: CARD-09
  seed_algo: sha256-v1
  seed: 13aaf78e798cd8f5a655e7bbe424d404f41139e65db6e2d5737364f180d7e2e3
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:41:55Z'
  status: locked
card:
  id: CARD-09
  name: Decisions
  namespace: noesis.conversation-grounding.exploration
  version: 1.0
  mode: EXPLORATION
suggested_patterns:
  often_paired_with:
  - CARD-02
  - CARD-07
  - CARD-13
  helpful_for:
  - preventing_re_litigation
  - locking_progress
  - clarity
state_schema:
  locked_decisions: array<object>
  provisional_decisions: array<object>
  deferred_decisions: array<object>
  rejected_options: array<object>

---

# ============================================================
# Conversation Grounding Deck — Exploration Mode
# CARD-09 — DECISIONS (Merged)
# Author: Timothy Wesley Stone
# License: Open / Shareable
# ============================================================

CardID: CARD-09
CardName: Decisions (Merged)
Mode: Exploration
Status: draft
Owner: Timothy Wesley Stone

Purpose:
Capture decisions explicitly so they stop drifting, being re-litigated,
or silently reversed by later turns in the conversation.

This card creates a memory anchor that persists across sessions.

This card answers:
"What have we actually decided so far?"

Use When:
- The same choice keeps getting revisited
- The assistant contradicts earlier conclusions
- Progress depends on locking something in
- You want to move forward without perfect certainty
- Tradeoffs have been accepted
- You need to stop re-arguing settled points

What This Card Holds:
- Explicit decisions
- Accepted tradeoffs
- Chosen defaults
- Ruled-out alternatives (with reason)
- Temporary decisions (clearly marked)
- Reversed decisions (with history)

What This Card Does NOT Do:
- It does not claim decisions are permanent
- It does not prevent revisiting (only makes it explicit)
- It does not enforce correctness
- It does not replace Intent or Scope
- It does not force decisions

Human-Filled Fields:

A) Locked Decisions:
- <decisions treated as stable>

Format:
- Decision:
- Rationale:
- Date / Context (optional):

Examples:
- Decision: "This deck is not a prompt pack."
  Rationale: Avoids output-optimization framing.
  Context: Grounding deck definition.

- Decision: "Cards are human-owned artifacts."
  Rationale: Prevents AI override of user intent.

- Decision: "Exploration deck is lightweight and unordered."
  Rationale: Everyday users need flexibility, not rigidity.

B) Provisional Decisions:
- <decisions accepted for now, revisit later>

Format:
- Decision:
- Condition for Revisit:
- Date (optional):

Examples:
- Decision: "Start with ~13 cards."
  Revisit If: User testing shows overload.

- Decision: "Build card executes one step per turn."
  Revisit If: Users request batch mode.

C) Deferred Decisions:
- <explicitly postponed choices>

Format:
- Topic:
- Reason Deferred:
- Revisit When:

Examples:
- Topic: Exact pricing
  Reason: Need user testing first
  Revisit: After prototype feedback

- Topic: Visual design language
  Reason: Content must stabilize first
  Revisit: Before public release

D) Rejected Options:
- <explicitly ruled out paths>

Format:
- Option:
- Reason Rejected:
- Date (optional):

Examples:
- Option: "Automatic enforcement engine"
  Reason: Violates human-first principle.

- Option: "Tool-specific implementation"
  Reason: Must remain tool-agnostic.

E) Reversed Decisions (History):
- <what changed and why>

Format:
- Original Decision:
- Reversal:
- Reason:
- Date:

Examples:
- Original: "This replaces prompts."
  Reversal: "This grounds conversations."
  Reason: Clearer positioning.
  Date: 2026-01-15

F) Decision Notes:
- <nuance, tradeoffs, or risks>
- <context that matters for future changes>

Assistant Behavior When This Card Is Active:
- Respect listed decisions as current truth
- Flag when a response contradicts a decision
- Ask before proposing changes
- Treat provisional decisions as soft, not fixed
- Help clarify consequences of changing a decision
- Do not override decisions silently
- Surface conflicts with new suggestions
- Reference Reversed Decisions to avoid regression

Update Rules:
- Decisions must be explicitly written to count
- Silent assumption ≠ decision
- Changes require explicit edit or supersession note
- Old decisions may remain with status "superseded"
- Reversals must include a reason
- Decisions may move between categories
- Dates are optional but helpful for long conversations

Relationship to Other Cards:
- Resolves: Open Questions
- Constrains: Build Plan, Scope, Constraints
- Informs: Intent refinement
- Paired with: Assumptions
- Prevents: Conversational amnesia

Example (filled):
Locked:
- "This deck is chat-native and tool-agnostic."
  Rationale: Must work in any LLM interface.

Provisional:
- "Sell as a lightweight PDF first."
  Revisit: After launch feedback.

Rejected:
- "Require all cards to be filled."
  Reason: Violates Exploration Mode principle.

Notes:
Decisions create momentum.
A decision written here becomes part of the conversational ground.
