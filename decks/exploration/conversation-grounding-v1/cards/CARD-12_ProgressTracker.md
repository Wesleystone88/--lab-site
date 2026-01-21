---
seed_identity:
  artifact_id: CARD-12
  seed_algo: sha256-v1
  seed: 5969ce10c47af4b81909374d89bfbc3729193514d98c5745b1636b3835532e3f
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:41:55Z'
  status: locked
card:
  id: CARD-12
  name: Progress Tracker
  namespace: noesis.conversation-grounding.exploration
  version: 1.0
  mode: EXPLORATION
suggested_patterns:
  often_paired_with:
  - CARD-11
  - CARD-09
  helpful_for:
  - maintaining_momentum
  - preventing_circles
  - visibility
state_schema:
  completed: array<object>
  in_progress: array<object>
  upcoming: array<object>
  blocked: array<object>

---

# ============================================================
# Conversation Grounding Deck — Exploration Mode
# CARD-12 — PROGRESS TRACKER
# Author: Timothy Wesley Stone
# License: Open / Shareable
# ============================================================

CardID: CARD-12
CardName: Progress Tracker
Mode: Exploration
Status: draft
Owner: Timothy Wesley Stone

Purpose:
Track what's been covered, what's active, and what remains,
so the conversation maintains momentum and avoids circling back unnecessarily.

This card answers:
"Where have we been, where are we now, and where are we going?"

Use When:
- The conversation feels like it's repeating itself
- You've lost track of what's already been addressed
- Multiple threads are active and competing for attention
- You want to prevent drift by maintaining visible progress
- You need to see the shape of the work ahead
- You want to celebrate completed milestones

What This Card Holds:
- Completed topics, tasks, or decisions
- Active threads or work in progress
- Upcoming work (next steps, backlog)
- Blocked or waiting items (dependencies, deferrals)
- Milestones or checkpoints
- Progress notes or observations

What This Card Does NOT Do:
- It does not enforce a schedule
- It does not prioritize automatically
- It does not block exploration
- It does not replace Intent or Build Card
- It does not assume linear progression

Human-Filled Fields:

A) Completed:
- <topics, tasks, or threads finished>

Format:
- [X] Topic / Task
- Date (optional)
- Outcome (optional)

Examples:
- [X] Defined Exploration Mode vs Engineering Mode
- [X] Created CARD-01 through CARD-06
- [X] Locked core design decisions
- [X] Finalized card naming conventions (2026-01-20)

B) In Progress:
- <active work or threads>

Format:
- [ ] Topic / Task
- Status note (optional)

Examples:
- [ ] Merging CARD-07 and CARD-10 (Open Questions)
  Status: Draft complete, review pending
- [ ] Creating CARD-10 (Definitions & Terminology)
  Status: Structure defined, examples in progress
- [ ] Finalizing handoff protocol
  Status: Card drafted

C) Upcoming / Next:
- <work planned but not yet started>

Format:
- [ ] Topic / Task
- Priority (optional): high / medium / low
- Depends on (optional)

Examples:
- [ ] Finalize full deck export format
  Priority: high
- [ ] User testing of card system
  Depends on: Deck completion
- [ ] Create public-facing README
  Priority: medium

D) Blocked / Waiting:
- <work paused due to dependencies or decisions>

Format:
- [!] Topic / Task
- Reason blocked:
- Unblock condition:

Examples:
- [!] Pricing model
  Reason: Needs user feedback
  Unblock: After prototype launch

- [!] Visual design system
  Reason: Content must stabilize first
  Unblock: After all cards finalized

E) Milestones:
- <significant checkpoints or achievements>

Format:
- Milestone:
- Status: complete / in-progress / upcoming
- Date (if complete):

Examples:
- Milestone: Core deck concept defined
  Status: complete
  Date: 2026-01-15

- Milestone: All 13 cards drafted
  Status: in-progress
  Date: TBD

- Milestone: First external user test
  Status: upcoming

F) Progress Notes:
- <observations, patterns, velocity, blockers>

Examples:
- "Card creation accelerating — structure is well-defined now."
- "Naming conventions took longer than expected but worth it."
- "Exploration Mode principles are holding up across all cards."

Assistant Behavior When This Card Is Active:
- Reference Completed items to avoid rehashing
- Update In Progress status when work advances
- Suggest moving items between sections as appropriate
- Flag when conversation circles back to completed topics
- Help identify when something should move to Blocked
- Celebrate milestones explicitly
- Use this card to maintain conversational momentum

Update Rules:
- Update frequently (every major turn or topic shift)
- Move items between sections as state changes
- Completed items may be archived or retained for reference
- Dates are optional but helpful for long conversations
- It's valid to move something from Upcoming back to Blocked
- Progress Notes should reflect current state, not accumulate indefinitely

Relationship to Other Cards:
- Feeds into: Context Handoff (state snapshot)
- Consumes: Build Card (stepwise progress), Decisions, Open Questions
- Complements: Scope & Boundaries (what's in/out)
- Enables: Momentum, anti-drift, milestone visibility
- Paired with: Intent (progress toward what?)

Example (filled):
Completed:
- [X] Defined all 13 Exploration Mode cards
- [X] Merged CARD-07 (Open Questions)

In Progress:
- [ ] Creating CARD-10 (Definitions)
  Status: Examples being refined

Upcoming:
- [ ] Full deck export
- [ ] Public README

Blocked:
- [!] User testing
  Reason: Deck incomplete
  Unblock: After all cards finalized

Milestones:
- Core deck design: complete (2026-01-15)
- All cards drafted: in-progress

Notes:
This card prevents the "what have we done?" question.
It turns invisible progress into visible momentum.
