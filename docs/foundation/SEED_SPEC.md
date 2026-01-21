# νόησις Seed Specification

**Version**: spine-v1  
**Algorithm**: sha256-v1  
**Status**: Active  

---

## What is a Seed?

A **seed** is a tamper-evident identity for artifacts. It's a cryptographic fingerprint of an artifact's **immutable meaning** (its "spine"), allowing you to prove: *this is the same artifact*, even if:

- Phrasing changes
- Examples are added/removed
- Formatting is reorganized
- Models switch
- Notes are appended

---

## Core Principle: Spine vs Body

Every artifact splits into **two zones**:

### Spine (Seeded / Identity)
The fields that define **what the artifact is**. If these change, it's a different artifact.

### Body (Unseeded / Expression)
Everything else. Can evolve freely without requiring a new seed.

**Constitution vs Commentary.**

---

## Spine Definitions by Artifact Type

### ENGINEERING MODE Cards
**Applies to**: Emergence Deck (v0.1), Canonical Deck (v1.0)

**Spine Fields**:
- `card.id` — Stable identifier (e.g., CARD-01, CARD-3)
- `card.name` — Card name
- `card.namespace` — Namespace (e.g., noesis.emergence.v0.1)
- `card.mode` — Must be "ENGINEERING"
- `card.deck_mode` — Emergence or Canonical
- `dependencies` — All dependency arrays (upstream, downstream, feeds_into, required_by)
- `gate` — Gate rules (enforcement, rules, blocks_downstream)
- `ordering` — Position and ordering constraints

**Body** (not seeded):
- Card content below the YAML front matter
- Examples, explanations, notes
- DeckName, Status, Owner fields
- Comments and formatting

### EXPLORATION MODE Cards
**Applies to**: Conversation Grounding Deck

**Spine Fields**:
- `card.id` — Stable identifier (e.g., CARD-01)
- `card.name` — Card name
- `card.namespace` — Namespace (e.g., noesis.conversation-grounding.exploration)
- `card.mode` — Must be "EXPLORATION"
- `suggested_patterns.often_paired_with` — Card pairing suggestions
- `suggested_patterns.helpful_for` — Use case hints
- `state_schema` — Queryable field definitions

**Body** (not seeded):
- Card content below the YAML front matter
- Extended descriptions
- Examples and templates
- Formatting and visuals

---

## Seed Identity Block

Every seeded artifact includes a `seed_identity` section in its YAML front matter:

```yaml
seed_identity:
  artifact_id: CARD-01              # Human-readable stable ID
  seed_algo: sha256-v1              # Hash algorithm + version
  seed: abc123...                   # SHA-256 hash (64 hex chars)
  seed_scope: spine-v1              # Which spine definition was used
  seeded_at: 2026-01-21T12:34:56Z   # ISO 8601 timestamp
  status: locked                    # draft | locked | deprecated
  parent_seed: xyz789...            # Optional: lineage tracking
```

---

## Canonicalization Rules

To ensure consistent seeds across trivial format differences:

1. **Extract** spine fields from YAML front matter
2. **Sort** all keys recursively (alphabetical)
3. **Convert** to canonical JSON: `{"key":"value"}` format
   - No whitespace variations
   - No comments
   - Stable field order (sorted)
4. **Hash** the canonical JSON with SHA-256
5. **Store** resulting 64-character hex string as seed

---

## Core Rules

### Rule 1: No Silent Spine Edits
If spine changes:
- ✅ Must generate new seed
- ✅ Optional: set `parent_seed` to old seed (lineage)
- ✅ Document in changelog

### Rule 2: Body Edits Never Require Reseeding
Otherwise the system becomes unusable.

### Rule 3: SeedScope is Versioned
`spine-v1` → future `spine-v2` without breaking old seeds

### Rule 4: Seeds Are Integrity, Not Authority
Seed proves: "matches claimed identity"  
Gate/validation proves: "is correct/valid"

---

## Verification Process

To verify a seed:

1. Read `seed_identity.seed` from artifact
2. Extract spine fields per `seed_identity.seed_scope`
3. Canonicalize spine
4. Compute SHA-256 hash
5. Compare to stored seed

**Match** = Integrity verified ✅  
**Mismatch** = Spine has changed ❌

---

## Status Lifecycle

**draft**: Spine may change freely, no seed required  
**locked**: Spine frozen, seed computed, body can evolve  
**deprecated**: No longer recommended, replaced by child artifact

---

## Scope Versioning

Current: `spine-v1` (initial definition)

Future versions might:
- Include/exclude different fields
- Change canonicalization rules
- Support new card types

Old seeds remain valid under their original scope.

---

## Example: Full Seeded Card

```yaml
---
# Seed Identity (tamper-evident)
seed_identity:
  artifact_id: CARD-01
  seed_algo: sha256-v1
  seed: a7f8e9d2c3b4a5f6e7d8c9b0a1f2e3d4c5b6a7f8e9d0c1b2a3f4e5d6c7b8a9
  seed_scope: spine-v1
  seeded_at: 2026-01-21T15:30:00Z
  status: locked

# Spine (seeded fields)
card:
  id: CARD-01
  name: Alignment Anchor
  namespace: noesis.conversation-grounding.exploration
  mode: EXPLORATION

suggested_patterns:
  often_paired_with: [CARD-02, CARD-03]
  helpful_for: [starting_conversations, refocusing_drift]

state_schema:
  goal: string
  user_priority: string
---

# Body (unseeded content)
# CARD-01 — Alignment Anchor

Purpose: Capture the core goal of the conversation...
```

---

## Benefits

✅ **Tamper Detection**: Any spine change breaks the seed  
✅ **Model Independence**: Rewrite explanations freely  
✅ **Lineage Tracking**: Parent seeds show artifact evolution  
✅ **Collaboration Safety**: Verify received artifacts match claims  
✅ **Stable Identity**: Same artifact = same seed, regardless of expression  

---

## Tool: seed-generator.py

Commands:
- `generate <file>` — Add seed to card
- `verify <file>` — Check seed integrity
- `show-spine <file>` — Display spine fields
- `batch-generate <dir>` — Seed all cards in directory

---

## Version History

**spine-v1** (2026-01-21): Initial specification
- ENGINEERING mode spine definition
- EXPLORATION mode spine definition
- SHA-256 canonicalization rules
- Status lifecycle (draft/locked/deprecated)

---

*Structure precedes automation. Identity precedes trust.*
