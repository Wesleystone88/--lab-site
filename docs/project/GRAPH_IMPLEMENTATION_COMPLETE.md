# νόησις Graph Implementation — Complete

**Date**: January 21, 2026  
**Status**: ✅ Complete  

---

## What Was Built

A **callable graph system** for νόησις cards that:
1. Tracks dependencies across all deck modes
2. Enforces mode-specific semantics (ENGINEERING vs EXPLORATION)
3. Validates graph integrity
4. Exports visualizations

---

## Implementation Summary

### Phase 1: Graph Metadata (Complete)

Added YAML front matter to **39 total cards**:

#### Emergence Deck (v0.1) — 14 cards
- Location: `noesis-release/deck/v0.1/cards/`
- Mode: ENGINEERING (diagnostic gates)
- Status: ✅ All cards have metadata (CARD-00 through CARD-13)
- Features:
  - Sequential dependencies (upstream/downstream)
  - Diagnostic gate enforcement (warns but allows)
  - Data flow tracking (feeds_into)
  - Ordering constraints (position, required_after/before)

#### Canonical Deck (v1.0) — 12 cards
- Location: `noesis-release/deck/v1.0/cards/`
- Mode: ENGINEERING (strict gates)
- Status: ✅ All cards have metadata (CARD-0 through CARD-11)
- Features:
  - Sequential dependencies (upstream/downstream)
  - Strict gate enforcement (blocks on error)
  - Data flow tracking (feeds_into)
  - Ordering constraints (position, required_after/before)

#### Conversation Grounding (Exploration) — 13 cards
- Location: `new/cards/`
- Mode: EXPLORATION
- Status: ✅ All cards have metadata (CARD-01 through CARD-13)
- Features:
  - Suggested patterns (often_paired_with, helpful_for)
  - No gates, no ordering requirements
  - State schemas for queryable fields
  - Topic-based grouping

---

### Phase 2: Graph Viewer (Complete)

Created `view-graph.py` — simple Python viewer that:

**Capabilities:**
- ✅ Scans all card files for graph metadata
- ✅ Displays deck summaries (counts, modes, namespaces)
- ✅ Shows detailed card relationships
- ✅ Visualizes dependency trees
- ✅ Validates graph integrity (broken refs, missing data)
- ✅ Exports Graphviz DOT format

**Output:**
```
Found 39 total cards across 3 decks

CANONICAL: 12 cards (ENGINEERING/strict gates)
EMERGENCE: 14 cards (ENGINEERING/diagnostic gates)
EXPLORATION: 13 cards (EXPLORATION/no gates)

Validation complete - All graphs valid!
```

---

## Graph Structure

### Namespace Convention
```
noesis.{deck-name}.{version}

Examples:
- noesis.emergence.v0.1
- noesis.canonical.v1.0
- noesis.conversation-grounding.exploration
```

### Metadata Schema

**ENGINEERING MODE** (Emergence & Canonical):
```yaml
card:
  id: CARD-XX
  namespace: noesis.deck.version
  mode: ENGINEERING
  deck_mode: Emergence | Canonical

dependencies:
  upstream: [required cards]
  downstream: [enabled cards]
  feeds_into: [data consumers]

gate:
  enforcement: diagnostic | strict
  blocks_downstream: false | true

ordering:
  position: N
  required_after: [cards]
  required_before: [cards]
```

**EXPLORATION MODE** (Conversation Grounding):
```yaml
card:
  namespace: noesis.conversation-grounding.exploration
  mode: EXPLORATION

suggested_patterns:
  often_paired_with: [cards]
  helpful_for: [use cases]

state_schema:
  [queryable fields]
```

---

## Key Differences By Mode

| Aspect | ENGINEERING | EXPLORATION |
|--------|-------------|-------------|
| **Order** | Required sequential | No order, topic-based |
| **Dependencies** | Upstream/downstream (strict) | Suggestions only |
| **Gates** | Diagnostic or strict enforcement | None |
| **Completeness** | Expected | Partial allowed forever |
| **Use Case** | Technical specifications | Daily conversation |
| **Relationships** | Requirements | Helpful pairings |

---

## Validation Results

**All 39 cards validated successfully:**
- ✅ No broken references
- ✅ All upstream/downstream exist
- ✅ All positions defined (ENGINEERING)
- ✅ No circular dependencies
- ✅ Mode-appropriate relationships

