# ============================================================
# νόησις Canonical Deck (v1.0)
# Authoritative Specification and Long-Term Preservation
# DeckName: νόησις Canonical Deck
# DeckMode: Canonical Deck (v1.0)
# Author: Timothy Wesley Stone
# License: Open / Shareable
# ============================================================

# PURPOSE
The νόησις Artifact Deck is a portable, human-first framework for converting vague ideas
into durable, explicit, and shareable system specifications. Each card represents a
complete specification artifact — not a summary, not a sketch, not a placeholder.

Cards persist across LLM sessions, model changes, collaborators, and time.

No engine, software, or tooling is required to use this deck.


# ============================================================
# CARD-0 — PACKAGE (Domain Envelope)
# ============================================================

Purpose:
Declare what kind of thing this project fundamentally is before intent is defined.
Prevents category confusion and hidden assumption drift.

Contains:
- Project Class: software | research | hardware | protocol | social | hybrid
- Execution Mode: human-only | LLM-assisted | automated | mixed
- Artifact Types: code | documents | datasets | models | hardware | simulations
- Distribution: open | closed | internal | regulated
- Longevity: prototype | production | archival | disposable
- Compliance Scope: legal, safety, privacy, export, medical, etc.
- Success Horizon: experiment | MVP | long-term system

Outputs:
- Determines which downstream cards are mandatory or optional.
- Establishes scope of rigor required.

Gate:
- PACKAGE must be declared before CARD-1 exists.


# ============================================================
# CARD-1 — WRITE-UP (Narrative Anchor)
# ============================================================

Purpose:
Capture the raw human story before formalization.
Preserves meaning, motivation, and context.

Contains:
- Problem narrative
- Why this exists now
- Who benefits
- Emotional drivers
- Risks and fears
- Success vision
- Example scenarios
- Rough ideas and metaphors

Rules:
- Informal language allowed.
- Contradictions allowed.
- Versioned over time.

Outputs:
- Shared mental grounding.
- Vocabulary seed.

Gate:
- Must exist before CARD-2.


# ============================================================
# CARD-2 — INTENT (Operational Goal)
# ============================================================

Purpose:
Convert narrative into executable purpose and boundaries.

Contains:
- Primary objective
- Non-goals
- Success criteria (measurable)
- Required capabilities
- Forbidden behaviors
- Acceptable compromises
- Explicit exclusions
- Priority ordering

Outputs:
- What must exist.
- What must never exist.

Gate:
- Must be internally consistent.
- Conflicts must be resolved or documented.


# ============================================================
# CARD-3 — CONSTRAINTS (System Physics)
# ============================================================

Purpose:
Define the immutable realities governing the system.

Contains:
- Budget limits
- Time constraints
- Hardware limits
- Latency ceilings
- API quotas
- Skill constraints
- Regulatory limits
- Data limits
- Energy / compute limits

Outputs:
- Feasible design envelope.

Gate:
- Constraints must be respected by downstream cards.


# ============================================================
# CARD-4 — STRUCTURE (System Topology)
# ============================================================

Purpose:
Define what exists and how it connects.

Contains:
- Component inventory
- Responsibility boundaries
- Data flows
- Control flows
- State ownership
- Trust boundaries
- Coupling points
- Failure propagation paths

Outputs:
- Conceptual architecture map.

Gate:
- No undefined responsibilities or orphan components.


# ============================================================
# CARD-5 — FILE / ASSET TREE (Materialization)
# ============================================================

Purpose:
Translate structure into tangible organization.

Contains:
- Directory layout
- Naming conventions
- Ownership zones
- Generated vs hand-written separation
- Artifact lifecycles
- Versioning strategy
- Storage growth expectations
- Backup policy

Outputs:
- Physical build skeleton.

Gate:
- Must reflect CARD-4 structure.


# ============================================================
# CARD-6 — INTERFACES / API (Communication Contract)
# ============================================================

Purpose:
Define all communication boundaries.

Contains:
- Input schemas
- Output schemas
- Validation rules
- Error contracts
- Versioning policy
- Backward compatibility rules
- Authentication boundaries
- Performance expectations

Outputs:
- Interoperability guarantees.

Gate:
- No ambiguous interfaces.


# ============================================================
# CARD-7 — DEPENDENCIES (External Coupling)
# ============================================================

Purpose:
Expose external reliance and fragility.

Contains:
- Libraries
- Services
- Models
- Vendors
- Hardware
- Licenses
- Update risks
- Lock-in risks
- Replacement strategies

Outputs:
- Dependency risk map.

Gate:
- All dependencies must be justified.


# ============================================================
# CARD-8 — SAFETY & SECURITY (Trust Envelope)
# ============================================================

Purpose:
Prevent harm, abuse, leakage, corruption.

Contains:
- Threat model
- Attack surfaces
- Data exposure risks
- Permission model
- Sandbox strategy
- Secrets handling
- Auditability
- Abuse prevention
- Incident response

Outputs:
- Trust boundary specification.

Gate:
- Unmitigated critical risks prohibited.


# ============================================================
# CARD-9 — FAILURE & RECOVERY (Resilience)
# ============================================================

Purpose:
Define how the system fails and heals.

Contains:
- Failure modes
- Silent failure risks
- Partial failure behavior
- Data corruption risks
- Human error risks
- Detection mechanisms
- Recovery strategies
- Rollback procedures

Outputs:
- Operational resilience plan.

Gate:
- Critical failures must have recovery paths.


# ============================================================
# CARD-10 — EVOLUTION & SCALING (Future Survivability)
# ============================================================

Purpose:
Ensure longevity and adaptability.

Contains:
- Growth paths
- Migration strategies
- Backward compatibility
- Performance ceilings
- Cost scaling
- Team scaling
- Decomposition strategy
- Retirement strategy

Outputs:
- Long-term viability roadmap.

Gate:
- Scaling assumptions must align with constraints.


# ============================================================
# CARD-11 — EXECUTION (Build Plan)
# ============================================================

Purpose:
Translate specification into action.

Contains:
- Milestones
- Validation gates
- Proof-of-life targets
- Kill criteria
- Feedback loops
- Automation strategy
- Testing strategy
- Documentation plan

Outputs:
- Concrete execution roadmap.

Gate:
- Execution must honor all upstream cards.


# ============================================================
# CORE PRINCIPLES
# ============================================================

- Cards are full specifications, not summaries.
- Cards are human-readable and portable.
- Cards persist across tools and models.
- LLMs assist but do not replace ownership.
- Drift must be visible and correctable.
- Structure precedes automation.
- Thinking is treated as engineering.

# ============================================================
