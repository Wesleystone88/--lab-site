// νόησις Graph Model - Core data structures and operations

class Graph {
    constructor() {
        this.nodes = [];
        this.edges = [];
        this.validated = false;
        this.nextNodeId = 1;
    }

    // Generate cryptographic seed (simplified SHA-256 simulation)
    generateSeed() {
        const timestamp = Date.now();
        const random = Math.random();
        const str = `${timestamp}-${random}`;
        // Simplified hash simulation (in production, use SubtleCrypto)
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash;
        }
        return Math.abs(hash).toString(16).padStart(16, '0');
    }

    // Generate identity hash from seed + template
    generateHash(seed, template) {
        const combined = `${seed}-${template}`;
        let hash = 0;
        for (let i = 0; i < combined.length; i++) {
            const char = combined.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash;
        }
        return Math.abs(hash).toString(16).padStart(64, '0').substring(0, 64);
    }

    // Create new node
    createNode(template, x, y) {
        const seed = this.generateSeed();
        const hash = this.generateHash(seed, template);
        
        const node = {
            id: `node-${this.nextNodeId++}`,
            template: template,
            seed: seed,
            hash: hash,
            version: '0.1.0',
            state: 'evolving',
            body: `[${template} content will go here]`,
            x: x,
            y: y,
            timestamp: new Date().toISOString()
        };

        this.nodes.push(node);
        this.validated = false;
        return node;
    }

    // Create node from imported card
    createNodeFromCard(cardData, x, y) {
        const node = {
            id: `node-${this.nextNodeId++}`,
            template: cardData.id,
            seed: cardData.seed,
            hash: cardData.hash,
            version: cardData.version || '0.1.0',
            state: 'evolving',
            body: cardData.body,
            x: x,
            y: y,
            timestamp: new Date().toISOString(),
            imported: true,
            cardData: {
                name: cardData.name,
                namespace: cardData.namespace,
                deck_mode: cardData.deck_mode,
                dependencies: cardData.dependencies
            }
        };

        this.nodes.push(node);
        this.validated = false;
        return node;
    }

    // Create edge between nodes
    createEdge(sourceId, targetId, type = 'DEPENDENCY') {
        const edge = {
            id: `edge-${sourceId}-${targetId}`,
            source: sourceId,
            target: targetId,
            type: type,
            timestamp: new Date().toISOString()
        };

        this.edges.push(edge);
        this.validated = false;
        return edge;
    }

    // Get node by ID
    getNode(id) {
        return this.nodes.find(n => n.id === id);
    }

    // Update node body
    updateNodeBody(id, body) {
        const node = this.getNode(id);
        if (node && node.state !== 'frozen') {
            node.body = body;
            this.validated = false;
            return true;
        }
        return false;
    }

    // Update node position
    updateNodePosition(id, x, y) {
        const node = this.getNode(id);
        if (node) {
            node.x = x;
            node.y = y;
            return true;
        }
        return false;
    }

    // Validate graph (simple validation for MVP)
    validate() {
        let valid = true;
        const errors = [];

        // Check for cycles (simple DFS)
        const hasCycle = () => {
            const visited = new Set();
            const recStack = new Set();

            const dfs = (nodeId) => {
                visited.add(nodeId);
                recStack.add(nodeId);

                const outgoing = this.edges.filter(e => e.source === nodeId);
                for (const edge of outgoing) {
                    if (!visited.has(edge.target)) {
                        if (dfs(edge.target)) return true;
                    } else if (recStack.has(edge.target)) {
                        return true;
                    }
                }

                recStack.delete(nodeId);
                return false;
            };

            for (const node of this.nodes) {
                if (!visited.has(node.id)) {
                    if (dfs(node.id)) return true;
                }
            }
            return false;
        };

        if (hasCycle()) {
            errors.push('Graph contains cycles');
            valid = false;
        }

        // Check for orphaned edges
        for (const edge of this.edges) {
            if (!this.getNode(edge.source) || !this.getNode(edge.target)) {
                errors.push(`Edge ${edge.id} references non-existent node`);
                valid = false;
            }
        }

        // Mark nodes as stable if valid
        if (valid) {
            this.nodes.forEach(node => {
                if (node.state === 'evolving') {
                    node.state = 'stable';
                }
            });
            this.validated = true;
        }

        return { valid, errors };
    }

    // Freeze graph (create immutable snapshot)
    freeze() {
        if (!this.validated) {
            return { success: false, error: 'Graph must be validated before freezing' };
        }

        this.nodes.forEach(node => {
            if (node.state === 'stable') {
                node.state = 'frozen';
            }
        });

        return { success: true };
    }

    // Serialize to JSON
    toJSON() {
        return {
            nodes: this.nodes,
            edges: this.edges,
            validated: this.validated
        };
    }

    // Load from JSON
    fromJSON(data) {
        this.nodes = data.nodes || [];
        this.edges = data.edges || [];
        this.validated = data.validated || false;
        
        // Update nextNodeId
        if (this.nodes.length > 0) {
            const maxId = Math.max(...this.nodes.map(n => {
                const match = n.id.match(/node-(\d+)/);
                return match ? parseInt(match[1]) : 0;
            }));
            this.nextNodeId = maxId + 1;
        }
    }
}
