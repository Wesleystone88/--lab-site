# ============================================================
# Conversation Grounding Deck â€” Exploration Mode
# CARD-01 â€” ALIGNMENT ANCHOR
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
- You catch yourself repeating "what I'm trying to do isâ€¦"

What This Card Holds:
- The current primary intent (not the final outcome)
- The reason this conversation is happening *at this moment*
- The frame of collaboration (explore, decide, plan, build, learn, vent, etc.)

What This Card Does NOT Do:
- It does not lock scope
- It does not define steps
- It does not enforce correctness
- It does not prevent evolution

This card is allowed to change over time.

Human-Filled Fields:
A) Current Alignment Statement (1â€“3 sentences):
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
- <not success criteria â€” just a sanity check>

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


---


# ============================================================
# Conversation Grounding Deck â€” Exploration Mode
# CARD-02 â€” CONSTRAINTS & RULES
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


---


# ============================================================
# Conversation Grounding Deck â€” Exploration Mode
# CARD-03 â€” INTENT & DIRECTION
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


---


# ============================================================
# Conversation Grounding Deck â€” Exploration Mode
# CARD-04 â€” SCOPE & BOUNDARIES
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
"What territory are we exploring â€” and what is outside the fence for now?"

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


---


# ============================================================
# Conversation Grounding Deck â€” Exploration Mode
# CARD-05 â€” NOTES & IDEA COLLECTION
# Author: Timothy Wesley Stone
# License: Open / Shareable
# ============================================================

CardID: CARD-05
CardName: Notes & Idea Collection
Mode: Exploration
Status: draft
Owner: Timothy Wesley Stone

Purpose:
Provide a persistent place to collect thoughts, fragments, partial ideas,
and observations *without forcing structure or decisions*.

This card answers:
"Where do ideas go when they're not ready yet?"

Use When:
- Ideas appear mid-conversation
- You don't want to lose a thought
- Something is interesting but premature
- You need a scratchpad that persists
- Multiple loose threads are forming

What This Card Holds:
- Raw notes
- Half-formed ideas
- Observations
- Quotes or phrasing worth keeping
- References to revisit later
- Brain-dump material

What This Card Does NOT Do:
- It does not organize ideas
- It does not decide importance
- It does not resolve contradictions
- It does not imply commitment

Human-Filled Fields:

A) Active Notes:
- <free-form notes added during conversation>
Examples:
- "The deck feels like a cognitive stabilizer, not a tool."
- "Cards should feel optional, not bureaucratic."
- "This could help people who think out loud."

B) Parked Ideas:
- <ideas acknowledged but deferred>
Examples:
- "Could later turn this into a workshop."
- "Might need a visual metaphor for cards."

C) Language Worth Keeping:
- <phrases, metaphors, wording>
Examples:
- "The conversation orbits the cards."
- "Stability without enforcement."

D) Questions to Revisit:
- <open questions with no urgency>
Examples:
- "How many cards is too many?"
- "What makes a card feel alive?"

Assistant Behavior When This Card Is Active:
- Suggest adding ideas here instead of derailing flow
- Refer back to notes when relevant
- Do not elevate notes into decisions automatically
- Treat this card as non-authoritative memory

Update Rules:
- Notes can be added anytime
- Notes can be deleted without ceremony
- Notes may later be promoted into other cards
- Messiness is allowed and expected

Relationship to Other Cards:
- Feeds into: Intent, Build, Decisions, Definitions
- Often paired with: Scope & Boundaries
- Never blocks progress

Example (filled):
Active Notes:
- "This deck is about orientation, not answers."

Parked Ideas:
- "Possible name variations."

Notes:
This card protects creativity.
It absorbs noise so the rest of the conversation can stay clean.


---


# ============================================================
# Conversation Grounding Deck â€” Exploration Mode
# CARD-06 â€” ASSUMPTIONS & BELIEFS
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


---


# ============================================================
# Conversation Grounding Deck â€” Exploration Mode
# CARD-07 â€” OPEN QUESTIONS (Merged)
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
- <questions answered since last update â€” retained for reference>
Format:
- Question â†’ Answer / Resolution
- Date (optional)

