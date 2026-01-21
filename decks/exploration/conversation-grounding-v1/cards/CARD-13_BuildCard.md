---
seed_identity:
  artifact_id: CARD-13
  seed_algo: sha256-v1
  seed: d7bc16c389cb71270e18a73d18a01e1a1b9594c932fa7f0560f2d9c08b51768a
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:41:55Z'
  status: locked
card:
  id: CARD-13
  name: Build Card (Stepwise Execution)
  namespace: noesis.conversation-grounding.exploration
  version: 1.0
  mode: EXPLORATION
suggested_patterns:
  often_paired_with:
  - CARD-02
  - CARD-09
  - CARD-11
  helpful_for:
  - stepwise_execution
  - preventing_drift_in_builds
  - anti_scope_creep
state_schema:
  build_goal: string
  definition_of_done: string
  step_list: array<object>
  active_step: integer
  constraints: array<string>

---

# ============================================================
# Conversation Grounding Deck — Exploration Mode
# CARD-13 — BUILD CARD (Stepwise Execution)
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
