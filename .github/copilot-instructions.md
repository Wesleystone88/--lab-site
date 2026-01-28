# νόησις Artifact Deck Project — AI Agent Instructions

Author: Timothy Wesley Stone  
Copyright © 2026 Timothy Wesley Stone. All Rights Reserved.

## What This Is
A **portable markdown-based card system** for structuring AI conversations and system specifications. Plus complementary **React+Vite sidebar applications** for interacting with cards via Gemini API.

### Dual Architecture

**Core System** (markdown-based, no build):
1. **Exploration Mode** ([Conversation Grounding Deck](decks/exploration/conversation-grounding-v1/)) — Everyday AI conversation management (13 cards, no order required)
2. **Engineering Mode - Emergence** ([decks/engineering/emergence-v0.1/](decks/engineering/emergence-v0.1/)) — System design exploration (14 ordered cards, diagnostic gates)
3. **Engineering Mode - Canonical** ([decks/engineering/canonical-v1.0/](decks/engineering/canonical-v1.0/)) — Authoritative specifications (12 ordered cards, strict gates)

**Sidebar Applications** (React + Vite + Gemini):
- Located in parallel workspaces: `copy-of-νόησις-chat/`, `noesis-workflow-engine-v0.1/`, `noesis-ram_-cognitive-memory-substrate/`
- Each runs independently with `npm run dev` (Vite dev server on localhost)
- All use Gemini API key for LLM interactions
- Styled with lucide-react icons and react-markdown with math support

**Core principle**: Card system = copy/paste markdown only, no dependencies. Cryptographically seeded for tamper-evident identity. Apps are optional tooling layer.

## Constitutional Rules ([docs/foundation/POLICY.md](docs/foundation/POLICY.md))

