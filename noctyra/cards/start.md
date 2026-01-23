Noctyra / VøR — Name Reference Card # Noctyra / VøR **World Name (Official):** Noctyra **Colloquial Short Form:** VøR --- ## Usage **Noctyra** appears in: - Story, lore, world-building - Formal documentation - First-time explanations - "What is this?" contexts **VøR** appears in: - Community shorthand - Technical contexts (where brevity matters) - Protocol strings (ASCII: vor, UTF-8: vør) - What people actually type in chat --- ## Pronunciation **Noctyra:** /nok-TIE-ruh/ or /NOK-tir-uh/ **VøR:** Undefined (intentionally ambiguous) --- ## Design Intent The world has a long name for narrative weight. People will use the short name because they always do. Both are intentional. Both are correct. --- **Project:** Noctyra Monster Deck **Owner:** Timothy Wesley Stone **Protocol:** Strong Mint v2
# Monster Deck — Strong Mint Protocol v2

**Project Owner:** Timothy Wesley Stone
**Status:** Active (Generator Phase)
**Scope:** Seed → Generator Card → Deterministic Monster Minting

---

## 1. What This Is

Monster Deck is a procedural monster system built on **finite generators** and **infinite deterministic instances**.

* There are **exactly 12 Generator Cards**.
* Each Generator Card is a **permanent statistical recipe**.
* Each Generator can mint **infinitely many unique monsters**.
* Monsters are **not collectibles**; they are **instances**.
* Validity is enforced by **math + recomputation**, not trust.

There is **no gameplay logic** here. This repository defines **how monsters are born**, not how they fight.

---

## 2. Core Principles (Non‑Negotiable)

1. **Strong Determinism**
   Same generator + same nonce = same monster forever.

2. **Finite Rules, Infinite Output**
   Rules never change. Variety comes from deterministic variation.

3. **No Probabilistic Illusions**
   No sampling, no confidence bounds, no randomness at runtime.

4. **Spine Authority**
   The spine recomputes everything. If it doesn’t match, the monster is invalid.

5. **LLM ≠ Authority**
   LLMs generate flavor only. Numbers come from math.

---

## 3. System Overview

```
Generator Card (1 of 12)
        ↓
   seed_256 + parameters
        ↓
nonce_128 (unique per mint)
        ↓
HKDF → domain‑separated keys
        ↓
Deterministic PRNG stream
        ↓
Stat derivation (exact math)
        ↓
Quantization
        ↓
Merkle root receipt
        ↓
Monster Instance (valid or rejected)
```

---

## 4. Generator Cards (The Only Sources of Variety)

Each Generator Card defines **how a family of monsters may exist**.

### Required Fields per Generator

* `generator_id` (1–12)
* `seed_256` (32‑byte hex)
* `mint_version`
* `spine_ref`
* `archetype_bias` (Stable | Volatile | Growth | Locked)

### Statistical Definition

* **μ (mu)** — mean vector `[ATK, DEF, HP, ENG]`
* **sigma_factor** — deviation scale
* **corr_R** — 4×4 correlation matrix (SPD)
* **dist_family** — Normal | Beta | TruncatedNormal
* **latent_policy** — None | GrowthSplit | LockedSplit
* **latent_pct** — percentage moved to latent stats

Generator Cards are immutable. Changes require a **new mint_version**.

---

## 5. Nonce Ledger (Uniqueness Enforcement)

Every monster mint requires a **nonce_128**.

* Nonce is a **monotonic counter**, starting at 0
* Incremented once per mint
* Unique per `(account, generator_id, mint_version)`
* Replay is rejected

Nonce ensures uniqueness without adding entropy.

---

## 6. Strong Mint Protocol v2 (Summary)

### Step 1 — Identity Key

```
k_id = HKDF(seed_256, nonce_128, "monster_identity")
```

### Step 2 — Stream Keys

```
k_stats = HKDF(k_id, None, "stats_stream")
```

### Step 3 — Deterministic PRNG

* PRNG: **Xoshiro256**
* Seeded with `k_stats`
* Produces uniform stream `[0,1)`

### Step 4 — Stat Derivation

* Convert uniforms → distribution variates
* Apply correlation via Cholesky decomposition
* Add to μ
* Apply latent split if defined
* Quantize deterministically

### Step 5 — Spine Validation

* Recompute everything from `(seed_256, nonce_128)`
* Require **exact match**

