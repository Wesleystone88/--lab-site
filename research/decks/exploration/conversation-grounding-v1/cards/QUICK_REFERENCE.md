# Conversation Grounding Deck — Quick Reference

## Card Selection Guide

**Choose 1-3 cards for most conversations. Don't use all 13 at once.**

### By Conversation Type

| Conversation Type | Recommended Cards | Why |
|------------------|-------------------|-----|
| **Exploring ideas** | 01, 05, 07 | Alignment, Notes, Questions |
| **Making decisions** | 01, 02, 09 | Alignment, Constraints, Decisions |
| **Building something** | 02, 09, 13 | Constraints, Decisions, Build |
| **Clarifying concepts** | 06, 10, 03 | Assumptions, Definitions, Intent |
| **Long conversations** | 01, 11, 12 | Alignment, Handoff, Progress |
| **Thinking out loud** | 01, 05, 08 | Alignment, Notes, Ideas |
| **Session resume** | 11 | Context Handoff (only) |

### By Problem

| Problem | Card Solution |
|---------|---------------|
| Conversation keeps drifting | CARD-01 (Alignment Anchor) |
| Assistant ignores rules | CARD-02 (Constraints & Rules) |
| Unclear what we're doing | CARD-03 (Intent & Direction) |
| Too many topics at once | CARD-04 (Scope & Boundaries) |
| Losing ideas/thoughts | CARD-05 (Notes) or CARD-08 (Ideas) |
| Talking past each other | CARD-06 (Assumptions) or CARD-10 (Definitions) |
| Questions keep returning | CARD-07 (Open Questions) |
| Re-arguing decisions | CARD-09 (Decisions) |
| Session reset amnesia | CARD-11 (Context Handoff) |
| Lost track of progress | CARD-12 (Progress Tracker) |
| Need stepwise execution | CARD-13 (Build Card) |

---

## Card Combinations (Proven Patterns)

### "Foundation Stack"
**CARD-01 + CARD-02 + CARD-03**  
Alignment + Constraints + Intent  
Use when: Starting significant work

### "Memory Stack"
**CARD-05 + CARD-07 + CARD-09**  
Notes + Questions + Decisions  
Use when: Long exploratory conversation

### "Execution Stack"
**CARD-02 + CARD-09 + CARD-13**  
Constraints + Decisions + Build  
Use when: Building something concrete

### "Clarity Stack"
**CARD-06 + CARD-10 + CARD-03**  
Assumptions + Definitions + Intent  
Use when: Confusion or misalignment

### "Handoff Stack"
**CARD-11 + CARD-12**  
Context Handoff + Progress Tracker  
Use when: Session about to reset

---

## Quick Start Workflow

### Step 1: Pick Your Card(s)
- Start with **CARD-01** if unsure
- Add **CARD-02** if you have rules
- Add others as needed

### Step 2: Fill Human Fields
Open the card file, fill the sections marked:
```
Human-Filled Fields:
A) Section Name:
- <your content here>
```

### Step 3: Paste Into Chat
Copy entire filled card into your LLM chat with your question.

### Step 4: Update As Needed
Cards evolve during conversation. Update and re-paste when intent shifts.

---

## Card Cheat Sheet

| # | Card Name | One-Line Purpose |
|---|-----------|------------------|
| 01 | Alignment Anchor | Why this conversation exists |
| 02 | Constraints & Rules | Boundaries to respect |
| 03 | Intent & Direction | What we're aiming at |
| 04 | Scope & Boundaries | What's in/out |
| 05 | Notes & Ideas | Raw thought collection |
| 06 | Assumptions & Beliefs | Hidden foundations |
| 07 | Open Questions | Unanswered questions |
| 08 | Idea Collection | Ideas without judgment |
| 09 | Decisions | What's been decided |
| 10 | Definitions | Shared vocabulary |
| 11 | Context Handoff | Session resume package |
| 12 | Progress Tracker | Done/in-progress/next |
| 13 | Build Card | Stepwise execution |

---

## Usage Tips

### DO:
✅ Use 1-3 cards per conversation  
✅ Update cards as thinking evolves  
✅ Fill cards with concrete content  
✅ Paste cards when resuming sessions  
✅ Add new cards mid-conversation  
✅ Remove cards that stop helping  

### DON'T:
❌ Use all 13 cards at once  
❌ Treat cards as bureaucracy  
❌ Let assistant modify your card content  
❌ Fill cards with placeholders ("TBD")  
❌ Expect automatic enforcement  
❌ Over-structure exploration  

---

## Emergency Fixes

### "Conversation is drifting"
→ Paste **CARD-01** (Alignment Anchor)

### "Assistant keeps doing X despite me saying no"
→ Paste **CARD-02** (Constraints) with X in "Forbidden Behaviors"

### "We keep re-arguing the same point"
→ Paste **CARD-09** (Decisions) with the decision locked

### "Session is about to reset"
→ Fill **CARD-11** (Context Handoff) and save it

### "Building something but it's getting messy"
→ Switch to **CARD-13** (Build Card) with explicit steps

---

## Minimal Viable Deck (3 Cards)

For 80% of conversations, you only need:

1. **CARD-01: Alignment Anchor**  
   (Why we're talking)

2. **CARD-09: Decisions**  
   (What we've locked in)

3. **CARD-11: Context Handoff**  
   (For session resumes)

Start here. Add others only when friction appears.

---

## Session Resume Template

When chat resets, paste:

```markdown
[CARD-11: Context Handoff — filled]

Current State: <1-3 sentences>
Active Cards: CARD-XX, CARD-YY
Last Activity: <where we left off>
Key Decisions: <bullet list>
Next Steps: <what's next>
```

The assistant will reconstruct context and continue.

---

## Common Mistakes

### Mistake 1: Using Too Many Cards
**Problem**: Cognitive overload, feels bureaucratic  
**Fix**: Start with 1-2 cards, add only when needed

### Mistake 2: Treating Cards as Forms
**Problem**: Feels like homework, not thinking  
**Fix**: Cards are living documents, update freely

### Mistake 3: Vague Content
**Problem**: "Define constraints" → unhelpful  
**Fix**: "Do not skip steps. One thing per message."

### Mistake 4: Forgetting to Update
**Problem**: Cards drift from reality  
**Fix**: Update cards when intent/decisions shift

### Mistake 5: Expecting Magic
**Problem**: Cards don't automatically fix everything  
**Fix**: Cards provide structure; you provide direction

---

**Remember**: Cards are cognitive tools, not process overhead.  
Use them when they help. Ignore them when they don't.
