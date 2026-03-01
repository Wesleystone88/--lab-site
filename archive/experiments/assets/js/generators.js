// VøR Monster Deck — Generator Specifications
// GEN-01 fully specified, GEN-02 through GEN-12 are stubs

export const GENERATORS = {
    1: {
        generator_id: 1,
        name: 'Stable Anchor',
        seed_256: '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef',
        spine_ref: 'spine.mint.v2',
        mint_version: 'v2',
        archetype_bias: 'Stable',
        
        // Statistical parameters
        mu: [50, 50, 100, 50], // [ATK, DEF, HP, ENG]
        sigma_factor: 0.08,
        
        // Correlation matrix (4x4, symmetric, SPD)
        corr_R: [
            [ 1.00, -0.35,  0.10, -0.05 ],
            [-0.35,  1.00,  0.20,  0.10 ],
            [ 0.10,  0.20,  1.00,  0.25 ],
            [-0.05,  0.10,  0.25,  1.00 ]
        ],
        
        dist_family: 'Normal',
        latent_policy: 'None',
        latent_pct: 0.0
    },
    
    // Stubs for GEN-02 through GEN-12
    2: { generator_id: 2, name: 'Stable Variant', archetype_bias: 'Stable', status: 'stub' },
    3: { generator_id: 3, name: 'Volatile Baseline', archetype_bias: 'Volatile', status: 'stub' },
    4: { generator_id: 4, name: 'Volatile Variant', archetype_bias: 'Volatile', status: 'stub' },
    5: { generator_id: 5, name: 'Growth Baseline', archetype_bias: 'Growth', status: 'stub' },
    6: { generator_id: 6, name: 'Growth Variant', archetype_bias: 'Growth', status: 'stub' },
    7: { generator_id: 7, name: 'Locked Baseline', archetype_bias: 'Locked', status: 'stub' },
    8: { generator_id: 8, name: 'Locked Variant', archetype_bias: 'Locked', status: 'stub' },
    9: { generator_id: 9, name: 'Stable Reserve', archetype_bias: 'Stable', status: 'stub' },
    10: { generator_id: 10, name: 'Volatile Reserve', archetype_bias: 'Volatile', status: 'stub' },
    11: { generator_id: 11, name: 'Growth Reserve', archetype_bias: 'Growth', status: 'stub' },
    12: { generator_id: 12, name: 'Locked Reserve', archetype_bias: 'Locked', status: 'stub' }
};

export function getGenerator(id) {
    const gen = GENERATORS[id];
    if (!gen) throw new Error(`Generator ${id} not found`);
    if (gen.status === 'stub') throw new Error(`Generator ${id} is not yet implemented`);
    return gen;
}
