---
seed_identity:
  artifact_id: CARD-11
  seed_algo: sha256-v1
  seed: eabf67e53eea09c61de51a8d7cc2986fead657c766ec6833e79087106ad468f3
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:41:55Z'
  status: locked
card:
  id: CARD-11
  name: Context Handoff
  namespace: noesis.conversation-grounding.exploration
  version: 1.0
  mode: EXPLORATION
suggested_patterns:
  often_paired_with:
  - CARD-12
  - CARD-13
  helpful_for:
  - session_resume
  - context_preservation
  - collaboration_handoff
state_schema:
  current_state_summary: string
  active_cards: array<string>
  last_activity: string
  key_decisions_snapshot: array<string>

---

# ============================================================
# Conversation Grounding Deck — Exploration Mode
# CARD-11 — CONTEXT HANDOFF
# Author: Timothy Wesley Stone
# License: Open / Shareable
# ============================================================

CardID: CARD-11
CardName: Context Handoff
Mode: Exploration
Status: draft
Owner: Timothy Wesley Stone

Purpose:
Package conversation state for session resume, model switching, or handoff to collaborators.

Prevent context collapse when conversations reset or transition.

This card answers:
"What does someone need to know to pick up where this conversation left off?"

Use When:
- Chat session is about to reset (token limit, deliberate restart)
- Switching between LLM models or interfaces
- Handing off to another person or team
- Resuming after a break (days, weeks, months)
- Archiving conversation state for later retrieval
- You want to preserve momentum across discontinuities

What This Card Holds:
- Current state summary (where the conversation is now)
- Active cards in use (which cards are currently guiding the conversation)
- Where the conversation left off (last activity, thread, or topic)
- Key decisions and constraints snapshot
- Open threads or incomplete work
- Next intended steps (if known)
- Handoff-specific notes (context receiver needs)

What This Card Does NOT Do:
- It does not replace full conversation history
- It does not guarantee perfect continuity
- It does not enforce resumption order
- It does not lock future direction
- It does not capture every detail (intentionally compressed)

Human-Filled Fields:

A) Current State Summary:
- <where the conversation is right now — 2–5 sentences>

Examples:
- "We're designing a Conversation Grounding Deck for everyday users.
   13 cards defined. Currently finalizing merge requirements for 5 new cards.
   Intent is clear, structure is stable, examples are being refined."

- "Mid-build on a stepwise execution system. Step 3 of 7 complete.
   Constraints locked, next step is testing card sequencing."

B) Active Cards in Use:
- <which cards are currently guiding the conversation>

Format:
- CARD-XX: [Card Name] — (role in conversation)

Examples:
- CARD-01: Alignment Anchor — Defines current purpose
- CARD-02: Constraints & Rules — Enforces no-rewrite rule
- CARD-09: Decisions — Holds locked design choices
- CARD-13: Build Card — Currently executing Step 5

C) Last Activity / Where Conversation Left Off:
- <specific point of departure>

Examples:
- "Just completed CARD-07 merge. About to start CARD-09."
- "Waiting for human feedback on Build Step 4 output."
- "Paused mid-discussion about card naming conventions."

D) Key Decisions & Constraints Snapshot:
- <critical context for resumption — abbreviated>

Examples:
Decisions:
- This is Exploration Mode (no gates, no ordering)
- Cards must include examples
- Human owns all final choices

Constraints:
- No placeholders (TBD, TODO forbidden)
- One step per message in builds
- Avoid jargon unless defined

E) Open Threads / Incomplete Work:
- <active topics or tasks not yet resolved>

Examples:
- "Need to finalize CARD-12 structure."
- "Unresolved question: How many cards is too many?"
- "Deferred decision: Pricing model."

F) Next Intended Steps (Optional):
- <where the conversation was heading>

Examples:
- "Next: Review merged CARD-09, then proceed to new card creation."
- "Next: Execute Build Step 6."
- "Next: User testing of card structure."

G) Handoff Notes:
- <anything the context receiver specifically needs to know>

Examples:
- "User prefers concise responses unless asked to expand."
- "Avoid suggesting tools or frameworks."
- "This deck is NOT technical — keep language accessible."
- "Human may paste this card to resume after session reset."

Assistant Behavior When This Card Is Active:
- Use this card to reconstruct conversational ground
- Prioritize information in this card over guessing context
- Ask clarifying questions if handoff context is insufficient
- Do not assume continuity beyond what's explicitly stated
- Treat this card as authoritative snapshot, not perfect history
- Update this card before major transitions if requested

Update Rules:
- Update whenever conversation state significantly changes
- Update before deliberate pauses or handoffs
- Overwrite or version (human choice)
- Compress ruthlessly — this is a summary, not a transcript
- Include only what's needed for effective resumption

Relationship to Other Cards:
- Consumes: All active cards
- Summarizes: Decisions, Constraints, Open Questions, Intent
- Enables: Session continuity, collaboration, archiving
- Paired with: Build Card (for stepwise execution state)

Example (filled):
Current State:
"Designing Conversation Grounding Deck for everyday users. 
13 cards complete. Finalizing 5 new merged/created cards now."

Active Cards:
- CARD-01: Alignment Anchor (exploration intent)
- CARD-09: Decisions (locked design choices)

Last Activity:
"Just finished CARD-07 merge. Moving to CARD-09 next."

Decisions Snapshot:
- Exploration Mode (no gates)
- Human-owned artifacts
- Examples required in all cards

Open Threads:
- Finalize naming for CARD-10, 11, 12

Next Steps:
- Complete remaining 4 card files
- Review full deck structure

Handoff Notes:
- User wants concise, direct responses
- Avoid over-teaching or jargon

Notes:
This card is the escape hatch from conversational amnesia.
When sessions reset, paste this card first.
