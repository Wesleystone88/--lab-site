# CARD-03 — CONSTRAINTS (System Physics)

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
