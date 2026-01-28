// νόησις Canvas Controller - UI and interaction layer

class CanvasController {
    constructor() {
        this.graph = new Graph();
        this.mode = 'navigate'; // 'navigate' or 'bind'
        this.selectedNode = null;
        this.bindSourceNode = null;
        this.draggedNode = null;
        this.panOffset = { x: 0, y: 0 };
        this.isDragging = false;
        this.dragStart = { x: 0, y: 0 };
        this.ghostNode = null; // Ghost preview node
        this.dragListenersSetup = false;
        
        this.init();
    }

    init() {
        // Load saved state
        const savedGraph = Storage.loadGraph();
        if (savedGraph.nodes.length > 0) {
            this.graph.fromJSON(savedGraph);
            this.log('info', 'Workspace loaded from storage');
        }

        const workspace = Storage.loadWorkspace();
        document.getElementById('workspace-name').textContent = workspace.name;

        // Setup event listeners
        this.setupEventListeners();
        this.setupImportListeners();
        
        // Initial render
        this.render();
        
        this.log('success', 'νόησις Canvas initialized');
    }

    setupEventListeners() {
        const canvas = document.getElementById('canvas');
        const contextMenu = document.getElementById('context-menu');

        // Canvas interactions
        canvas.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            const rect = canvas.getBoundingClientRect();
            contextMenu.style.left = e.clientX + 'px';
            contextMenu.style.top = e.clientY + 'px';
            contextMenu.classList.remove('hidden');
            this.contextMenuPos = { 
                x: e.clientX - rect.left - this.panOffset.x, 
                y: e.clientY - rect.top - this.panOffset.y 
            };
        });

        canvas.addEventListener('click', (e) => {
            if (!contextMenu.classList.contains('hidden')) {
                contextMenu.classList.add('hidden');
            }
        });

        // Context menu actions
        document.querySelectorAll('.menu-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const action = e.target.dataset.action;
                contextMenu.classList.add('hidden');
                
                if (action === 'spawn') {
                    this.showSpawnModal();
                } else if (action === 'import') {
                    this.showImportModal();
                } else if (action === 'bind-mode') {
                    this.toggleBindMode();
                }
            });
        });

        // Top bar buttons
        document.getElementById('validate-btn').addEventListener('click', () => this.validateGraph());
        document.getElementById('snapshot-btn').addEventListener('click', () => this.createSnapshot());
        document.getElementById('clear-log-btn').addEventListener('click', () => this.clearLog());

        // Workspace name
        document.getElementById('workspace-name').addEventListener('blur', (e) => {
            Storage.saveWorkspace(e.target.textContent);
            this.log('info', `Workspace renamed to: ${e.target.textContent}`);
        });

        // Modals
        this.setupModalListeners();

        // Node search
        document.getElementById('node-search').addEventListener('input', (e) => {
            this.filterNodes(e.target.value);
        });

        // Canvas panning
        canvas.addEventListener('mousedown', (e) => {
            if (e.target === canvas || e.target.id === 'nodes-layer' || e.target.id === 'edges-layer') {
                this.isDragging = true;
                this.dragStart = { x: e.clientX - this.panOffset.x, y: e.clientY - this.panOffset.y };
                canvas.classList.add('grabbing');
            }
        });

        canvas.addEventListener('mousemove', (e) => {
            if (this.isDragging) {
                this.panOffset.x = e.clientX - this.dragStart.x;
                this.panOffset.y = e.clientY - this.dragStart.y;
                this.render();
            }
        });

        canvas.addEventListener('mouseup', () => {
            this.isDragging = false;
            canvas.classList.remove('grabbing');
        });
    }

    setupModalListeners() {
        // Close modals
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                modal.classList.add('hidden');
                
                // Remove ghost on cancel
                if (modal.id === 'spawn-modal') {
                    this.removeGhost();
                }
            });
        });

        // Spawn modal - update ghost when template changes
        document.getElementById('template-select').addEventListener('change', (e) => {
            if (this.ghostNode) {
                this.ghostNode.template = e.target.value;
                this.render();
            }
        });

        // Spawn modal confirm
        document.getElementById('spawn-confirm-btn').addEventListener('click', () => {
            const template = document.getElementById('template-select').value;
            const pos = this.contextMenuPos || { x: 400, y: 300 };
            const node = this.graph.createNode(template, pos.x, pos.y);
            this.log('success', `Spawned ${template} at (${Math.round(pos.x)}, ${Math.round(pos.y)})`);
            this.removeGhost();
            this.saveAndRender();
            document.getElementById('spawn-modal').classList.add('hidden');
        });

        // Inspector modal
        document.getElementById('save-inspector-btn').addEventListener('click', () => {
            if (this.selectedNode) {
                const newBody = document.getElementById('inspector-body').value;
                if (this.graph.updateNodeBody(this.selectedNode.id, newBody)) {
                    this.log('success', `Updated ${this.selectedNode.template} body`);
                    this.saveAndRender();
                } else {
                    this.log('error', 'Cannot edit frozen node');
                }
                document.getElementById('inspector-modal').classList.add('hidden');
            }
        });
    }

    showSpawnModal() {
        const template = document.getElementById('template-select').value;
        const pos = this.contextMenuPos || { x: 400, y: 300 };
        
        // Create ghost preview
        this.ghostNode = {
            id: 'ghost',
            template: template,
            hash: 'preview...',
            state: 'evolving',
            x: pos.x,
            y: pos.y
        };
        
        this.render();
        this.log('info', `Ghost preview: ${template}`);
        document.getElementById('spawn-modal').classList.remove('hidden');
    }

    removeGhost() {
        if (this.ghostNode) {
            this.ghostNode = null;
            this.render();
        }
    }

    showInspector(node) {
        this.selectedNode = node;
        document.getElementById('inspector-id').textContent = node.template;
        document.getElementById('inspector-seed').textContent = node.seed;
        document.getElementById('inspector-hash').textContent = node.hash.substring(0, 16) + '...';
        document.getElementById('inspector-version').textContent = node.version;
        document.getElementById('inspector-state').textContent = node.state;
        document.getElementById('inspector-body').value = node.body;
        document.getElementById('inspector-modal').classList.remove('hidden');
    }

    toggleBindMode() {
        if (this.mode === 'navigate') {
            this.mode = 'bind';
            this.bindSourceNode = null;
            document.getElementById('mode-indicator').textContent = 'Bind Mode';
            document.getElementById('mode-indicator').classList.add('bind-mode');
            document.getElementById('canvas').classList.add('bind-mode');
            this.log('info', 'Bind mode activated - Click source, then target');
        } else {
            this.mode = 'navigate';
            this.bindSourceNode = null;
            document.getElementById('mode-indicator').textContent = 'Navigate Mode';
            document.getElementById('mode-indicator').classList.remove('bind-mode');
            document.getElementById('canvas').classList.remove('bind-mode');
            this.log('info', 'Navigate mode activated');
        }
    }

    handleNodeClick(node, e) {
        if (this.mode === 'bind') {
            if (!this.bindSourceNode) {
                this.bindSourceNode = node;
                this.log('info', `Bind source: ${node.template}`);
            } else {
                if (this.bindSourceNode.id !== node.id) {
                    this.graph.createEdge(this.bindSourceNode.id, node.id);
                    this.log('success', `Created edge: ${this.bindSourceNode.template} → ${node.template}`);
                    this.saveAndRender();
                }
                this.bindSourceNode = null;
                this.toggleBindMode();
            }
        } else if (e.detail === 2) {
            // Double click - open inspector
            this.showInspector(node);
        } else {
            // Single click - select
            this.selectedNode = node;
            this.render();
            this.updateNodeList();
        }
    }

    validateGraph() {
        const result = this.graph.validate();
        
        if (result.valid) {
            document.getElementById('validation-indicator').textContent = 'Valid';
            document.getElementById('validation-indicator').classList.add('valid');
            document.getElementById('validation-indicator').classList.remove('invalid');
            this.log('success', 'Graph validation passed');
        } else {
            document.getElementById('validation-indicator').textContent = 'Invalid';
            document.getElementById('validation-indicator').classList.add('invalid');
            document.getElementById('validation-indicator').classList.remove('valid');
            result.errors.forEach(err => this.log('error', err));
        }
        
        this.saveAndRender();
    }

    createSnapshot() {
        const freezeResult = this.graph.freeze();
        
        if (freezeResult.success) {
            const snapshot = Storage.saveSnapshot(this.graph.toJSON());
            this.log('success', `Snapshot created: ${snapshot.timestamp}`);
            this.saveAndRender();
        } else {
            this.log('error', freezeResult.error);
        }
    }

    filterNodes(query) {
        const items = document.querySelectorAll('.node-list-item');
        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            if (text.includes(query.toLowerCase())) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }

    render() {
        this.renderCanvas();
        this.updateNodeList();
    }

    renderCanvas() {
        const nodesLayer = document.getElementById('nodes-layer');
        const edgesLayer = document.getElementById('edges-layer');
        
        nodesLayer.innerHTML = '';
        edgesLayer.innerHTML = '';

        // Render edges
        this.graph.edges.forEach(edge => {
            const source = this.graph.getNode(edge.source);
            const target = this.graph.getNode(edge.target);
            if (source && target) {
                const line = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                const sx = source.x + this.panOffset.x + 75;
                const sy = source.y + this.panOffset.y + 20;
                const tx = target.x + this.panOffset.x + 75;
                const ty = target.y + this.panOffset.y + 20;
                line.setAttribute('d', `M ${sx} ${sy} L ${tx} ${ty}`);
                line.classList.add('edge');
                edgesLayer.appendChild(line);
            }
        });

        // Render real nodes
        this.graph.nodes.forEach(node => {
            this.renderNode(node, nodesLayer, false);
        });

        // Render ghost node if exists
        if (this.ghostNode) {
            this.renderNode(this.ghostNode, nodesLayer, true);
        }
    }

    renderNode(node, container, isGhost) {
        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        g.classList.add('canvas-node');
        
        if (isGhost) {
            g.classList.add('ghost');
        }
        
        if (!isGhost && this.selectedNode && this.selectedNode.id === node.id) {
            g.classList.add('selected');
        }

        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('x', node.x + this.panOffset.x);
        rect.setAttribute('y', node.y + this.panOffset.y);
        rect.setAttribute('width', '150');
        rect.setAttribute('height', '40');
        rect.classList.add('node-rect');

        const title = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        title.setAttribute('x', node.x + this.panOffset.x + 10);
        title.setAttribute('y', node.y + this.panOffset.y + 18);
        title.classList.add('node-title');
        title.textContent = node.template;

        const hash = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        hash.setAttribute('x', node.x + this.panOffset.x + 10);
        hash.setAttribute('y', node.y + this.panOffset.y + 32);
        hash.classList.add('node-hash');
        hash.textContent = isGhost ? 'preview...' : (node.hash.substring(0, 12) + '...');

        const dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        dot.setAttribute('cx', node.x + this.panOffset.x + 140);
        dot.setAttribute('cy', node.y + this.panOffset.y + 10);
        dot.classList.add('node-state-dot', node.state);

        g.appendChild(rect);
        g.appendChild(title);
        g.appendChild(hash);
        g.appendChild(dot);

        // Only add interactions for real nodes
        if (!isGhost) {
            g.addEventListener('click', (e) => this.handleNodeClick(node, e));
            g.addEventListener('mousedown', (e) => {
                if (this.mode === 'navigate') {
                    this.draggedNode = node;
                    this.nodeDragStart = { x: e.clientX - node.x, y: e.clientY - node.y };
                }
            });
        }

        container.appendChild(g);

        // Node dragging (only setup once on canvas)
        if (!isGhost && !this.dragListenersSetup) {
            const canvas = document.getElementById('canvas');
            canvas.addEventListener('mousemove', (e) => {
                if (this.draggedNode && this.mode === 'navigate') {
                    const newX = e.clientX - this.nodeDragStart.x;
                    const newY = e.clientY - this.nodeDragStart.y;
                    this.graph.updateNodePosition(this.draggedNode.id, newX, newY);
                    this.render();
                }
            });

            canvas.addEventListener('mouseup', () => {
                if (this.draggedNode) {
                    this.saveAndRender();
                    this.draggedNode = null;
                }
            });
            
            this.dragListenersSetup = true;
        }
    }

    updateNodeList() {
        const nodeList = document.getElementById('node-list');
        nodeList.innerHTML = '';

        this.graph.nodes.forEach(node => {
            const item = document.createElement('div');
            item.classList.add('node-list-item', node.state);
            if (this.selectedNode && this.selectedNode.id === node.id) {
                item.classList.add('selected');
            }

            const title = document.createElement('div');
            title.classList.add('node-list-item-title');
            title.textContent = node.template;

            const hash = document.createElement('div');
            hash.classList.add('node-list-item-hash');
            hash.textContent = node.hash.substring(0, 16) + '...';

            item.appendChild(title);
            item.appendChild(hash);

            item.addEventListener('click', () => {
                this.selectedNode = node;
                this.render();
            });

            item.addEventListener('dblclick', () => {
                this.showInspector(node);
            });

            nodeList.appendChild(item);
        });
    }

    log(type, message) {
        const logEl = document.getElementById('event-log');
        const entry = document.createElement('div');
        entry.classList.add('log-entry', type);

        const timestamp = document.createElement('span');
        timestamp.classList.add('log-timestamp');
        timestamp.textContent = new Date().toLocaleTimeString();

        const msg = document.createElement('span');
        msg.classList.add('log-message');
        msg.textContent = message;

        entry.appendChild(timestamp);
        entry.appendChild(msg);
        logEl.appendChild(entry);
        logEl.scrollTop = logEl.scrollHeight;
    }

    clearLog() {
        document.getElementById('event-log').innerHTML = '';
        this.log('info', 'Event log cleared');
    }

    saveAndRender() {
        Storage.saveGraph(this.graph.toJSON());
        this.render();
    }

    setupImportListeners() {
        const fileInput = document.getElementById('card-file-input');
        const importBtn = document.getElementById('import-card-btn');
        const modal = document.getElementById('import-modal');
        let parsedCard = null;

        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (event) => {
                const text = event.target.result;
                parsedCard = this.parseCardFile(text);

                if (parsedCard) {
                    // Show preview
                    document.getElementById('card-preview').innerHTML = `
                        <p><strong>ID:</strong> ${parsedCard.id}</p>
                        <p><strong>Name:</strong> ${parsedCard.name}</p>
                        <p><strong>Seed:</strong> ${parsedCard.seed.substring(0, 32)}...</p>
                    `;
                    importBtn.disabled = false;
                    this.log('info', `Card parsed: ${parsedCard.name}`);
                } else {
                    document.getElementById('card-preview').innerHTML = '<p style="color: var(--color-error)">Failed to parse card file</p>';
                    importBtn.disabled = true;
                    this.log('error', 'Card parsing failed');
                }
            };
            reader.readAsText(file);
        });

        importBtn.addEventListener('click', () => {
            if (parsedCard && this.contextMenuPos) {
                const node = this.graph.createNodeFromCard(parsedCard, this.contextMenuPos.x, this.contextMenuPos.y);
                this.log('success', `Imported card: ${parsedCard.name}`);
                this.saveAndRender();
                modal.classList.add('hidden');
                fileInput.value = '';
                parsedCard = null;
                importBtn.disabled = true;
                document.getElementById('card-preview').innerHTML = '';
            }
        });
    }

    showImportModal() {
        document.getElementById('import-modal').classList.remove('hidden');
    }

    parseCardFile(text) {
        try {
            // Extract YAML front matter
            const yamlMatch = text.match(/^---\s*\n([\s\S]*?)\n---/);
            if (!yamlMatch) {
                console.error('No YAML front matter found');
                return null;
            }

            const yamlText = yamlMatch[1];
            const bodyText = text.substring(yamlMatch[0].length).trim();

            // Parse YAML manually (simple parsing)
            const lines = yamlText.split('\n');
            const data = { seed_identity: {}, card: {} };
            let currentSection = null;
            let indent = 0;

            for (const line of lines) {
                const trimmed = line.trim();
                if (!trimmed || trimmed.startsWith('#')) continue;

                const currentIndent = line.search(/\S/);

                if (trimmed === 'seed_identity:') {
                    currentSection = 'seed_identity';
                    indent = currentIndent;
                } else if (trimmed === 'card:') {
                    currentSection = 'card';
                    indent = currentIndent;
                } else if (currentSection && currentIndent > indent) {
                    const colonIdx = trimmed.indexOf(':');
                    if (colonIdx > -1) {
                        const key = trimmed.substring(0, colonIdx).trim();
                        let value = trimmed.substring(colonIdx + 1).trim();
                        // Remove quotes
                        value = value.replace(/^['"]|['"]$/g, '');
                        data[currentSection][key] = value;
                    }
                }
            }

            // Build card data
            const cardData = {
                id: data.seed_identity.artifact_id || data.card.id,
                name: data.card.name || 'Imported Card',
                seed: data.seed_identity.seed || 'unknown',
                version: data.card.version || '0.0.0',
                namespace: data.card.namespace || 'unknown',
                deck_mode: data.card.deck_mode || 'unknown',
                body: bodyText
            };

            return cardData;
        } catch (error) {
            console.error('Error parsing card:', error);
            return null;
        }
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    new CanvasController();
});
