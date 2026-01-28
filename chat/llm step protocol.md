# Live Canvas Step-Update Schema (MVP v0.2)
Goal: make the LLM “think in steps” by writing durable state to a shared canvas each turn.
No governance/rules engine yet — just a consistent structure so the loop works.

---

## 0) Golden Rule
The LLM must **never** “continue solving in prose only.”
Every turn MUST:
1) read the current canvas
2) produce ONE step
3) **write** the step back into the canvas using the schema below
4) stop (unless explicitly told “take another step”)

---

## 1) Canvas Data Model (human-readable but structured)
Use this exact top-level layout every time.

CANVAS:
A) PROBLEM
B) GIVEN
C) GOAL
D) WORKING STATE
E) STEP LOG
F) OPEN ITEMS
G) NEXT STEP REQUEST

---

### A) PROBLEM
- A single pasted problem statement (verbatim).
- Never rewrite unless the user edits it.

### B) GIVEN
A bullet list of facts extracted from the problem.
Example fields (optional, just keep them consistent):
- triangle_type:
- angle_constraints:
- points_defined:
- lengths_given:

### C) GOAL
- One line: “Find XC” / “Prove …” / etc.

### D) WORKING STATE
This is the “chalkboard snapshot.” Keep it short and surgical.
Recommended subfields:
- coordinate_choice: (e.g., “Place B=(0,0), C=(c,0)” or “Use vectors”)
- key_objects: (Euler line, orthocenter H, centroid G, circumcenter O)
- derived_relations: (only confirmed relations)
- current_equations: (only confirmed equations)
- invariants_to_use: (named lemmas or known theorems you’re committing to)

### E) STEP LOG
Append-only list of steps. Each step has:
- step_id: integer increasing by 1
- timestamp: optional
- intent: what this step is trying to do (one sentence)
- action: the actual math move (derivation, lemma application)
- result: what new fact is now confirmed
- checks: sanity checks (dimensional/geometry consistency)
- patch_summary: what changed on the canvas this step

### F) OPEN ITEMS
Short bullet list of unresolved items:
- unknowns: (XC, AC, etc.)
- missing links: (need relation between Euler line intersection and side segments)
- candidate lemmas: (if not yet committed)

### G) NEXT STEP REQUEST
A single line telling the model what to do next:
- “Take step 5: derive relation between X on Euler line and directed segments on BC”
or
- “Stop and wait for user.”

---

## 2) Update Protocol (how the LLM edits the canvas each step)

### 2.1 Allowed Edits per Step (MVP discipline)
Per step, the LLM may:
- Add 1–3 items to “derived_relations” OR “current_equations”
- Append exactly 1 new STEP LOG entry
- Update OPEN ITEMS (remove solved items, add new ones)
- Update NEXT STEP REQUEST

Avoid rewriting large blocks. Small diffs = stability.

### 2.2 Required Output Every Turn
The LLM output must contain two parts:

PART 1 — Chat (brief)
- 3–8 lines max: explain what it did and what is now true.

PART 2 — CANVAS PATCH (structured)
- Provide a minimal patch showing exactly what to add/change.

---

## 3) Minimal Patch Format (easy for Build Mode)
Use a simple “diff-like” patch so the app can apply it without complex tooling.

PATCH FORMAT:
- Lines starting with “+” are additions
- Lines starting with “~” replace a single existing line (exact match)
- Lines starting with “-” delete a line (exact match)

Example:
+ D) WORKING STATE / derived_relations:
+ - Since X lies on BC, we can use directed segments with B between X and C.
+ E) STEP LOG / step_id: 3
+ intent: Express XC using known XB and XA via Euler-line relation.
+ action: ...
+ result: ...
~ G) NEXT STEP REQUEST: Take step 4: ...

If your environment prefers JSON, use the JSON patch schema below.

---

## 4) Optional JSON Patch Schema (if you want machine enforcement later)
This is still MVP-friendly, because it’s just “ops”.

{
  "run_id": "string",
  "step_id": 1,
  "ops": [
    { "op": "add", "path": "/working_state/derived_relations/-", "value": "string" },
    { "op": "add", "path": "/step_log/-", "value": {
        "step_id": 1,
        "intent": "string",
        "action": "string",
        "result": "string",
        "checks": ["string"],
        "patch_summary": "string"
    }},
    { "op": "replace", "path": "/next_step_request", "value": "string" }
  ]
}

---

## 5) The LLM Instruction (drop-in “system rule”)
Use this verbatim as the model’s operating constraint:

- Always read the full canvas before responding.
- Perform exactly ONE reasoning step per turn.
- After the step, output a CANVAS PATCH that appends a Step Log entry and updates Working State.
- Do not erase or rewrite prior steps; only append or minimal edits.
- If you are unsure, write the uncertainty into OPEN ITEMS and propose the next step request.
- Stop after writing the patch.

---

## 6) The Data You Actually Need (minimum viable fields)
If you want the absolute minimum fields (barebones), keep only:

PROBLEM
GIVEN
GOAL
WORKING STATE (2–6 lines)
STEP LOG (append-only)
OPEN ITEMS
NEXT STEP REQUEST

That alone is enough to create “time,” “memory,” and “causality.”

---