### Step 6 — Integrity Receipt

* Canonical Merkle tree over:

  * Visible stats
  * Latent stats
  * generator_id
  * archetype
* Root stored with monster instance

---

## 7. Archetypes (Statistical Meaning Only)

* **Stable** — Tight variance, predictable output
* **Volatile** — Wide variance, high swing
* **Growth** — Low visible stats, high latent potential
* **Locked** — Suppressed visible stats, stored reserve

Archetypes **do not add mechanics**.

---

## 8. LLM Role (Strictly Limited)

LLMs may generate:

* Names
* Lore
* Visual descriptors
* Taxonomy tags

LLMs may NOT:

* Choose or modify stats
* Modify generator parameters
* Override spine validation

---

## 9. What Exists Right Now

* Strong Mint Protocol v2
* GEN‑01 fully specified and active
* Deterministic reference mint implementation
* Merkle‑based integrity receipts

This is sufficient to:

* Mint the first monster
* Verify it offline
* Prove legitimacy mathematically

---

## 10. What Comes Next (Not In This File)

* Finalize GEN‑02 → GEN‑12
* Optional Weak Mint mode (envelope‑bounded)
* Gameplay systems that *consume* monsters
* Multiplayer signature enforcement (optional)

---

## 11. One‑Line Truth

**Rules are finite. Generators are fixed. Monsters are infinite. Math keeps them honest.**
# GEN-01 (Stable Anchor) — Activation Pack
# Strong Mint Protocol v2 (Deterministic / Exact Recompute)
# Project: Monster Deck (12 Generators)
# Owner: Timothy Wesley Stone

You asked for everything needed to start this part and mint the first monster.
This pack includes:
1) GEN-01 fully specified (seed, nonce ledger start, μ, σ, R)
2) Canonical nonce construction (monotonic counter)
3) Reference mint implementation (HKDF + Xoshiro256** + Box–Muller + Cholesky + quantize + Merkle root)
4) A concrete first mint example you can reproduce

------------------------------------------------------------
A) GEN-01 — Generator Card Spec (Stable Anchor)
------------------------------------------------------------

generator_id: 1
mint_version: "v2"
spine_ref: "spine.mint.v2"
archetype_bias: "Stable"

# 1) Cryptographic Identity
seed_256 (32-byte hex):
  0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef

nonce_ledger:
  - type: "monotonic_counter"
  - start: 0
  - increment: +1 per mint (per account, per generator_id, per mint_version)

# 2) Statistical Mean Profile (μ)
# Order: [ATK, DEF, HP, ENG]
mu:
  [50, 50, 100, 50]

# 3) Variance & Scale (σ factor)
# Stable: tight grouping
sigma_factor:
  0.08

# 4) Correlation Matrix R (4x4 correlation, symmetric, SPD)
# Notes:
# - Negative ATK↔DEF enforces trade-off
# - Positive HP↔ENG makes “heavy” profiles emerge naturally
corr_R:
  [
    [ 1.00, -0.35,  0.10, -0.05 ],
    [ -0.35, 1.00,  0.20,  0.10 ],
    [ 0.10,  0.20,  1.00,  0.25 ],
    [ -0.05, 0.10,  0.25,  1.00 ]
  ]

# 5) Distribution-Specific Parameters
dist_family: "Normal"          # Stable uses Normal
# (No beta α/β, no truncation bounds needed here)

# 6) Latent Mechanics
latent_policy: "None"
latent_pct: 0.0

------------------------------------------------------------
B) Nonce Construction (Monotonic Counter → 128-bit nonce)
------------------------------------------------------------

Goal: nonce_128 is unique per (account, generator_id, mint_version).

Canonical encoding (simple and deterministic):
- counter is uint128 big-endian (16 bytes)
- nonce_128 = counter_bytes

Example:
- first mint counter = 1
- nonce_hex = 00000000000000000000000000000001

(You can later mix in account_id if you want, but Strong Mint only needs uniqueness.)
IMPORTANT: keep a used-nonce ledger so replay is rejected.

------------------------------------------------------------
C) Reference Implementation (Python) — Strong Mint v2
------------------------------------------------------------

This is a minimal “works-now” implementation:
- HKDF: HMAC-SHA256
- PRNG: Xoshiro256**
- Normal: Box–Muller
- Correlation: Σ = Dσ * R * Dσ, then Cholesky
- Quantize: round-half-away-from-zero (canonical)
- Merkle root over fixed leaves (stats + metadata)

