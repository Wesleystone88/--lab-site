// VøR Monster Deck — Strong Mint Protocol v2 Engine
// Project: Noctyra Monster TCG
// Owner: Timothy Wesley Stone
// Status: Active (Generator Phase)

/**
 * Core deterministic monster minting engine.
 * Same seed + nonce = same monster, always.
 * No randomness at runtime. Pure mathematical derivation.
 */

// ============================================================================
// HKDF (RFC 5869) — Key Derivation
// ============================================================================

async function hmacSha256(key, message) {
    const cryptoKey = await crypto.subtle.importKey(
        'raw', key, { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']
    );
    const signature = await crypto.subtle.sign('HMAC', cryptoKey, message);
    return new Uint8Array(signature);
}

async function hkdfExtract(salt, ikm) {
    if (!salt) salt = new Uint8Array(32);
    return await hmacSha256(salt, ikm);
}

async function hkdfExpand(prk, info, length) {
    const blocks = [];
    let t = new Uint8Array(0);
    let counter = 1;
    
    while (blocks.reduce((sum, b) => sum + b.length, 0) < length) {
        const input = new Uint8Array([...t, ...info, counter]);
        t = await hmacSha256(prk, input);
        blocks.push(t);
        counter++;
    }
    
    const okm = new Uint8Array(blocks.reduce((sum, b) => sum + b.length, 0));
    let offset = 0;
    for (const block of blocks) {
        okm.set(block, offset);
        offset += block.length;
    }
    
    return okm.slice(0, length);
}

async function hkdf(ikm, salt, info, length) {
    const prk = await hkdfExtract(salt, ikm);
    return await hkdfExpand(prk, info, length);
}

// ============================================================================
// Xoshiro256** PRNG — Deterministic Random Stream
// ============================================================================

class Xoshiro256ss {
    constructor(seed32) {
        const view = new DataView(seed32.buffer);
        this.state = [
            view.getBigUint64(0, true),
            view.getBigUint64(8, true),
            view.getBigUint64(16, true),
            view.getBigUint64(24, true)
        ];
    }
    
    static rotl(x, k) {
        const mask = (1n << 64n) - 1n;
        return ((x << BigInt(k)) & mask) | (x >> BigInt(64 - k));
    }
    
    next() {
        const [s0, s1, s2, s3] = this.state;
        const mask = (1n << 64n) - 1n;
        
        const result = (Xoshiro256ss.rotl((s1 * 5n) & mask, 7) * 9n) & mask;
        const t = (s1 << 17n) & mask;
        
        let ns2 = s2 ^ s0;
        let ns3 = s3 ^ s1;
        let ns1 = s1 ^ ns2;
        let ns0 = s0 ^ ns3;
        ns2 ^= t;
        ns3 = Xoshiro256ss.rotl(ns3, 45);
        
        this.state = [ns0, ns1, ns2, ns3];
        return result;
    }
    
    u01() {
        return Number(this.next()) / Math.pow(2, 64);
    }
}

// ============================================================================
// Box-Muller Transform — Uniform to Normal
// ============================================================================

function boxMuller(u1, u2) {
    u1 = Math.max(u1, 1e-16);
    const r = Math.sqrt(-2.0 * Math.log(u1));
    const theta = 2.0 * Math.PI * u2;
    return [r * Math.cos(theta), r * Math.sin(theta)];
}

// ============================================================================
// Matrix Operations — Cholesky Decomposition
// ============================================================================

function cholesky(matrix) {
    const n = matrix.length;
    const L = Array(n).fill(0).map(() => Array(n).fill(0));
    
    for (let i = 0; i < n; i++) {
        for (let j = 0; j <= i; j++) {
            let sum = 0;
            for (let k = 0; k < j; k++) {
                sum += L[i][k] * L[j][k];
            }
            
            if (i === j) {
                L[i][j] = Math.sqrt(matrix[i][i] - sum);
            } else {
                L[i][j] = (matrix[i][j] - sum) / L[j][j];
            }
        }
    }
    
    return L;
}

function matrixVectorMultiply(matrix, vector) {
    return matrix.map(row => 
        row.reduce((sum, val, i) => sum + val * vector[i], 0)
    );
}

function buildCovarianceMatrix(mu, sigma_factor, corr_R) {
    const sigma = mu.map(m => m * sigma_factor);
    const n = mu.length;
    const Sigma = Array(n).fill(0).map(() => Array(n).fill(0));
    
    for (let i = 0; i < n; i++) {
        for (let j = 0; j < n; j++) {
            Sigma[i][j] = sigma[i] * corr_R[i][j] * sigma[j];
        }
    }
    
    return Sigma;
}

// ============================================================================
// Canonical Rounding — Half Away From Zero
// ============================================================================

function roundHalfAwayFromZero(x) {
    return x >= 0 ? Math.floor(x + 0.5) : Math.ceil(x - 0.5);
}

// ============================================================================
// Merkle Tree — Integrity Receipt
// ============================================================================

async function sha256(data) {
    const buffer = await crypto.subtle.digest('SHA-256', data);
    return new Uint8Array(buffer);
}

async function encodeLeaf(name, value, mintVersion) {
    const nameBytes = new TextEncoder().encode(name);
    const valueBytes = new DataView(new ArrayBuffer(8));
    valueBytes.setBigInt64(0, BigInt(value), false);
    const versionBytes = new TextEncoder().encode(mintVersion);
    
    const combined = new Uint8Array([
        ...new TextEncoder().encode('leaf|'),
        ...nameBytes,
        ...new TextEncoder().encode('|'),
        ...new Uint8Array(valueBytes.buffer),
        ...new TextEncoder().encode('|'),
        ...versionBytes
    ]);
    
    return await sha256(combined);
}

async function merkleRoot(leaves) {
    if (leaves.length === 0) return await sha256(new Uint8Array());
    
    let level = leaves.slice();
    
    while (level.length > 1) {
        if (level.length % 2 === 1) {
            level.push(level[level.length - 1]);
        }
        
        const nextLevel = [];
        for (let i = 0; i < level.length; i += 2) {
            const combined = new Uint8Array([...level[i], ...level[i + 1]]);
            nextLevel.push(await sha256(combined));
        }
        level = nextLevel;
    }
    
    return level[0];
}

// ============================================================================
// Monster Minting — Strong Mint v2
// ============================================================================

async function mintMonster(generatorSpec, nonceHex) {
    const mintVersion = 'v2';
    
    const seed = hexToBytes(generatorSpec.seed_256);
    const nonce = hexToBytes(nonceHex);
    
    // Step 1: Identity key
    const k_id = await hkdf(seed, nonce, new TextEncoder().encode('monster_identity'), 32);
    
    // Step 2: Stats stream key
    const k_stats = await hkdf(k_id, null, new TextEncoder().encode('stats_stream'), 32);
    
    // Step 3: Initialize PRNG
    const prng = new Xoshiro256ss(k_stats);
    
    // Step 4: Build covariance and Cholesky
    const { mu, sigma_factor, corr_R } = generatorSpec;
    const Sigma = buildCovarianceMatrix(mu, sigma_factor, corr_R);
    const L = cholesky(Sigma);
    
    // Generate 4 standard normals
    const normals = [];
    for (let i = 0; i < 2; i++) {
        const [z0, z1] = boxMuller(prng.u01(), prng.u01());
        normals.push(z0, z1);
    }
    
    // Apply correlation: x = μ + L*z
    const correlatedNormals = matrixVectorMultiply(L, normals);
    const rawStats = mu.map((m, i) => m + correlatedNormals[i]);
    
    // Step 5: Quantize
    const statsVisible = rawStats.map(roundHalfAwayFromZero);
    const statsLatent = [0, 0, 0, 0];
    
    // Step 6: Merkle integrity receipt
    const leaves = await Promise.all([
        encodeLeaf('ATK', statsVisible[0], mintVersion),
        encodeLeaf('DEF', statsVisible[1], mintVersion),
        encodeLeaf('HP', statsVisible[2], mintVersion),
        encodeLeaf('ENG', statsVisible[3], mintVersion),
        encodeLeaf('LAT_ATK', 0, mintVersion),
        encodeLeaf('LAT_DEF', 0, mintVersion),
        encodeLeaf('LAT_HP', 0, mintVersion),
        encodeLeaf('LAT_ENG', 0, mintVersion),
        encodeLeaf('GEN', generatorSpec.generator_id, mintVersion),
        encodeLeaf('ARCH', 0, mintVersion)
    ]);
    
    const root = await merkleRoot(leaves);
    
    return {
        k_id: bytesToHex(k_id),
        k_stats: bytesToHex(k_stats),
        stats_visible: statsVisible,
        stats_latent: statsLatent,
        merkle_root: bytesToHex(root),
        generator_id: generatorSpec.generator_id,
        archetype: 'Stable',
        nonce: nonceHex
    };
}

// ============================================================================
// Utilities
// ============================================================================

function hexToBytes(hex) {
    const bytes = new Uint8Array(hex.length / 2);
    for (let i = 0; i < hex.length; i += 2) {
        bytes[i / 2] = parseInt(hex.substr(i, 2), 16);
    }
    return bytes;
}

function bytesToHex(bytes) {
    return Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
}

// ============================================================================
// Export
// ============================================================================

export { mintMonster, Xoshiro256ss, boxMuller, cholesky };
