---
seed_identity:
  artifact_id: CARD-03
  seed_algo: sha256-v1
  seed: e3d8578c566d657aa4ed95dc4d8de4aad71d678033be7bc7b5242f38511857a2
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:42:03Z'
  status: locked
card:
  id: CARD-03
  name: Constraints (System Physics)
  namespace: noesis.emergence.v0.1
  version: 0.1.0
  mode: ENGINEERING
  deck_mode: Emergence
dependencies:
  upstream:
  - CARD-00
  - CARD-02
  downstream:
  - CARD-04
  guards:
  - CARD-04
  - CARD-05
  - CARD-06
  - CARD-07
  - CARD-08
  required_by:
  - CARD-04
gate:
  enforcement: diagnostic
  rules:
  - WARNING if fewer than 3 constraints
  blocks_downstream: false
ordering:
  position: 3
  required_after:
  - CARD-02
  required_before:
  - CARD-04

---

# CARD-03 — CONSTRAINTS (System Physics)

DeckName: vóṇōs Emergence Deck
DeckMode: Emergence Deck (v0.1)
CardID: CARD-03
CardName: Constraints
Version: 0.1
Status: draft
Owner: Timothy Wesley Stone
UpstreamCards: [CARD-02]
DownstreamCards: [CARD-04]

Purpose:
Define immutable laws.

Inputs:
- CARD-02 INTENT

Outputs:
- Hard invariants
- Soft targets

Content:
Hard Invariants:
I1. No silent decisions.
I2. Deck usable without software.
I3. Cards remain plain text.
I4. Structure is typed, not generic.
I5. Humans retain authority.

Soft Targets:
T1. Lightweight.
T2. Readable.
T3. Minimal ceremony.

Gate:
- ERROR if fewer than 3 invariants.