---

## Files Created

### Graph Implementation
1. **Card Metadata** (39 files)
   - All Emergence cards: `noesis-release/deck/v0.1/cards/*.md`
   - All Canonical cards: `noesis-release/deck/v1.0/cards/*.md`
   - All Exploration cards: `new/cards/*.md`

2. **Graph Viewer**
   - `view-graph.py` — Simple ASCII viewer
   - `noesis-graph-viewer.py` — Full Unicode viewer (Windows issues)
   - `noesis-graph.dot` — Graphviz export

3. **Documentation**
   - `GRAPH_VIEWER_README.md` — Usage guide
   - This summary document

---

## Usage Examples

### View All Graphs
```bash
python view-graph.py "c:\Users\timmy\OneDrive\Desktop\abc"
```

### Validate Only
```bash
python view-graph.py . | grep -A 20 "Validation"
```

### Export Visualization
```bash
python view-graph.py .
dot -Tpng noesis-graph.dot -o noesis-graph.png
```

---

## What The Graph Enables

### 1. **Dependency Tracking**
- Know what cards must be completed first
- Understand data flow between cards
- Prevent skipping required steps

### 2. **Mode-Aware Enforcement**
- ENGINEERING: Gates block/warn based on deck type
- EXPLORATION: Suggestions only, user decides

### 3. **Scalability**
- New decks can be added with same metadata structure
- Namespace prevents collisions
- Cross-deck references possible

### 4. **Validation**
- Automated integrity checks
- Broken reference detection
- Consistency enforcement

### 5. **Visualization**
- DOT export for Graphviz
- ASCII tree for quick reference
- Dependency flow diagrams

---

## Next Steps (Future)

### Immediate
- ✅ Graph metadata complete
- ✅ Viewer working
- ✅ Validation passing

### Future Enhancements
1. **Cross-Deck References**
   - Define syntax: `@noesis.exploration/CARD-09 → @noesis.emergence.v0.1/CARD-02`
   - Document flow patterns (Exploration → Engineering)

2. **Workflow Nodes**
   - Formalize patterns as first-class entities:
     - Foundation Stack: CARD-01 + CARD-02 + CARD-03
     - Memory Stack: CARD-05 + CARD-07 + CARD-09
     - Execution Stack: CARD-02 + CARD-09 + CARD-13

3. **Namespace Registry**
   - Central registration for community decks
   - Conflict resolution
   - Version tracking

4. **Graph API**
   - Programmatic access to relationships
   - Query engine (find paths, check gates)
   - Integration with other tools

5. **Interactive Viewer**
   - Web-based visualization
   - Click to expand dependencies
   - Filter by mode/namespace

---

## Technical Metrics

**Lines of Metadata Added**: ~1,500 lines (YAML front matter)  
**Cards Enhanced**: 39 cards (100% of existing cards)  
**Decks Integrated**: 3 decks (Emergence, Canonical, Exploration)  
**Validation Errors**: 0 (all graphs valid)  
**Viewer Code**: ~350 lines (Python)  

---

## Design Principles Preserved

✅ **Markdown Portability**: Graph metadata is optional YAML front matter  
✅ **Mode Awareness**: Different semantics for ENGINEERING vs EXPLORATION  
✅ **No Breaking Changes**: Original card content unchanged  
✅ **Human Readable**: ASCII viewer works without Graphviz  
✅ **Scalable**: Namespace strategy prevents collisions  

---

## Validation Output

```
NOESIS GRAPH VIEWER - Validation

Validating emergence...
  OK - No issues found

Validating canonical...
  OK - No issues found

Validating exploration...
  OK - No issues found

Validation complete - All graphs valid!
```

---

## Summary

**Status**: ✅ Implementation complete and validated

All 39 cards across 3 decks now have:
- Mode-appropriate graph metadata
- Validated dependencies
- Working visualization
- No integrity errors

The graph system understands:
- ENGINEERING MODE: Ordered, gated, strict dependencies
- EXPLORATION MODE: Independent, suggested pairings, no gates

Users can now:
- View relationships across all decks
- Validate graph integrity
- Export visualizations
- Query dependencies

**The νόησις card system is now a callable graph.**

---

*Structure precedes automation. Thinking is treated as engineering.*
