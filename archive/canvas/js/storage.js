// νόησις Storage Layer - localStorage persistence

const Storage = {
    KEYS: {
        WORKSPACE: 'noesis_workspace',
        GRAPH: 'noesis_graph',
        SNAPSHOTS: 'noesis_snapshots'
    },

    // Save workspace metadata
    saveWorkspace(name) {
        localStorage.setItem(this.KEYS.WORKSPACE, JSON.stringify({ name, timestamp: Date.now() }));
    },

    // Load workspace metadata
    loadWorkspace() {
        const data = localStorage.getItem(this.KEYS.WORKSPACE);
        return data ? JSON.parse(data) : { name: 'Untitled Workspace', timestamp: Date.now() };
    },

    // Save complete graph state
    saveGraph(graph) {
        localStorage.setItem(this.KEYS.GRAPH, JSON.stringify(graph));
    },

    // Load graph state
    loadGraph() {
        const data = localStorage.getItem(this.KEYS.GRAPH);
        return data ? JSON.parse(data) : { nodes: [], edges: [], validated: false };
    },

    // Save snapshot
    saveSnapshot(graph) {
        const snapshots = this.loadSnapshots();
        const snapshot = {
            id: Date.now(),
            timestamp: new Date().toISOString(),
            graph: JSON.parse(JSON.stringify(graph))
        };
        snapshots.push(snapshot);
        localStorage.setItem(this.KEYS.SNAPSHOTS, JSON.stringify(snapshots));
        return snapshot;
    },

    // Load all snapshots
    loadSnapshots() {
        const data = localStorage.getItem(this.KEYS.SNAPSHOTS);
        return data ? JSON.parse(data) : [];
    },

    // Clear all data
    clearAll() {
        Object.values(this.KEYS).forEach(key => localStorage.removeItem(key));
    }
};
