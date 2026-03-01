# νόησις — Conversation Structuring System & Research Platform

Author: Timothy Wesley Stone  
License: Open / Shareable

A portable research platform combining:
- **Product**: νóησις Lab — A React/Vite application for AI-driven research
- **Research System**: Card-based markdown decks for structuring thinking and decisions
- **Tools**: Graph visualization and cryptographic seeding systems

---

## Repository Organization

This repository follows a professional organization scheme:

```
noesis-workspace/
├── apps/
│   └── noesis-lab/               # Main React/Vite application
│       ├── frontend/             # Vite React app
│       ├── netlify/functions/    # Serverless backend
│       └── netlify.toml          # App-specific config
│
├── research/                      # Intellectual property & tools
│   ├── decks/                    # νóησις card systems
│   │   ├── engineering/
│   │   ├── exploration/
│   │   └── templates/
│   └── tools/                    # Graph visualization, seeding, etc.
│
├── docs/                          # Project documentation
│   ├── foundation/               # Core philosophy & governance
│   ├── guides/                   # How-to & tutorials
│   ├── api/                      # API documentation
│   └── project/                  # History & decisions
│
├── archive/                       # Legacy & experiments
│   ├── legacy/
│   ├── experiments/
│   ├── assets/
│   └── do-not-use/
│
├── packages/                      # Shared libraries (future)
└── infrastructure/                # DevOps & deployment (future)
```

---

## What This Is

νóησις provides three complementary deck systems for structuring thinking and decisions:

### **Exploration Mode**
- **[Conversation Grounding Deck (v1.0)](research/decks/exploration/conversation-grounding-v1/)** — Everyday AI conversation management (13 cards)

### **Engineering Mode**
- **[νóησις Emergence Deck (v0.1)](research/decks/engineering/emergence-v0.1/)** — Exploration, ideation, structural discovery (14 cards)
- **[νóησις Canonical Deck (v1.0)](research/decks/engineering/canonical-v1.0/)** — Authoritative specification, long-term preservation (12 cards)

Each card is:
- ✅ A complete, portable markdown artifact
- ✅ Cryptographically seeded (tamper-evident identity)
- ✅ Graph-connected (shows relationships)
- ✅ Copy/paste friendly (no special tools required)

---

## Quick Start

### Working on the Web Application

The main application is located in `apps/noesis-lab/`:

```bash
cd apps/noesis-lab
npm install         # Install dependencies
npm run dev         # Start Vite dev server (http://localhost:5173)
npm run build       # Build for production (output to frontend/dist)
```

**Deployment**: Netlify automatically rebuilds from the `main` branch using `netlify.toml` at the repo root.

### Working with Research Decks

Browse the three deck systems:
- **Exploration**: `research/decks/exploration/conversation-grounding-v1/`
- **Emergence**: `research/decks/engineering/emergence-v0.1/`
- **Canonical**: `research/decks/engineering/canonical-v1.0/`

### Using Tools

Graph visualization and card seeding tools are located in `research/tools/`:

```bash
cd research/tools
python view-graph.py .              # Visualize card relationships
python seed-generator.py verify …   # Verify card integrity
```

See [research/tools/](research/tools/) and [docs/guides/](docs/guides/) for details.

---

## Documentation

See [docs/foundation/WHICH_DECK.md](research/decks/) for guidance on choosing card systems and working with the platform.
│   ├── foundation/                 # Core specifications
│   │   ├── POLICY.md              # Constitutional rules
│   │   ├── SEED_SPEC.md           # Seeding system
│   │   └── WHICH_DECK.md          # Deck selection guide
│   ├── guides/                     # How-to guides
│   └── project/                    # Project history
│
├── archive/                        # Legacy versions
└── README.md                       # This file

## Repository Structure

