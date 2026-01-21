# Which Deck Should I Use?

Author: Timothy Wesley Stone  
License: Open / Shareable

νόησις provides two complementary decks. They serve different cognitive phases of building.

You do not "upgrade" tools — you mature ideas.

---

## 🟡 Emergence Deck (v0.x)

**Use this when:**
- You are exploring an idea.
- The problem is still fuzzy.
- Requirements are moving.
- You are thinking out loud with an LLM.
- You want fast momentum without over-constraint.
- You expect contradictions, revisions, and drift.

**Characteristics:**
- Narrative-friendly.
- Partial cards are allowed.
- Gates act as guidance, not enforcement.
- Ambiguity is tolerated temporarily.
- Creativity and discovery are prioritized.
- Cards evolve rapidly.

**Primary goal:**
> Turn vague intuition into structured understanding without killing creativity.

**Typical users:**
- Early-stage builders
- Researchers
- Exploratory system designers
- Concept architects
- Solo thinkers iterating fast

---

## 🔵 Canonical Deck (v1.x)

**Use this when:**
- The system must be correct, reproducible, and stable.
- You are preparing for implementation, collaboration, or publication.
- Ambiguity must be eliminated.
- Decisions must be traceable and auditable.
- Safety, dependency, and failure modes matter.
- You are locking a design.

**Characteristics:**
- Full specification required.
- Gates are binding.
- Incomplete cards are not allowed.
- Contradictions must be resolved explicitly.
- Assumptions must be documented.
- Drift is treated as a defect.

**Primary goal:**
> Produce durable, engineering-grade system specifications that survive time, teams, and tooling.

**Typical users:**
- Production builders
- Open-source maintainers
- Research teams
- Infrastructure designers
- Safety-critical projects

---

## 🔁 Promotion Flow (Emergence → Canonical)

Ideas typically begin in the **Emergence Deck** and mature into the **Canonical Deck**.

Promotion is intentional and human-controlled.

A project is ready to promote when:
- Intent is stable.
- Constraints are understood.
- Major unknowns are resolved.
- Interfaces and dependencies are no longer speculative.
- Safety and failure modes are explicitly considered.

Promotion is not automatic.
Copy relevant cards forward and refine them to Canonical rigor.

---

## 📄 Templates

All templates are **deck-agnostic**.

You may use the same templates for both decks.

The difference is enforcement:
- **Emergence Deck:** Partial filling is acceptable.
- **Canonical Deck:** Full completion is required.

---

## 🧭 Quick Decision Guide

| If you are...                                | Use this deck              |
|--------------------------------------------|-----------------------------|
| Exploring ideas                             | Emergence Deck (v0.x)       |
| Refining concepts                          | Emergence Deck (v0.x)       |
| Designing rigorously                       | Canonical Deck (v1.x)       |
| Preparing to build                         | Canonical Deck (v1.x)       |
| Publishing or sharing specifications       | Canonical Deck (v1.x)       |
| Thinking out loud with an LLM               | Emergence Deck (v0.x)       |
| Locking architecture and safety guarantees | Canonical Deck (v1.x)       |

---

Structure precedes automation.  
Thinking is treated as engineering.
