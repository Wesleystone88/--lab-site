# Live Canvas + LLM - Implementation Spec for Google AI Build Mode

## What You're Building

A two-pane web application that tests whether **persistent shared state** improves LLM reasoning quality compared to standard chat.

---

## UI Layout

```
┌─────────────────────────────────────────────────────┐
│  LIVE CANVAS (Left 50%)   │   CHAT (Right 50%)      │
│                            │                         │
│  ┌──────────────────────┐ │  ┌──────────────────┐  │
│  │                      │ │  │  Claude: ...     │  │
│  │  # Shared Canvas     │ │  │                  │  │
│  │                      │ │  │  You: ...        │  │
│  │  Persistent working  │ │  │                  │  │
│  │  memory that both    │ │  │  Claude: ...     │  │
│  │  you and the AI can  │ │  │                  │  │
│  │  read and modify.    │ │  └──────────────────┘  │
│  │                      │ │                         │
│  │  [User can directly  │ │  ┌──────────────────┐  │
│  │   edit this]         │ │  │ Message input... │  │
│  │                      │ │  │ [Send]           │  │
│  └──────────────────────┘ │  └──────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## Core Interaction Flow

### Step 1: User Action
User can:
- Edit the canvas directly (left pane)
- Send a chat message (right pane)
- Or both

### Step 2: Send to AI
When user sends a message, the system sends to Gemini:
```
System Prompt:
"You are participating in the Live Canvas + LLM experiment.

CURRENT CANVAS CONTENT:
[full canvas text here]

The canvas is persistent shared state. Both you and the user can read and modify it.
Use it to stabilize reasoning, track assumptions, store intermediate results.

If you want to update the canvas, propose changes using:
**Proposed Canvas Update:**
```
[new canvas content]
```

User message: [their actual message]
```

### Step 3: AI Response
Gemini responds with:
- Normal chat response
- Optionally: a proposed canvas update (in the format above)

### Step 4: User Reviews
If Gemini proposed a canvas update:
- Show the proposal in the chat with [Accept] [Reject] buttons
- If user accepts → update canvas
- If user rejects → ignore proposal
- Canvas persists into next turn either way

---

## Technical Requirements

### State Management
You need to track:
```javascript
- canvas (string): current canvas content
- messages (array): chat history [{role: 'user'|'assistant'|'system', content: string}]
- input (string): current user input
- loading (boolean): is AI responding
- pendingCanvasUpdate (string|null): proposed canvas change awaiting approval
```

### Gemini API Integration
Use Google's Gemini API (free in Build Mode):

```javascript
const response = await ai.languageModel.create({
  systemPrompt: `[system prompt with canvas content]`,
  messages: conversationHistory
});
```

### Canvas Update Extraction
After getting AI response, parse for:
```
**Proposed Canvas Update:**
```
[content here]
```
```

Extract the content between the code fences and store in `pendingCanvasUpdate`.

---

## What NOT to Build (MVP Scope)

❌ No automatic canvas updates (user must approve)
❌ No schemas or validation rules
❌ No canvas history/undo (keep it simple)
❌ No persistence beyond session (in-memory only)
❌ No fancy formatting tools for canvas
❌ No auto-save or syncing
❌ No multi-user support

---

## Visual Design (Keep Minimal)

- Two equal-width panes side by side
- Canvas: plain textarea, monospace font
- Chat: simple message bubbles (user vs assistant)
- Pending updates: highlighted box with approve/reject buttons
- Clean, readable, no distractions

---

## Success Indicators to Observe

During testing, watch for:
- ✅ Does the AI reference canvas content correctly?
- ✅ Does reasoning stay coherent across multiple turns?
- ✅ Does canvas reduce repetition/re-derivation?
- ✅ Can complex multi-step problems converge faster?
- ✅ Does shared state improve alignment between user and AI?

---

## Example Test Scenario

**User:** "Let's solve this problem: A train leaves station A at 60mph, another leaves station B (300 miles away) at 40mph, heading toward each other. When do they meet?"

**Expected Flow:**
1. AI responds in chat with approach
2. AI proposes canvas update with:
   - Known facts
   - Variables defined
   - Equations set up
3. User accepts → canvas updated
4. User: "Now solve for time"
5. AI reads canvas, continues from there (no re-explaining setup)
6. AI proposes canvas update with solution
7. Reasoning stays grounded in canvas throughout

---

## Implementation Tips for Build Mode

1. Use `ai.languageModel.create()` for Gemini access
2. Include full canvas in system prompt every turn
3. Keep UI responsive (disable send while loading)
4. Parse AI response for canvas proposals
5. Let user maintain full control over canvas state
6. Test with multi-turn reasoning tasks

---

## Philosophy Reminder

This is a **behavioral experiment**, not a production app.

Goal: Observe whether persistent shared state measurably improves reasoning quality.

Keep it minimal. Add structure only when real friction appears.

---

Start building! The experiment begins when you start testing real multi-step reasoning tasks.