```
/
├── POLICY.md              # Canonical governance rules
├── CHANGELOG.md           # Version history
├── WHICH_DECK.md          # Deck selection guide
├── PROJECT_STRUCTURE.md   # Detailed organization
├── noesis-release/         # Main release package
│   ├── deck/              # Complete decks with examples
│   Three Deck Modes
- **Exploration** = Everyday conversation management (no order, suggestions only)
- **Emergence** = System design exploration (diagnostic gates, ordered flow)
- **Canonical** = Authoritative specifications (strict gates, binding rules)

### Cryptographic Seeds (Tamper-Evident Identity)
Each card has a **seed** (SHA-256 hash) that proves its identity:
- **Spine** (seeded): Identity fields that define what the card *is*
- **Body** (unseeded): Explanations, examples that evolve freely
- Change the spine → seed breaks → must generate new seed
- Change the body → seed stays valid → no reseeding needed

### Graph Metadata (Relationships)
Cards declare relationships:
- **Engineering Mode**: `upstream`, `downstream`, `feeds_into` (dependencies)
- **Exploration Mode**: `often_paired_with`, `helpful_for` (suggestions)

### Gates Enforce Quality
- **Exploration**: No gates (pick what you need)
- **Emergence**: Diagnostic gates (warn but allow)
- **Canonical**: Strict gates (block downstream work)
- LLM context loss
- Model switching
- Team collaboration
- Long time spans

### Decks Are Cognitive Instruments
- **Emergence** = Thinking instrument for exploration
- *Tools

### Seed Generator
```bash
python tools/seed-generator.py generate <card-file>
python tools/seed-generator.py verify <card-file>
python tools/seed-generator.py batch-generate <directory>
```

### Graph Viewer
```bash
python tools/view-graph.py .
```

Shows:
- All 39 cards across 3 decks
- Dependencies and relationships
- Seed verification status
- Mode-aware enforcement

See [docs/guides/GRAPH_VIEWER_README.md](docs/guides/GRAPH_VIEWER_README.md) for details.

---

## Governance

This project follows explicit constitutional rules:
  
Identity precedes trust.

Conversations stay coherent through explicit structure.  
Ideas are born in Emergence, mature into Canonical.  
Cards persist. Decisions endure. Intent survives.

**Constitution vs Commentary**: Seeds separate immutable meaning (spine) from mutable expression (body).

---

## Documentation

### Foundation
- [docs/foundation/POLICY.md](docs/foundation/POLICY.md) — Constitutional governance rules
- [docs/foundation/SEED_SPEC.md](docs/foundation/SEED_SPEC.md) — Cryptographic seeding system
- [docs/foundation/WHICH_DECK.md](docs/foundation/WHICH_DECK.md) — Deck selection guide

### Guides
- [docs/guides/GRAPH_VIEWER_README.md](docs/guides/GRAPH_VIEWER_README.md) — Graph visualization tool

### Project
- [docs/project/CHANGELOG.md](docs/project/CHANGELOG.md) — Version history
- [docs/project/GRAPH_IMPLEMENTATION_COMPLETE.md](docs/project/GRAPH_IMPLEMENTATION_COMPLETE.md) — Graph system overview
- [.github/copilot-instructions.md](.github/copilot-instructions.md) — AI agent guide

---

## Stats

- **39 cards** across 3 decks (13 Exploration + 14 Emergence + 12 Canonical)
- **100% seeded** (tamper-evident identity on all cards)
- **Graph-connected** (relationships mapped and validated)
- **0 dependencies** (pure markdown, copy/paste works everywhere)
- **Promotion**: Emergence → Canonical requires explicit human approval
- **Gates**: Same rules, different enforcement (diagnostic vs binding)
- **Templates**: Deck-agnostic with mode-specific usage

See [POLICY.md](POLICY.md) for canonical governance.

---

## Philosophy

Structure precedes automation.  
Thinking is treated as engineering.

Ideas are born in Emergence, mature into Canonical.  
Cards persist. Decisions endure. Intent survives.

---

## Documentation

- [POLICY.md](POLICY.md) — Governance and rules
- [WHICH_DECK.md](WHICH_DECK.md) — Deck selection guide
- [CHANGELOG.md](CHANGELOG.md) — Version history
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) — Detailed organization
- [.github/copilot-instructions.md](.github/copilot-instructions.md) — AI agent guide

---

## License

**Copyright © 2026 Timothy Wesley Stone. All Rights Reserved.**

The νόησις™ name, system, methodology, and overall framework are proprietary intellectual property.

### Card Sharing License

Individual artifact cards may be:
- ✓ Used for personal projects and AI conversations
- ✓ Shared with others with attribution
- ✓ Modified for your own use
- ✓ Referenced in derivative works

Cards may NOT be:
- ✗ Reproduced in bulk for commercial distribution
- ✗ Included in competing card/template systems
- ✗ Stripped of authorship/copyright notices
- ✗ Sold as standalone products

**Attribution Required**: "Card from νόησις by Timothy Wesley Stone (noesis-lab.com)"

Like collectible trading cards: once you have a card, you can use/share it, but you can't manufacture and sell copies. The system itself remains proprietary IP.

See [LICENSE](LICENSE) for complete terms.

