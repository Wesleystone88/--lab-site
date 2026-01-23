// VøR — Noctyra Monster Deck
import { mintMonster } from './mint-engine.js';
import { getGenerator } from './generators.js';
import NonceLedger from './nonce-ledger.js';

const nonceLedger = new NonceLedger();

document.addEventListener('DOMContentLoaded', () => {
    nonceLedger.load();
    console.log('VøR Monster Deck — Strong Mint v2 Engine initialized');
    
    // Make mint function available globally for testing
    window.VoR = {
        mint: async (generatorId, account = 'player1') => {
            const gen = getGenerator(generatorId);
            const nonce = nonceLedger.nextNonce(account, generatorId, 'v2');
            const monster = await mintMonster(gen, nonce);
            nonceLedger.save();
            return monster;
        },
        getGenerator,
        nonceLedger
    };
    
    console.log('Test with: await VoR.mint(1)');
});