### 1. Three Deck Modes
- **Exploration Mode** (Conversation Grounding): No ordering, suggestions only, fluid structure
- **Emergence Deck (v0.x)**: Exploration, ideation, discovery. Partial cards allowed. Gates diagnostic (warn but don't block).
- **Canonical Deck (v1.x)**: Specification, preservation, authority. Complete cards required. Gates binding (block downstream).

### 2. Paired Naming (Engineering Mode only)
Always use: **νόησις Emergence Deck (v0.1)** or **νόησις Canonical Deck (v1.0)**  
Never: "v0.1" or "v1.0" alone in human-facing text.

### 3. Cryptographic Seeding
Every card has a `seed_identity` block with tamper-evident hash of its "spine" (immutable identity fields). See [docs/foundation/SEED_SPEC.md](docs/foundation/SEED_SPEC.md).
- **Spine**: Card ID, name, namespace, dependencies, gates (seeded)
- **Body**: Content, examples, notes (unseeded - can evolve freely)

### 4. Templates
Templates are deck-agnostic ([decks/templates/](decks/templates/)). Usage strictness depends on deck mode.

---

## Sidebar Applications (React + Vite + Gemini)

**Three independent apps** in parallel workspaces, each with identical architecture:

### Development Workflow

**Setup** (same for all three):
```bash
cd copy-of-νόησις-chat/  # or workflow-engine or ram-substrate
npm install
# Set GEMINI_API_KEY in .env.local (required to run)
npm run dev     # Start Vite dev server on http://localhost:5173
npm run build   # Production bundle
npm run preview # Preview built version locally
```

### Key Architecture Patterns

**File Structure** (consistent across all apps):
```
├── index.tsx              # Entry point (React 19)
├── App.tsx                # Root component
├── types.ts               # TypeScript interfaces
├── vite.config.ts         # Vite configuration
├── services/
│   ├── geminiService.ts   # Google Gemini API wrapper
│   └── [app-specific services]
├── components/
│   ├── ChatMessage.tsx    # Common: Render AI/user messages
│   ├── TemplateSelector.tsx # Common: Pick deck cards
│   └── [app-specific components]
└── assets/                # CSS, images
```

**Dependencies** (standard across apps):
- `react` (^19.2+) & `react-dom`
- `@google/genai` (^1.38+) — Gemini API client
- `lucide-react` (^0.56+) — Icon library
- `react-markdown` (^9.0+) with `remark-math` & `rehype-katex` — MD + math rendering
- Vite + TypeScript for dev/build tooling

**Gemini API Integration**:
- All apps wrap `@google/genai` in `geminiService.ts`
- Expects `GEMINI_API_KEY` in `.env.local`
- Pattern: `generateResponse(prompt, systemMessage?)` → Promise<string>
- Math rendering via KaTeX for LaTeX in responses

### App-Specific Purposes

| App | Purpose | Key Component |
|-----|---------|---------------|
| `copy-of-νόησις-chat` | Deck card chat interface | `TemplateSelector.tsx` loads CARD files |
| `noesis-workflow-engine-v0.1` | Workflow orchestration | Canvas-based card flow visualization |
| `noesis-ram_-cognitive-memory-substrate` | Memory/context persistence | `MemoryExplorer.tsx` for session state |

---

## Quick Reference

### Starting a New Deck

**Exploration Mode** (conversation management):
1. Browse [cards](decks/exploration/conversation-grounding-v1/cards/)
2. Copy CARD-01 (Alignment Anchor) into your AI chat
3. Fill in your current conversation goal
4. Add other cards as needed (no required order)

**Emergence Deck** (exploring ideas):
1. Copy [PACKAGE_TEMPLATE.md](decks/templates/PACKAGE_TEMPLATE.md) → fill project class
2. Copy [01_CARD-01_WRITE_UP_Raw_Narrative_Intake.md](decks/engineering/emergence-v0.1/cards/01_CARD-01_WRITE_UP_Raw_Narrative_Intake.md) → paste project narrative
3. Continue sequentially through cards (14 total: CARD-00 to CARD-13)
4. Gates warn but don't block

**Canonical Deck** (defining systems):
1. Copy [PACKAGE_TEMPLATE.md](decks/templates/PACKAGE_TEMPLATE.md) → declare project envelope
2. Copy [01_CARD-1_WRITE_UP_Narrative_Anchor.md](decks/engineering/canonical-v1.0/cards/01_CARD-1_WRITE_UP_Narrative_Anchor.md) → formalize intent
3. Progress through 12 cards (CARD-0 to CARD-11)
4. Gates block downstream work if violated

### Helping Fill an Existing Card
1. Read `DeckMode` field to understand enforcement context
2. Check `UpstreamCards` — read those first for context
3. Use templates in [decks/templates/](decks/templates/) as guidance
4. Fill CONTENT section with concrete, measurable content
5. **No placeholders**: "TBD", "TODO", "see later" = violations

### Validating a Card
Check `Gate` section:
- **ERROR**: Blocks downstream work (Canonical), signals risk (Emergence)
- **WARNING**: Advisory only (v0.1 specific)
- **INFO**: Guidance (v0.1 specific)

### Working with Python Tools
**Required**: Python 3.7+, `pyyaml` (installed via `pip install pyyaml`)

**Common Operations**:
```bash
# Add/verify cryptographic seeds on all cards
cd noesis-workspace
python tools/seed-generator.py add decks/engineering/emergence-v0.1/cards/
python tools/seed-generator.py verify decks/engineering/emergence-v0.1/cards/

# View card relationships and dependency graph
python tools/view-graph.py .

# Check individual card
python tools/seed-generator.py verify decks/engineering/emergence-v0.1/cards/00_CARD-00_DECK_SCHEMA_Meta_Card.md
```

**When seeding is important**: Any time you edit card YAML front matter (dependencies, gates, ordering), re-run verification to detect tampering.

---

## Repository Structure

```
noesis-workspace/
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
```

---

## Deck Selection Guide

See [WHICH_DECK.md](docs/foundation/WHICH_DECK.md) for full guidance.

**Use Exploration Mode (Conversation Grounding) when:**
- Managing AI conversations that span multiple sessions
- Preventing decisions from being re-litigated
- Tracking open questions and assumptions
- No specific ordering needed — pick cards that help

**Use Emergence Deck (v0.1) when:**
- Exploring ideas, prototyping systems
- Requirements are still fluid
- Thinking out loud with an LLM
- Expecting contradictions and revisions
- Want fast momentum without over-constraint

**Use Canonical Deck (v1.0) when:**
- Defining real systems ready for implementation
- Sharing specifications with collaborators
- Ambiguity must be eliminated
- Preserving intent across long time spans
- Safety, dependencies, and failure modes matter

**Anti-pattern**: Don't skip Emergence and go straight to Canonical for new ideas — premature canonization kills exploration.

---

## Three Deck Modes

### Exploration Mode (Conversation Grounding)
- **13 cards**: CARD-01 to CARD-13 (no CARD-00)
- **Purpose**: AI conversation management, session continuity
- **Ordering**: None required — use cards as needed
- **Gates**: None (pure suggestions)
- **Location**: [decks/exploration/conversation-grounding-v1/](decks/exploration/conversation-grounding-v1/)

Key cards:
- CARD-01 (Alignment Anchor) — Current conversation goal
- CARD-07 (Open Questions) — Track unresolved items
- CARD-09 (Decisions) — Record choices made
- CARD-11 (Context Handoff) — Resume sessions

### Engineering Mode - Emergence

## Deck Differences

| Dimension | Emergence Deck (v0.1) | Canonical Deck (v1.0) |
|-----------|----------------------|----------------------|
| **Card count** | 14 (CARD-00 to CARD-13) | 12 (CARD-0 to CARD-11) |
| **Purpose** | Exploration, discovery | Specification, preservation |
| **Completeness** | Partial cards allowed | Complete cards required |
| **Gates** | Diagnostic (warn) | Binding (block) |
| **Ambiguity** | Tolerated temporarily | Must be resolved |
| **Stability** | Experimental | Backward compatible |
| **Breaking changes** | Acceptable | Require migration notes |

---

## Cryptographic Seeding System

All cards have YAML front matter with `seed_identity` blocks (see [SEED_SPEC.md](docs/foundation/SEED_SPEC.md)):

```yaml
seed_identity:
  artifact_id: CARD-01              # Human-readable stable ID
  seed_algo: sha256-v1              # Hash algorithm + version
  seed: abc123...                   # SHA-256 hash (64 hex chars)
  seed_scope: spine-v1              # Which spine definition was used
  seeded_at: 2026-01-21T12:34:56Z   # ISO 8601 timestamp
  status: locked                    # draft | locked | deprecated
```

**Spine vs Body**:
- **Spine** (seeded): Card ID, name, namespace, dependencies, gates — immutable identity
- **Body** (unseeded): Content, examples, notes — can evolve freely

**Tool**: [tools/seed-generator.py](tools/seed-generator.py) — Add/verify seeds, detect tampering

---

## Python Tools

### seed-generator.py
Generates and verifies cryptographic seeds for card identity.

**Usage**:
```bash
# Add seeds to all cards in a directory
python tools/seed-generator.py add decks/engineering/emergence-v0.1/cards/

# Verify existing seeds
python tools/seed-generator.py verify decks/engineering/emergence-v0.1/cards/

# Check single card
python tools/seed-generator.py verify decks/engineering/emergence-v0.1/cards/00_CARD-00_DECK_SCHEMA_Meta_Card.md
```

**What it does**:
- Extracts spine fields from YAML front matter based on mode (ENGINEERING vs EXPLORATION)
- Canonicalizes spine to sorted JSON (deterministic format)
- Computes SHA-256 hash of canonical spine
- Adds/updates `seed_identity` block in YAML front matter
- Detects tampering by recomputing and comparing seeds

**Spine fields** (seeded, immutable):
- ENGINEERING: `card.id`, `card.name`, `card.namespace`, `card.mode`, `card.deck_mode`, `dependencies`, `gate`, `ordering`
- EXPLORATION: `card.id`, `card.name`, `card.namespace`, `card.mode`, `suggested_patterns`, `state_schema`

**Body fields** (unseeded, can evolve): All content below YAML front matter, plus human-readable headers like `DeckName`, `Status`, `Owner`

### view-graph.py
Visualizes card relationships and dependency trees.

**Usage**:
```bash
# View all deck relationships from workspace root
python tools/view-graph.py .

# Specify workspace path
python tools/view-graph.py "c:\path\to\noesis-workspace"
```

**Output**:
1. **Deck Summary**: Card counts per deck mode
2. **Card Details**: Each card's upstream/downstream dependencies, gate enforcement
3. **Dependency Tree**: ASCII tree showing requires/enables relationships
4. **Validation**: Checks for missing dependencies, circular references

**Exports**: Generates `noesis-graph.dot` (Graphviz format) for visual diagrams

---

## Real YAML Front Matter Examples

### Engineering Mode Card (Emergence Deck)
```yaml
---
seed_identity:
  artifact_id: CARD-00
  seed_algo: sha256-v1
  seed: 5937c764fd45b0e696068945a2a56a9b39f2d205e6f428d1f80478ad788ad17d
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:42:03Z'
  status: locked
card:
  id: CARD-00
  name: Deck Schema (Meta-Card)
  namespace: noesis.emergence.v0.1
  version: 0.1.0
  mode: ENGINEERING
  deck_mode: Emergence
dependencies:
  upstream: []
  downstream:
  - CARD-01
  - CARD-02
  required_by:
  - CARD-01
gate:
  enforcement: strict
  blocks_downstream: true
ordering:
  position: 0
  required_before:
  - CARD-01
---
```

### Exploration Mode Card (Conversation Grounding)
```yaml
---
seed_identity:
  artifact_id: CARD-01
  seed_algo: sha256-v1
  seed: 466fa5b1d8e5b4c92bd47b67c9d6006c7ae7dc43f354127c219afc9fff4d9f36
  seed_scope: spine-v1
  seeded_at: '2026-01-21T05:41:16Z'
  status: locked
card:
  id: CARD-01
  name: Alignment Anchor
  namespace: noesis.conversation-grounding.exploration
  version: 1.0
  mode: EXPLORATION
suggested_patterns:
  often_paired_with:
  - CARD-02
  - CARD-03
  helpful_for:
  - starting_conversations
  - refocusing_drift
  - long_discussions
state_schema:
  alignment_statement: string
  collaboration_mode: string
  worth_it_if: string
---
```

**Key Differences**:
- Engineering cards have `dependencies`, `gate`, `ordering` (strict flow)
- Exploration cards have `suggested_patterns`, `state_schema` (flexible pairing)
- Both have `seed_identity` (tamper-evident) but different spine compositions

---

## Card Structure

### Emergence Deck (v0.1) Cards
```
DeckName: νόησις Emergence Deck
DeckMode: Emergence Deck (v0.1)
CardID: CARD-XX
CardName: Name
Version: 0.1
Status: draft | locked
Owner: Timothy Wesley Stone
UpstreamCards: [CARD-YY]
DownstreamCards: [CARD-ZZ]

Purpose:
Inputs:
Outputs:
Content:
Gate:
```

### Canonical Deck (v1.0) Cards
```
DeckName: νόησις Canonical Deck
DeckMode: Canonical Deck (v1.0)

Purpose:
Contains:
Outputs:
Gate:
```

---

## Gate Enforcement

### Emergence Deck
Gates are **diagnostic**:
- Errors signal design risk but don't block progress
- Violations allowed temporarily during exploration
- Contradictions tolerated while learning
- Incomplete cards acceptable

Example gates:
```
ERROR if empty
ERROR if fewer than 3 examples
```

### Canonical Deck
Gates are **binding**:
- Errors block downstream cards and releases
- Violations must be resolved before progression
- Contradictions must be resolved or documented
- Complete cards required

Example gates:
```
Must exist before CARD-2
Must be internally consistent
Constraints must be respected by downstream cards
Unmitigated critical risks prohibited
```

---

## Card Dependencies

### Emergence Deck (v0.1) Ordering
```
CARD-00 (DECK SCHEMA) → CARD-01 (WRITE-UP) → CARD-02 (INTENT) →
CARD-03 (CONSTRAINTS) → CARD-04 (ARCHITECTURE) → CARD-05 (INTERFACE) →
CARD-06 (DATA) → CARD-07 (DEPENDENCY) → CARD-08 (SAFETY) →
CARD-09 (TOPOLOGY) → CARD-10 (TESTING) → CARD-11 (DEPLOYMENT) →
CARD-12 (STYLE) → CARD-13 (IMPLEMENTATION)
```

Enforced via `UpstreamCards`/`DownstreamCards` fields.

### Canonical Deck (v1.0) Ordering
```
CARD-0 (PACKAGE) → CARD-1 (WRITE-UP) → CARD-2 (INTENT) →
CARD-3 (CONSTRAINTS) → CARD-4 (STRUCTURE) → CARD-5 (FILE_ASSET_TREE) →
CARD-6 (INTERFACES) → CARD-7 (DEPENDENCIES) → CARD-8 (SAFETY_SECURITY) →
CARD-9 (FAILURE_RECOVERY) → CARD-10 (EVOLUTION_SCALING) → CARD-11 (EXECUTION)
```

CARD-0 (PACKAGE) gates everything downstream.

---

## Content Quality Rules

From [decks/templates/](decks/templates/):

### ✅ Concrete Content (Correct)
```
Objectives:
O1. Preserve intent across LLM sessions.
O2. Make structure explicit and shareable.

Success Criteria:
SC1. Deck usable purely as Markdown templates.
SC2. Users can resume work by pasting cards.

Threats: - Hallucinated structure
Mitigations: - Versioning, human review

Budget: $0 (volunteer project)
Time: 3 months to v1.0
```

### ❌ Vague Content (Violations)
```
System should be fast and scalable
Auth will be added later (TBD)
Performance TBD based on requirements
TODO: define constraints
See implementation for details
```

### Key Patterns
- **Numbered references**: O1, SC1, I1, T1 for traceability
- **Explicit tradeoffs**: Document what was chosen and why
- **Named threats + mitigations**: Paired, specific, actionable
- **Measurable criteria**: Quantifiable where possible
- **Operational language**: Implementation-ready, not aspirational

---

## Promotion Workflow (Emergence → Canonical)

When content stabilizes in Emergence Deck, it may be promoted to Canonical:

### Checklist
1. ✓ Intent has not materially changed for several iterations
2. ✓ All gates pass without unresolved ERRORs
3. ✓ Tradeoffs and constraints explicitly documented
4. ✓ A third party could implement without oral explanation
5. ✓ Human owner declares readiness

### Process
1. Copy Emergence deck into Canonical directory
2. Update `DeckMode` headers in all cards
3. Re-validate gates with strict (binding) enforcement
4. Resolve any newly surfaced violations
5. Record promotion in [CHANGELOG.md](docs/project/CHANGELOG.md)

**Promotion is irreversible for that version line.**

---

## File Naming Conventions

- Master decks: `noesis-emergence-deck-v0.1.md`, `noesis-canonical-deck-v1.0.md`
- Emergence cards: `{number}_CARD-{id}_{NAME}_{description}.md`
  - Example: [01_CARD-01_WRITE_UP_Raw_Narrative_Intake.md](decks/engineering/emergence-v0.1/cards/01_CARD-01_WRITE_UP_Raw_Narrative_Intake.md)
- Canonical cards: `{number}_CARD-{id}_{NAME}_{description}.md`
  - Example: [01_CARD-1_WRITE_UP_Narrative_Anchor.md](decks/engineering/canonical-v1.0/cards/01_CARD-1_WRITE_UP_Narrative_Anchor.md)

---

## Common Operations

### Creating a New Project Deck
1. Choose deck mode (Emergence for exploration, Canonical for specification)
2. Start with PACKAGE declaration (gates all downstream cards)
3. Progress sequentially respecting dependencies
4. Respect gate enforcement based on deck mode

### Modifying Existing Cards
1. Check `DeckMode` to understand enforcement context
2. Verify `UpstreamCards` are still valid
3. Respect Gate rules (diagnostic vs binding)
4. Update `Version` field on breaking changes
5. Update `DeckMode` if moving between decks

### Understanding Card Status
- `draft`: Work in progress, may change
- `locked`: Stable, referenced by downstream cards

---

## Anti-Patterns to Avoid

❌ **Skip PACKAGE declaration**: Gates everything else  
❌ **Violate card ordering**: Breaks dependency chain  
❌ **Use placeholder language**: "TBD", "TODO", "see later"  
❌ **Treat as documentation**: This is specification framework  
❌ **Add tooling dependencies**: Maintain pure markdown portability  
❌ **Skip Emergence phase**: Premature canonization kills exploration  
❌ **Invent constraints**: Only reference what's in upstream cards  
❌ **Mix deck modes**: Don't treat Emergence cards as Canonical  

---

## Stability Contracts

### Emergence Deck (v0.x)
- Backward compatibility **NOT guaranteed**
- Card structure may evolve
- Semantics may shift
- Breaking changes acceptable
- v0.2, v0.3, etc. = experimental refinement

### Canonical Deck (v1.x)
- Backward compatibility **expected**
- Structural changes require migration notes
- Semantics treated as durable
- Breaking changes rare and explicit
- v1.1, v1.2, etc. = additive refinement
- v2.0 only if foundational philosophy changes

---

## Authority and Governance

- **Human maintainers**: Retain final authority
- **LLMs**: May assist but cannot override policy or gates
- **Canonical source**: [POLICY.md](docs/foundation/POLICY.md)
- **Deck selection**: [WHICH_DECK.md](docs/foundation/WHICH_DECK.md)
- **History**: [CHANGELOG.md](docs/project/CHANGELOG.md)

---

## Key Reminders for AI Agents

1. **Always use paired naming** in responses to users
2. **Respect deck mode** — Emergence allows exploration, Canonical requires precision
3. **Check gates before proceeding** — enforcement differs by deck
4. **No placeholders** — concrete operational content only
5. **Promotion is manual** — never auto-promote from Emergence to Canonical
6. **Templates are neutral** — usage strictness depends on deck context
7. **Card identity matters** — DeckName/DeckMode must be updated if cards move

---

## Cross-Workspace Integration Patterns

### Card System → Sidebar Apps
- Deck cards are the **source of truth** for system specifications
- Apps in `copy-of-νόησις-chat/`, `noesis-workflow-engine-v0.1/`, etc. **display and interact with** deck cards
- Use `TemplateSelector.tsx` pattern to load `.md` card files and render them
- Never hardcode deck content into React components — reference card files

### Managing Gemini API Keys Across Apps
- Each app has its own `.env.local` file (gitignored)
- Pattern: `GEMINI_API_KEY=your_key_here`
- All three apps expect identical structure in `geminiService.ts`
- If adding new app: copy `geminiService.ts` from `copy-of-νόησις-chat/` as template

### Development Workflow (Multi-Workspace)
**Sequential startup** (recommended):
```bash
# Terminal 1: Main noesis-workspace for card editing
cd c:\Users\timmy\OneDrive\Desktop\noesis-workspace
# Edit cards, run Python tools, manage structure

# Terminal 2: Sidebar app dev server
cd c:\Users\timmy\Downloads\copy-of-νóησις-chat
npm run dev  # Vite dev server on :5173

# Terminal 3: (optional) Another sidebar app
cd c:\Users\timmy\Downloads\noesis-workflow-engine-v0.1
npm run dev  # Vite dev server on :5174 (auto-incremented)
```

### Common Editing Patterns

**Pattern 1: Edit card, verify seed**
```bash
# Edit a card file (e.g., change dependencies, gate logic)
nano decks/engineering/emergence-v0.1/cards/02_CARD-02_INTENT_Compiled_Meaning.md

# Verify seed hasn't been tampered with
python tools/seed-generator.py verify decks/engineering/emergence-v0.1/cards/02_CARD-02_INTENT_Compiled_Meaning.md
```

**Pattern 2: Update card references in sidebar app**
- Load card markdown from `decks/*/cards/*.md`
- Parse YAML front matter for metadata
- Render body with `react-markdown` + KaTeX
- Don't cache card content — apps should fetch fresh on each session

**Pattern 3: Add new Vite app to workspace**
1. Create new folder: `noesis-new-app/`
2. Copy structure from `copy-of-νóησις-chat/` (package.json, vite.config.ts, index.tsx, etc.)
3. Copy `geminiService.ts` wrapper pattern
4. Update `package.json` name field
5. Create `.env.local` with `GEMINI_API_KEY`
6. Run `npm install && npm run dev`

---

## Troubleshooting Workflows

### Seed Verification Fails
- **Cause**: Card YAML front matter was edited without re-running `seed-generator.py`
- **Fix**: `python tools/seed-generator.py add decks/engineering/emergence-v0.1/cards/{card_file}` to regenerate seed
- **Preventive**: Run verification after any `dependencies`, `gate`, or `ordering` field edits

### Vite App Won't Start
- **Cause 1**: `GEMINI_API_KEY` not set in `.env.local`
- **Fix 1**: Create `.env.local` in app root with `GEMINI_API_KEY=abc123...`
- **Cause 2**: Port 5173 already in use
- **Fix 2**: Kill process on port 5173 or start second app (Vite auto-increments to 5174)

### Card Dependencies Circular
- **Symptom**: `view-graph.py` reports circular reference
- **Fix**: Edit `dependencies.upstream` or `dependencies.downstream` to break cycle
- **Validate**: Run `python tools/view-graph.py .` to confirm

### App Can't Load Card Content
- **Cause 1**: Card file path in code is absolute instead of relative to workspace
- **Cause 2**: Card YAML front matter parsing failed
- **Debug**: Log raw file content and YAML parse errors in `geminiService.ts`

---

## File Organization Conventions

### Naming in Emergence Deck (v0.1)
```
{order:02d}_CARD-{id}_{SECTION}_{description}.md
Example: 02_CARD-02_INTENT_Compiled_Meaning.md
```

### Naming in Canonical Deck (v1.0)
```
{order:02d}_CARD-{id}_{SECTION}_{description}.md
Example: 02_CARD-2_INTENT_System_Intent_Anchor.md
```
Note: Canonical uses CARD-0, CARD-1, etc. (no zero-padding in ID)

### Custom Project Decks
When users create new decks from templates:
- Follow naming convention: `{number}_CARD-{id}_...`
- Update `namespace` field in YAML to avoid collisions
- Increment version in `card.version` field
- Re-run seeding: `python tools/seed-generator.py add {custom_deck_path}`

---

## Project Organization Philosophy

### Product vs Website Separation (Gaming Card Collection Style)

**Domain**: https://noesis-lab.com

**Organizational Principle**: Like collectible card games maintain **clean file structure** between product assets and website presentation, this project separates concerns by directory:

#### Product Assets (Core Card System)
- **Location**: `decks/`, `templates/`, `docs/foundation/`
- **Nature**: Version-controlled markdown cards, templates, specifications
- **Stability**: Cryptographically seeded, immutable spine, strict versioning
- **Source of Truth**: These are the canonical card definitions

#### Website Assets (noesis-lab.com)
- **Location**: `site/` (separate directory from product)
- **Nature**: HTML, CSS, images, presentation layer
- **Stability**: Can change freely without affecting product versioning
- **Purpose**: Display, showcase, and present cards to users

**File Structure Guidance**:
```
noesis-workspace/
├── decks/              # PRODUCT: Core card decks (source of truth)
├── templates/          # PRODUCT: Blank card templates
├── docs/               # PRODUCT: Specifications
├── tools/              # PRODUCT: Utilities
├── site/               # WEBSITE: noesis-lab.com files
│   ├── index.html      #   - Landing page (can display cards)
│   ├── content/        #   - Blog posts, tutorials
│   ├── assets/         #   - Images, CSS, JS
│   └── build/          #   - Generated site (gitignored)
└── archive/            # Legacy versions
```

**Key Principle**: Clean file organization - product files stay in `decks/` with version control and seeding, website files stay in `site/` for presentation. The website can freely display, embed, and showcase cards - the separation is organizational, not access-based.

This mirrors how Magic: The Gathering organizes card database files separately from Gatherer website files, or how Pokémon TCG maintains card data files separate from pokemon.com website code - but both websites display the cards.

---

## Copyright & Intellectual Property

**Copyright © 2026 Timothy Wesley Stone. All Rights Reserved.**

The νόησις™ name, system, methodology, framework, and website are proprietary intellectual property.

### Card Sharing License
Individual artifact cards may be used and shared with attribution, but:
- Cannot be reproduced in bulk for commercial sale
- Cannot be included in competing card/template systems
- Must preserve authorship and copyright notices
- Cannot be sold as standalone products

**Attribution Required**: "Card from νόησις by Timothy Wesley Stone (noesis-lab.com)"

Like collectible trading cards: you can share cards you have, but can't manufacture copies of the system. See [LICENSE](../LICENSE) for complete terms.

---

Structure precedes automation.  
Thinking is treated as engineering.
