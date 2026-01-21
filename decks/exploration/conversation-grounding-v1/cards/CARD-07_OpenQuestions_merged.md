---
seed_identity:
  artifact_id: CARD-07
  seed_algo: sha256-v1
  seed: ee7aeafa057bb0d97423c457c493b848e102361a5728a5062bf31bfe8b43ec75
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:41:55Z'
  status: locked
card:
  id: CARD-07
  name: Open Questions
  namespace: noesis.conversation-grounding.exploration
  version: 1.0
  mode: EXPLORATION
suggested_patterns:
  often_paired_with:
  - CARD-09
  - CARD-06
  helpful_for:
  - preserving_uncertainty
  - preventing_premature_closure
  - exploration
state_schema:
  active_questions: array<string>
  parked_questions: array<string>
  recently_resolved: array<string>

---

# ============================================================
# Conversation Grounding Deck — Exploration Mode
# CARD-07 — OPEN QUESTIONS (Merged)
# Author: Timothy Wesley Stone
# License: Open / Shareable
# ============================================================

CardID: CARD-07
CardName: Open Questions (Merged)
Mode: Exploration
Status: draft
Owner: Timothy Wesley Stone

Purpose:
Hold unanswered questions in a visible, stable place so they are not forgotten,
implicitly answered, or accidentally overwritten by confident-sounding replies.

Questions are assets, not bugs.

This card answers:
"What is still genuinely unknown or undecided?"

Use When:
- Questions keep resurfacing without resolution
- The assistant fills gaps with assumptions
- You want to explore without committing yet
- Multiple threads are open at once
- You want to park questions safely without losing them
- You catch yourself asking the same thing multiple times

What This Card Holds:
- Explicit unanswered questions
- Design unknowns
- Research questions
- Clarification needs
- Fork points that require future choice
- Questions intentionally left open
- Questions that have been resolved (for reference)

What This Card Does NOT Do:
- It does not require answers
- It does not force prioritization
- It does not imply ignorance is a failure
- It does not block progress elsewhere
- It does not collapse uncertainty prematurely

Human-Filled Fields:

A) Active Open Questions:
- <questions currently in play>
Examples:
- "How many cards is too many for everyday users?"
- "Do cards live inline in chat or as external files?"
- "How do we explain this without sounding technical?"
- "Should this be taught or discovered?"
- "Can everyday users actually manage cards without friction?"

B) Parked Questions (Intentionally Deferred):
- <questions acknowledged but paused>
Examples:
- "Monetization model."
- "Brand visual system."
- "Pricing model (later)."
- "Would this work in voice conversations?"

C) Recently Resolved Questions:
- <questions answered since last update — retained for reference>
Format:
- Question → Answer / Resolution
- Date (optional)

Examples:
- "Is this an engine?" → No, it's a grounding system.
- "Is this a prompt system?" → No, it's conversational structure.
- "Should cards be ordered?" → Not in Exploration Mode.

D) Question Notes:
- <context, assumptions, or constraints tied to questions>
- <patterns observed across questions>

Assistant Behavior When This Card Is Active:
- Do not assume answers to listed questions
- Surface when a response touches an open question
- Ask before implicitly resolving one
- Help explore without collapsing uncertainty
- Suggest when a question may be ready to move to Decisions
- Reference Recently Resolved section to avoid re-litigating
- Treat questions as live thinking objects, not blockers

Update Rules:
- Questions may move between sections freely
- Answers should be explicit before moving to Decisions
- Old questions may remain for historical context
- Questions can stay open indefinitely
- It's valid to move a question back from Resolved to Active

Relationship to Other Cards:
- Paired with: Decisions, Assumptions
- Feeds into: Build Plan, Scope, Intent
- Protects uncertainty from premature closure
- Complements: Idea Collection (questions vs ideas)

Example (filled):
Active:
- "Should this deck be sold as a PDF or templates first?"
- "How do we explain cards without over-teaching?"

Parked:
- "Physical index-card version?"

Recently Resolved:
- "Is this for technical users?" → No, everyday users.

Notes:
Unanswered questions are assets, not bugs.
They signal active thinking, not incompleteness.