Examples:
- "Is this an engine?" â†’ No, it's a grounding system.
- "Is this a prompt system?" â†’ No, it's conversational structure.
- "Should cards be ordered?" â†’ Not in Exploration Mode.

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
- "Is this for technical users?" â†’ No, everyday users.

Notes:
Unanswered questions are assets, not bugs.
They signal active thinking, not incompleteness.


---


# ============================================================
# Conversation Grounding Deck â€” Exploration Mode
# CARD-08 â€” IDEA COLLECTION
# Author: Timothy Wesley Stone
# License: Open / Shareable
# ============================================================

CardID: CARD-08
CardName: Idea Collection
Mode: Exploration
Status: draft
Owner: Timothy Wesley Stone

Purpose:
Provide a safe place to collect, cluster, and preserve ideas as they appear
during conversationâ€”without forcing evaluation, structure, or decisions.

This card answers:
"What ideas have surfaced that we don't want to lose?"

Use When:
- Ideas appear faster than you can evaluate them
- You want to keep momentum without deciding
- Multiple directions are emerging
- You don't want good ideas buried in chat history
- You want to revisit ideas later with fresh context

What This Card Holds:
- Raw ideas
- Half-formed concepts
- Alternate approaches
- Naming ideas
- Feature thoughts
- Metaphors or analogies
- "What ifâ€¦" statements

What This Card Does NOT Do:
- It does not judge idea quality
- It does not prioritize automatically
- It does not assume ideas must be used
- It does not imply commitment

Human-Filled Fields:

A) Raw Ideas (Unfiltered):
- <ideas exactly as they surfaced>
Examples:
- "What if the deck had a 'conversation temperature' card?"
- "Random topic cards for creative exploration."
- "Physical index-card version of this."

B) Grouped / Clustered Ideas (Optional):
- <light grouping without evaluation>
Examples:
- UX Ideas:
  - "Visual card pins"
  - "Collapsed card summaries"
- Product Ideas:
  - "Starter decks"
  - "Printable cards"

C) Ideas Under Light Consideration:
- <ideas you keep glancing at>
Examples:
- "13-card build sequence."
- "Exploration vs Canonical decks."

D) Ideas to Revisit Later:
- <explicitly parked>
Examples:
- "AI-assisted card summarization."
- "Public deck sharing gallery."

Assistant Behavior When This Card Is Active:
- Add ideas verbatim when suggested
- Do not optimize or rephrase unless asked
- Do not evaluate unless prompted
- Help cluster only when requested
- Respect that some ideas stay messy

Update Rules:
- Ideas may move between sections
- Deleting ideas is allowed but discouraged
- Old ideas can be revived at any time
- Silence â‰  rejection

Relationship to Other Cards:
- Feeds into: Build Plan, Decisions, Intent
- Paired with: Open Questions
- Helps maintain creative flow

Example (filled):
Raw Idea:
- "Conversation cards for therapy-like journaling."

Notes:
This card exists to protect creativity from premature structure.


---


# ============================================================
# Conversation Grounding Deck â€” Exploration Mode
# CARD-09 â€” DECISIONS (Merged)
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
- Silent assumption â‰  decision
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


---


# ============================================================
# Conversation Grounding Deck â€” Exploration Mode
# CARD-10 â€” DEFINITIONS & TERMINOLOGY
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
  Why: Not a UI element, not a metaphor â€” actual artifact.

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
- "Framework" (too rigid) â†’ use "system"

Evolving:
- "Handoff" (still clarifying what this means)

Notes:
This card prevents the most common failure mode in long conversations:
assuming shared vocabulary that was never established.


---


# ============================================================
# Conversation Grounding Deck â€” Exploration Mode
# CARD-11 â€” CONTEXT HANDOFF
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
- <where the conversation is right now â€” 2â€“5 sentences>

Examples:
- "We're designing a Conversation Grounding Deck for everyday users.
   13 cards defined. Currently finalizing merge requirements for 5 new cards.
   Intent is clear, structure is stable, examples are being refined."

- "Mid-build on a stepwise execution system. Step 3 of 7 complete.
   Constraints locked, next step is testing card sequencing."

B) Active Cards in Use:
- <which cards are currently guiding the conversation>

Format:
- CARD-XX: [Card Name] â€” (role in conversation)

