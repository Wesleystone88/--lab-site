---
seed_identity:
  artifact_id: CARD-10
  seed_algo: sha256-v1
  seed: a20c96d4b96b8bad9f75c50462ac347c4879c7f2c271dd177ae9c536ac597672
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:41:55Z'
  status: locked
card:
  id: CARD-10
  name: Definitions & Terminology
  namespace: noesis.conversation-grounding.exploration
  version: 1.0
  mode: EXPLORATION
suggested_patterns:
  often_paired_with:
  - CARD-06
  - CARD-03
  helpful_for:
  - preventing_miscommunication
  - establishing_vocabulary
  - clarity
state_schema:
  active_definitions: array<object>
  disambiguations: array<object>
  terms_to_avoid: array<object>

---

# ============================================================
# Conversation Grounding Deck — Exploration Mode
# CARD-10 — DEFINITIONS & TERMINOLOGY
# Author: Timothy Wesley Stone
# License: Open / Shareable
# ============================================================

CardID: CARD-10
CardName: Definitions & Terminology
Mode: Exploration
Status: draft
Owner: Timothy Wesley Stone

Purpose:
Establish shared vocabulary to prevent talking past each other.

Capture context-specific meanings, disambiguations, and working definitions
so the conversation doesn't silently shift terms or assume shared understanding.

This card answers:
"What do we mean when we say X?"

Use When:
- The same word is being used in different ways
- Jargon or metaphors need anchoring
- The assistant misinterprets your language
- You catch yourself explaining the same term repeatedly
- Precision matters but hasn't been established yet
- Technical and everyday language are colliding

What This Card Holds:
- Key terms and their working definitions
- Disambiguations (when one word has multiple meanings)
- Context-specific meanings that differ from common usage
- Metaphors or shorthand you're using consistently
- Terms to actively avoid (and why)
- Evolving definitions (terms still being clarified)

What This Card Does NOT Do:
- It does not claim universal truth
- It does not enforce dictionary definitions
- It does not prevent language evolution
- It does not replace nuance with rigidity
- It does not require formal precision everywhere

Human-Filled Fields:

A) Active Definitions:
- <terms with stable meanings in this conversation>

Format:
- Term:
- Definition (as used here):
- Why it matters:

Examples:
- Term: "Deck"
  Definition: A collection of independent cards used for cognitive grounding.
  Why: Not a slide deck, not a game mechanic.

- Term: "Card"
  Definition: A self-contained markdown artifact that holds one type of thinking.
  Why: Not a UI element, not a metaphor — actual artifact.

- Term: "Exploration Mode"
  Definition: Deck mode for everyday users with no ordering or gates.
  Why: Distinguishes from Engineering Mode (ordered, gated).

- Term: "Grounding"
  Definition: Persistent conversational structure that prevents drift.
  Why: Not "prompting" (one-shot), not "memory" (passive storage).

B) Disambiguations:
- <terms with multiple meanings that need clarity>

Format:
- Term:
- Meaning A (not used here):
- Meaning B (used here):

Examples:
- Term: "Canonical"
  Not here: Religious or literary authority
  Used here: Formalized deck mode with strict gates (v1.0)

- Term: "Artifact"
  Not here: Historical object
  Used here: Persistent, portable markdown file

- Term: "Build"
  Not here: Software compilation
  Used here: Stepwise execution of a defined task

C) Context-Specific Meanings:
- <terms used differently than their common definition>

Examples:
- "Locked" = Stable for now, but revisitable (not permanent)
- "Draft" = Actively evolving (not low quality)
- "Gate" = Enforcement check (Engineering Mode only)

D) Terms to Avoid:
- <words that mislead or confuse>

Format:
- Term:
- Why avoid:
- Use instead:

Examples:
- "Framework"
  Why: Implies rigid structure or code dependency
  Use: "System" or "deck"

- "Template"
  Why: Implies one-time fill-and-forget
  Use: "Card" or "artifact"

- "Prompt"
  Why: Implies one-shot optimization
  Use: "Grounding" or "anchor"

E) Evolving Definitions:
- <terms still being clarified>

Examples:
- "Conversation temperature" (exploring: measure of drift or chaos)
- "Card activation" (unclear: does it mean 'in use' or 'filled'?)

F) Definition Notes:
- <patterns, observations, or clarifications>

Examples:
- "We're avoiding jargon where possible, but some terms need precision."
- "Deck/card language chosen for portability (physical metaphor, no tech baggage)."

Assistant Behavior When This Card Is Active:
- Use defined terms consistently
- Flag when assistant language contradicts definitions
- Ask for clarification when encountering undefined terms
- Suggest updates when meanings drift
- Avoid terms listed in "Terms to Avoid"
- Reference this card when terminology disputes arise
- Help refine Evolving Definitions when patterns emerge

Update Rules:
- Definitions may evolve as understanding sharpens
- Disambiguations can be added anytime
- Old definitions may be retained with "superseded" label
- It's valid for a term to move from Evolving to Active
- Avoid over-defining; some fuzziness is acceptable

Relationship to Other Cards:
- Feeds into: Assumptions, Decisions, Intent
- Prevents: Miscommunication, silent drift
- Paired with: Open Questions (what does X mean?)
- Complements: Notes (captures usage examples)

Example (filled):
Active:
- "Card" = Markdown artifact for one thinking type.

Disambiguations:
- "Mode" = Deck behavior type, not UI state.

Terms to Avoid:
- "Framework" (too rigid) → use "system"

Evolving:
- "Handoff" (still clarifying what this means)

Notes:
This card prevents the most common failure mode in long conversations:
assuming shared vocabulary that was never established.
