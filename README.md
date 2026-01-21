# νόησις — Conversation Structuring System

Author: Timothy Wesley Stone  
License: Open / Shareable

A portable, markdown-based card system that keeps AI conversations coherent across sessions by making decisions, questions, and structure explicit.

---

## What This Is

νόησις (pronounced "noh-ay-sis") provides three complementary deck systems:

### **Exploration Mode**
- **[Conversation Grounding Deck (v1.0)](decks/exploration/conversation-grounding-v1/)** — Everyday AI conversation management (13 cards)

### **Engineering Mode**
- **[νόησις Emergence Deck (v0.1)](decks/engineering/emergence-v0.1/)** — Exploration, ideation, structural discovery (14 cards)
- **[νόησις Canonical Deck (v1.0)](decks/engineering/canonical-v1.0/)** — Authoritative specification, long-term preservation (12 cards)

Each card is:
- ✅ A complete, portable markdown artifact
- ✅ Cryptographically seeded (tamper-evident identity)
- ✅ Graph-connected (shows relationships)
- ✅ Copy/paste friendly (no special tools required)

---

## Quick Start

### Choose Your Mode

**Use Exploration Mode (Conversation Grounding) when:**
- Managing any AI conversation
- Preventing decisions from being re-litigated
- Tracking open questions
- Resuming sessions after context resets

**Use Engineering Mode (Emergence) when:**
- Exploring system design ideas
- Requirements are fluid
- Want fast momentum with light structure
- Building specifications incrementally

**Use Engineering Mode (Canonical) when:**
- Defining production-ready systems
- Sharing formal specifications
- Ambiguity must be eliminated
- Long-term preservation required

See [docs/foundation/WHICH_DECK.md](docs/foundation/WHICH_DECK.md) for detailed guidance.

### Get Started

**For Conversation Management:**
1. Browse [Conversation Grounding cards](decks/exploration/conversation-grounding-v1/cards/)
2. Copy CARD-01 (Alignment Anchor) into your AI chat
3. Fill in your current conversation goal
4. Add other cards as needed (no required order)

νόησις/
├── decks/                          # All card decks
│   ├── exploration/                # Exploration Mode
│   │   └── conversation-grounding-v1/   # 13 cards for AI conversations
│   ├── engineering/                # Engineering Mode
│   │   ├── emergence-v0.1/         # 14 cards for system design
│   │   └── canonical-v1.0/         # 12 cards for specifications
│   └── templates/                  # Blank templates
│
├── tools/                          # Utilities
│   ├── seed-generator.py           # Add/verify cryptographic seeds
│   ├── view-graph.py               # Visualize card relationships
│   └── noesis-graph-viewer.py      # Full graph viewer
│
├── docs/                           # Documentation
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