Examples:
- CARD-01: Alignment Anchor â€” Defines current purpose
- CARD-02: Constraints & Rules â€” Enforces no-rewrite rule
- CARD-09: Decisions â€” Holds locked design choices
- CARD-13: Build Card â€” Currently executing Step 5

C) Last Activity / Where Conversation Left Off:
- <specific point of departure>

Examples:
- "Just completed CARD-07 merge. About to start CARD-09."
- "Waiting for human feedback on Build Step 4 output."
- "Paused mid-discussion about card naming conventions."

D) Key Decisions & Constraints Snapshot:
- <critical context for resumption â€” abbreviated>

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
- "This deck is NOT technical â€” keep language accessible."
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
- Compress ruthlessly â€” this is a summary, not a transcript
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


---


# ============================================================
# Conversation Grounding Deck â€” Exploration Mode
# CARD-12 â€” PROGRESS TRACKER
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
- "Card creation accelerating â€” structure is well-defined now."
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


---


# ============================================================
# Conversation Grounding Deck â€” Exploration Mode
# CARD-13 â€” BUILD CARD (Stepwise Execution)
# Author: Timothy Wesley Stone
# License: Open / Shareable
# ============================================================

CardID: CARD-13
CardName: Build Card (Stepwise Execution)
Mode: Exploration (Conversation Grounding)
Status: ready
Owner: Timothy Wesley Stone

Purpose:
Turn a fuzzy goal into a disciplined, step-by-step conversation where the assistant
executes ONE step at a time, reports back, and cannot rewrite earlier steps once
the build has progressed.

Use When:
- You want the chat to "build something" without drifting
- You want progress in ordered steps
- You want strong anti-scope-creep behavior
- You want a repeatable procedure you can resume later

Card Rules (Hard):
R1. One step at a time. The assistant only performs the CURRENT step.
R2. No retro-edits. Once Step 1 is completed and Step 2 begins, Step 1 is frozen.
R3. The assistant must NOT merge steps, skip steps, or jump ahead.
R4. Each step ends with a "Step Report" and a "Ready for Step N+1" marker.
R5. If the assistant believes a prior step is wrong, it must log it in "Issues"
    and propose a fix as a NEW future step (Step N+K), not by rewriting history.
R6. If the human changes the goal mid-run, the assistant must ask to create a new
    Build Run ID (fork) OR append a Change Request step at the end.

What the Human Fills In:
A) Build Goal (one sentence):
- <what you want built>

B) Definition of Done:
- <how we know it's finished>

C) Output Type:
- <plan | checklist | outline | prompt | code | doc | mixed>

D) Step List (ordered, explicit):
Step 1: <...>
Step 2: <...>
Step 3: <...>
...
Step N: <...>

E) Constraints for the Build:
- <time, tools, tone, risk, do/don't>

F) Build Run ID:
- <YYYY-MM-DD shortname> (example: 2026-01-20-groundingdeck)

G) Reporting Format (pick one):
- ( ) Brief
- ( ) Normal
- ( ) Detailed

Assistant Execution Script (paste this into chat with the filled card):
--------------------------------------------------------------------
You are now running BUILD CARD (Stepwise Execution).

Build Run ID: <ID>
Build Goal: <Goal>
Definition of Done: <DoD>
Output Type: <OutputType>
Constraints: <Constraints>
Reporting Format: <Brief|Normal|Detailed>

Step List (Frozen once Step 1 begins):
1) <Step 1>
2) <Step 2>
3) <Step 3>
...
N) <Step N>

Execution Rules (must obey):
- Do ONLY Step 1 right now.
- Do NOT alter Step 1 after finishing it.
- After completing Step 1, provide a Step Report with:
  * What was done
  * What was produced (artifact/output)
  * Any issues discovered (without rewriting Step 1)
  * What is needed for Step 2
- Then end with exactly:
  READY FOR STEP 2
--------------------------------------------------------------------

Step Report Template (assistant must use):
- Step Completed: Step <N>
- Output Produced:
  - <bullets or links or pasted artifact>
- Decisions Locked:
  - <bullets>
- Issues Logged (no retro-edits):
  - <bullets>
- Inputs Needed for Next Step:
  - <bullets>
- READY FOR STEP <N+1>

Notes:
- This card is compatible with re-uploading / re-pasting across sessions.
- If the conversation resets, paste this card and the last Step Report to resume.


---


