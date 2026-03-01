// VøR Monster Deck — Nonce Ledger (Monotonic Counter)
// Prevents replay attacks and ensures uniqueness

class NonceLedger {
    constructor() {
        this.ledger = new Map();
        this.counters = new Map();
    }
    
    /**
     * Generate next nonce for a given context
     */
    nextNonce(account, generatorId, mintVersion) {
        const key = `${account}_${generatorId}_${mintVersion}`;
        
        if (!this.counters.has(key)) {
            this.counters.set(key, 1);
            this.ledger.set(key, new Set());
        }
        
        const counter = this.counters.get(key);
        const nonceHex = counter.toString(16).padStart(32, '0');
        
        this.counters.set(key, counter + 1);
        this.ledger.get(key).add(nonceHex);
        
        return nonceHex;
    }
    
    /**
     * Check if a nonce has been used
     */
    hasBeenUsed(account, generatorId, mintVersion, nonceHex) {
        const key = `${account}_${generatorId}_${mintVersion}`;
        const used = this.ledger.get(key);
        return used ? used.has(nonceHex) : false;
    }
    
    /**
     * Mark a nonce as used (for external validation)
     */
    markUsed(account, generatorId, mintVersion, nonceHex) {
        const key = `${account}_${generatorId}_${mintVersion}`;
        
        if (!this.ledger.has(key)) {
            this.ledger.set(key, new Set());
        }
        
        if (this.hasBeenUsed(account, generatorId, mintVersion, nonceHex)) {
            throw new Error(`Nonce replay detected: ${nonceHex}`);
        }
        
        this.ledger.get(key).add(nonceHex);
    }
    
    /**
     * Get current counter value (for debugging)
     */
    getCurrentCounter(account, generatorId, mintVersion) {
        const key = `${account}_${generatorId}_${mintVersion}`;
        return this.counters.get(key) || 0;
    }
    
    /**
     * Save ledger to localStorage
     */
    save() {
        const data = {
            counters: Array.from(this.counters.entries()),
            ledger: Array.from(this.ledger.entries()).map(([k, v]) => [k, Array.from(v)])
        };
        localStorage.setItem('vor_nonce_ledger', JSON.stringify(data));
    }
    
    /**
     * Load ledger from localStorage
     */
    load() {
        const stored = localStorage.getItem('vor_nonce_ledger');
        if (!stored) return;
        
        const data = JSON.parse(stored);
        this.counters = new Map(data.counters);
        this.ledger = new Map(data.ledger.map(([k, v]) => [k, new Set(v)]));
    }
    
    /**
     * Clear all nonces (use with caution)
     */
    clear() {
        this.ledger.clear();
        this.counters.clear();
        localStorage.removeItem('vor_nonce_ledger');
    }
}

export default NonceLedger;