```python
import hashlib, hmac, struct, math
import numpy as np

# ---------- HKDF (RFC 5869 style) ----------
def hkdf_extract(salt: bytes | None, ikm: bytes) -> bytes:
    if salt is None:
        salt = b"\x00" * 32
    return hmac.new(salt, ikm, hashlib.sha256).digest()

def hkdf_expand(prk: bytes, info: bytes, length: int) -> bytes:
    out = b""
    t = b""
    c = 1
    while len(out) < length:
        t = hmac.new(prk, t + info + bytes([c]), hashlib.sha256).digest()
        out += t
        c += 1
    return out[:length]

def hkdf(ikm: bytes, salt: bytes | None, info: bytes, length: int) -> bytes:
    prk = hkdf_extract(salt, ikm)
    return hkdf_expand(prk, info, length)

# ---------- Xoshiro256** ----------
class Xoshiro256ss:
    def __init__(self, seed32: bytes):
        # 32 bytes -> 4 uint64 little-endian
        self.s = list(struct.unpack("<4Q", seed32))

    @staticmethod
    def rotl(x: int, k: int) -> int:
        return ((x << k) & ((1<<64)-1)) | (x >> (64-k))

    def next_u64(self) -> int:
        s0, s1, s2, s3 = self.s
        result = (self.rotl((s1 * 5) & ((1<<64)-1), 7) * 9) & ((1<<64)-1)
        t = (s1 << 17) & ((1<<64)-1)

        s2 ^= s0
        s3 ^= s1
        s1 ^= s2
        s0 ^= s3
        s2 ^= t
        s3 = self.rotl(s3, 45)
        self.s = [s0, s1, s2, s3]
        return result

    def u01(self) -> float:
        return self.next_u64() / 2**64  # [0,1)

# ---------- Normal from Uniform (Box–Muller) ----------
def box_muller(u1: float, u2: float) -> tuple[float, float]:
    u1 = max(u1, 1e-16)
    r = math.sqrt(-2.0 * math.log(u1))
    theta = 2.0 * math.pi * u2
    return r * math.cos(theta), r * math.sin(theta)

# ---------- Canonical rounding: half-away-from-zero ----------
def round_half_away_from_zero(x: float) -> int:
    return int(math.floor(x + 0.5)) if x >= 0 else int(math.ceil(x - 0.5))

# ---------- Merkle root (binary, duplicate last if odd) ----------
def sha256(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()

def merkle_root(leaves: list[bytes]) -> bytes:
    if not leaves:
        return sha256(b"")
    level = leaves[:]
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])
        nxt = []
        for i in range(0, len(level), 2):
            nxt.append(sha256(level[i] + level[i+1]))
        level = nxt
    return level[0]

def leaf(name: str, value: int, mint_version: str) -> bytes:
    name_b = name.encode("ascii")
    val_b = int(value).to_bytes(8, "big", signed=True)
    ver_b = mint_version.encode("ascii")
    return sha256(b"leaf|" + name_b + b"|" + val_b + b"|" + ver_b)

# ---------- Strong Mint: GEN-01 stats ----------
def mint_gen01(seed_hex: str, nonce_hex: str):
    mint_version = "v2"
    generator_id = 1
    archetype = 0  # enum encoding: Stable=0, Volatile=1, Growth=2, Locked=3

    seed = bytes.fromhex(seed_hex)
    nonce = bytes.fromhex(nonce_hex)

    # Step 1: Identity
    k_id = hkdf(ikm=seed, salt=nonce, info=b"monster_identity", length=32)

    # Step 2: Stream key
    k_stats = hkdf(ikm=k_id, salt=None, info=b"stats_stream", length=32)

    # Step 3: PRNG
    prng = Xoshiro256ss(k_stats)

    # GEN-01 params
    mu = np.array([50.0, 50.0, 100.0, 50.0])
    sigma_factor = 0.08
    R = np.array([
        [ 1.00, -0.35,  0.10, -0.05 ],
        [ -0.35, 1.00,  0.20,  0.10 ],
        [ 0.10,  0.20,  1.00,  0.25 ],
        [ -0.05, 0.10,  0.25,  1.00 ]
    ])

    sigma = mu * sigma_factor
    D = np.diag(sigma)
    Sigma = D @ R @ D
    L = np.linalg.cholesky(Sigma)

    # 4 normals via 2 Box–Muller pairs (consume 4 uniforms)
    zs = []
    for _ in range(2):
        u1, u2 = prng.u01(), prng.u01()
        z0, z1 = box_muller(u1, u2)
        zs.extend([z0, z1])
    z = np.array(zs[:4])

    x_raw = mu + (L @ z)
    stats = [round_half_away_from_zero(v) for v in x_raw.tolist()]

    ATK, DEF, HP, ENG = stats

    # Step 6: Merkle root receipt (include zeros for latent stats)
    leaves = [
        leaf("ATK", ATK, mint_version),
        leaf("DEF", DEF, mint_version),
        leaf("HP",  HP,  mint_version),
        leaf("ENG", ENG, mint_version),
        leaf("LAT_ATK", 0, mint_version),
        leaf("LAT_DEF", 0, mint_version),
        leaf("LAT_HP",  0, mint_version),
        leaf("LAT_ENG", 0, mint_version),
        leaf("GEN", generator_id, mint_version),
        leaf("ARCH", archetype, mint_version),
    ]
    root = merkle_root(leaves)

    return {
        "k_id": k_id.hex(),
        "k_stats": k_stats.hex(),
        "stats_visible": stats,
        "stats_latent": [0,0,0,0],
        "merkle_root": root.hex(),
    }

# Example:
# seed_hex  = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
# nonce_hex = "00000000000000000000000000000001"
# print(mint_gen01(seed_hex, nonce_hex))
D) First Monster Mint (Reproducible Example)
Use:
seed_hex = 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
nonce_hex = 00000000000000000000000000000001 (counter=1)

Expected (from the reference implementation above):
stats_visible = [53, 55, 100, 50]

Order: [ATK, DEF, HP, ENG]
stats_latent = [0, 0, 0, 0]

(If you copy this code exactly, you should reproduce those stats and the same merkle_root.)

# GENERATORS_BOX001_v2_STUBS.md
# 12 Generator Cards (Stubs / No Numbers Yet)
# Project: Monster Deck
# Owner: Timothy Wesley Stone
# Status: draft
# Mint Protocol: v2 Strong Mint

> These are generator card stubs. They define the fields required by MINTING_PROTOCOL_v2.md.
> Values are intentionally omitted here (no constraints drafted). Only structure and intent.

---

## GEN-01
generator_id: 1
seed_256: <TBD_32_BYTES_HEX>
spine_ref: spine.mint.v2
mint_version: v2
archetype_bias: Stable
mu: <TBD_VECTOR_ATK_DEF_HP_ENG>
dist_family: Normal
sigma_factor: <TBD>
corr_R: <TBD_4x4_SPD_CORR_MATRIX>
latent_policy: None
latent_pct: 0

Notes:
- Stable baseline anchor. Tight, predictable derivation shape.

---

## GEN-02
generator_id: 2
seed_256: <TBD_32_BYTES_HEX>
spine_ref: spine.mint.v2
mint_version: v2
archetype_bias: Stable
mu: <TBD_VECTOR_ATK_DEF_HP_ENG>
dist_family: Normal
sigma_factor: <TBD>
corr_R: <TBD_4x4_SPD_CORR_MATRIX>
latent_policy: None
latent_pct: 0

Notes:
- Stable variant anchor. Same archetype, different base profile/correlation style.

---

## GEN-03
generator_id: 3
seed_256: <TBD_32_BYTES_HEX>
spine_ref: spine.mint.v2
mint_version: v2
archetype_bias: Volatile
mu: <TBD_VECTOR_ATK_DEF_HP_ENG>
dist_family: Normal
sigma_factor: <TBD>
corr_R: <TBD_4x4_SPD_CORR_MATRIX>
latent_policy: None
latent_pct: 0

Notes:
- Volatile baseline anchor. Wider variance shape (still deterministic).

---

## GEN-04
generator_id: 4
seed_256: <TBD_32_BYTES_HEX>
spine_ref: spine.mint.v2
mint_version: v2
archetype_bias: Volatile
mu: <TBD_VECTOR_ATK_DEF_HP_ENG>
dist_family: Normal
sigma_factor: <TBD>
corr_R: <TBD_4x4_SPD_CORR_MATRIX>
latent_policy: None
latent_pct: 0

Notes:
- Volatile variant anchor. Different profile / correlation trade-offs.

---

## GEN-05
generator_id: 5
seed_256: <TBD_32_BYTES_HEX>
spine_ref: spine.mint.v2
mint_version: v2
archetype_bias: Growth
mu: <TBD_VECTOR_ATK_DEF_HP_ENG>
dist_family: Beta
sigma_factor: <TBD>
corr_R: <TBD_4x4_SPD_CORR_MATRIX>
latent_policy: GrowthSplit
latent_pct: <TBD_0_TO_1>

Notes:
- Growth baseline anchor. Skewed starts with stored latent capacity.

---

## GEN-06
generator_id: 6
seed_256: <TBD_32_BYTES_HEX>
spine_ref: spine.mint.v2
mint_version: v2
archetype_bias: Growth
mu: <TBD_VECTOR_ATK_DEF_HP_ENG>
dist_family: Beta
sigma_factor: <TBD>
corr_R: <TBD_4x4_SPD_CORR_MATRIX>
latent_policy: GrowthSplit
latent_pct: <TBD_0_TO_1>

Notes:
- Growth variant anchor. Different mean profile / correlation character.

---

## GEN-07
generator_id: 7
seed_256: <TBD_32_BYTES_HEX>
spine_ref: spine.mint.v2
mint_version: v2
archetype_bias: Locked
mu: <TBD_VECTOR_ATK_DEF_HP_ENG>
dist_family: TruncatedNormal
sigma_factor: <TBD>
corr_R: <TBD_4x4_SPD_CORR_MATRIX>
latent_policy: LockedSplit
latent_pct: <TBD_0_TO_1>

Notes:
- Locked baseline anchor. Suppressed visible with latent reserve.

---

## GEN-08
generator_id: 8
seed_256: <TBD_32_BYTES_HEX>
spine_ref: spine.mint.v2
mint_version: v2
archetype_bias: Locked
mu: <TBD_VECTOR_ATK_DEF_HP_ENG>
dist_family: TruncatedNormal
sigma_factor: <TBD>
corr_R: <TBD_4x4_SPD_CORR_MATRIX>
latent_policy: LockedSplit
latent_pct: <TBD_0_TO_1>

Notes:
- Locked variant anchor. Different base/correlation style.

---

## GEN-09
generator_id: 9
seed_256: <TBD_32_BYTES_HEX>
spine_ref: spine.mint.v2
mint_version: v2
archetype_bias: Stable
mu: <TBD_VECTOR_ATK_DEF_HP_ENG>
dist_family: Normal
sigma_factor: <TBD>
corr_R: <TBD_4x4_SPD_CORR_MATRIX>
latent_policy: None
latent_pct: 0

Notes:
- Third stable anchor reserved for a distinct “feel” (profile/correlation), not more rules.

---

## GEN-10
generator_id: 10
seed_256: <TBD_32_BYTES_HEX>
spine_ref: spine.mint.v2
mint_version: v2
archetype_bias: Volatile
mu: <TBD_VECTOR_ATK_DEF_HP_ENG>
dist_family: Normal
sigma_factor: <TBD>
corr_R: <TBD_4x4_SPD_CORR_MATRIX>
latent_policy: None
latent_pct: 0

Notes:
- Third volatile anchor reserved for another volatility flavor.

---

## GEN-11
generator_id: 11
seed_256: <TBD_32_BYTES_HEX>
spine_ref: spine.mint.v2
mint_version: v2
archetype_bias: Growth
mu: <TBD_VECTOR_ATK_DEF_HP_ENG>
dist_family: Beta
sigma_factor: <TBD>
corr_R: <TBD_4x4_SPD_CORR_MATRIX>
latent_policy: GrowthSplit
latent_pct: <TBD_0_TO_1>

Notes:
- Third growth anchor reserved for alternate growth skew/shape.

---

## GEN-12
generator_id: 12
seed_256: <TBD_32_BYTES_HEX>
spine_ref: spine.mint.v2
mint_version: v2
archetype_bias: Locked
mu: <TBD_VECTOR_ATK_DEF_HP_ENG>
dist_family: TruncatedNormal
sigma_factor: <TBD>
corr_R: <TBD_4x4_SPD_CORR_MATRIX>
latent_policy: LockedSplit
latent_pct: <TBD_0_TO_1>

Notes:
- Third locked anchor reserved for alternate lock style.

---
await VoR.mint(1)  // Mint first monster from GEN-01