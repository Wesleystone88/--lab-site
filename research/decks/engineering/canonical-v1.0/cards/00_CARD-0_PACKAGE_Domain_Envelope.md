---
seed_identity:
  artifact_id: CARD-0
  seed_algo: sha256-v1
  seed: 3ebb936856d9c0386b2233246df6819727327fd50d1952ac61f69c48ba31af69
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:42:08Z'
  status: locked
card:
  id: CARD-0
  name: Package (Domain Envelope)
  namespace: noesis.canonical.v1.0
  version: 1.0.0
  mode: ENGINEERING
  deck_mode: Canonical
dependencies:
  upstream: []
  downstream:
  - CARD-1
  - CARD-2
  - CARD-3
  - CARD-4
  - CARD-5
  - CARD-6
  - CARD-7
  - CARD-8
  - CARD-9
  - CARD-10
  - CARD-11
  required_by:
  - CARD-1
gate:
  enforcement: strict
  rules:
  - ERROR if project_class undefined
  - ERROR if execution_mode undefined
  blocks_downstream: true
ordering:
  position: 0
  required_before:
  - CARD-1

---

# CARD-0 — PACKAGE (Domain Envelope)

DeckName: vóṇōs Canonical Deck
DeckMode: Canonical Deck (v1.0)

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
