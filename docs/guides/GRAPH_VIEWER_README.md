# νόησις Graph Viewer

Simple Python tool to visualize card relationships across all νόησις deck modes.

## What It Does

- Scans all card markdown files for graph metadata
- Shows deck summaries (card counts, modes)
- Displays detailed card relationships (upstream, downstream, feeds_into)
- Visualizes dependency trees
- Validates graph integrity
- Exports Graphviz DOT format

## Usage

```bash
python view-graph.py "c:\path\to\workspace"
```

Or just run from the workspace root:
```bash
python view-graph.py .
```

## Output Sections

### 1. Deck Summary
Quick overview of all decks found:
- Namespace
- Mode (ENGINEERING vs EXPLORATION)
- Card count

### 2. Card Details
For each card:
- Position in deck
- Upstream dependencies (requires)
- Downstream cards (enables)
- Feeds_into relationships
- Gate enforcement (strict blocks, diagnostic warns)
- Exploration mode: suggested pairings

### 3. Dependency Tree
ASCII tree showing:
- `^ requires` - upstream dependencies
- `v enables` - downstream cards
- `[STRICT]` - blocks downstream on error
- `[DIAG]` - warns but allows progression

### 4. Validation
Checks for:
- Broken references (upstream/downstream not found)
- Missing positions (ENGINEERING mode)
- Reports errors and warnings

### 5. DOT Export
Generates `noesis-graph.dot` for visualization:
```bash
dot -Tpng noesis-graph.dot -o noesis-graph.png
```

## Graph Metadata

The viewer reads YAML front matter from card markdown files:

```yaml
---
card:
  id: CARD-XX
  name: Card Name
  namespace: noesis.deck.version
  mode: ENGINEERING | EXPLORATION
  deck_mode: Emergence | Canonical

dependencies:
  upstream: [CARD-YY]      # Required before this
  downstream: [CARD-ZZ]    # Enabled by this
  feeds_into: [CARD-AA]    # Data flows to

gate:
  enforcement: strict | diagnostic
  blocks_downstream: true | false

ordering:
  position: N
  required_after: [CARD-YY]
  required_before: [CARD-ZZ]
---
```

## Deck Modes

### ENGINEERING MODE
- **Emergence Deck (v0.1)**: 14 cards, diagnostic gates (warns)
- **Canonical Deck (v1.0)**: 12 cards, strict gates (blocks)
- Ordered cards with explicit dependencies
- Gate enforcement based on deck type

### EXPLORATION MODE
- **Conversation Grounding Deck**: 13 cards, no gates
- Independent cards, no required order
- Uses `suggested_patterns` instead of dependencies
- `often_paired_with` and `helpful_for` hints

## Requirements

- Python 3.7+
- PyYAML: `pip install pyyaml`
- Optional: Graphviz for DOT visualization

## Examples

### Check all decks
```bash
python view-graph.py .
```

### Export and visualize graph
```bash
python view-graph.py .
dot -Tpng noesis-graph.dot -o graph.png
```

### Validate only
```bash
python view-graph.py . | grep -A 20 "Validation"
```

## File Structure

Scans these locations:
```
workspace/
  noesis-release/
    deck/
      v0.1/cards/       # Emergence Deck
      v1.0/cards/       # Canonical Deck
  new/
    cards/              # Conversation Grounding (Exploration)
```

## Output Interpretation

**Gate Markers:**
- `[STRICT]` - Error blocks downstream work (Canonical)
- `[DIAG]` - Warning allows progression (Emergence)
- (none) - No gates (Exploration)

**Relationships:**
- `^ requires` - Must complete upstream first
- `v enables` - Unlocks downstream work
- Dashed edges in DOT - Data flows (feeds_into)

**Validation:**
- Errors = broken references, must fix
- Warnings = incomplete metadata, recommended fix
- OK = all checks passed

## License

Open / Shareable (per νόησις foundation)

---

*Structure precedes automation. Thinking is treated as engineering.*
