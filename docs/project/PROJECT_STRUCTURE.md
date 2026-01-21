# νόησις Artifact Deck — Project Structure

Author: Timothy Wesley Stone  
License: Open / Shareable

This document describes the canonical organization of the νόησις project.

---

## Root Level — Governance & Documentation

```
/
├── POLICY.md              # Canonical governance rules
├── CHANGELOG.md           # Version history and milestones
├── WHICH_DECK.md          # Deck selection guide for users
├── .github/
│   └── copilot-instructions.md  # AI agent operational guide
├── noesis-release/         # Main release package
└── noesis-templates/       # Enhanced templates
```

---

## noesis-release/ — Main Release Package

```
noesis-release/
├── LICENSE                # Open/Shareable license
├── README.md              # Release overview with paired naming
├── deck/
│   ├── v0.1/              # Emergence Deck (v0.1)
│   │   ├── README.md      # Deck purpose and rules
│   │   ├── noesis-emergence-deck-v0.1.md  # Master consolidated
│   │   └── cards/         # 14 individual card files (CARD-00 to CARD-13)
│   └── v1.0/              # Canonical Deck (v1.0)
│       ├── README.md      # Deck purpose and rules
│       ├── noesis-canonical-deck-v1.0.md  # Master consolidated
│       └── cards/         # 12 individual card files (CARD-0 to CARD-11)
└── templates/
    ├── README.md          # Template usage guide (deck-agnostic)
    ├── PACKAGE_TEMPLATE.md
    ├── CARD_TEMPLATE.md
    ├── v0.1/              # Emergence-specific templates
    │   ├── vonos-emergence-template.md
    │   └── cards/         # 14 blank card templates
    └── v1.0/              # Canonical-specific templates
        ├── vonos-canonical-template.md
        └── cards/         # 12 blank card templates
```

---

## noesis-templates/ — Enhanced Templates

```
noesis-templates/
├── README.md              # Upgrade pack overview
└── templates/
    ├── PACKAGE_TEMPLATE.md       # Enhanced PACKAGE with checkboxes
    ├── CARD_TEMPLATE.md          # Enhanced CARD with sections
    └── LLM_FILL_PROMPT_TEMPLATE.md  # AI agent filling guidance
```

---

## File Naming Conventions

### Master Deck Files
- Emergence: `noesis-emergence-deck-v0.1.md`
- Canonical: `noesis-canonical-deck-v1.0.md`

### Individual Card Files
- Format: `{number}_CARD-{id}_{NAME}_{description}.md`
- Emergence example: `01_CARD-01_WRITE_UP_Raw_Narrative_Intake.md`
- Canonical example: `01_CARD-1_WRITE_UP_Narrative_Anchor.md`

### Template Files
- Base: `PACKAGE_TEMPLATE.md`, `CARD_TEMPLATE.md`
- Templates are deck-agnostic (work for both Emergence and Canonical)

---

## Deck Organization Principles

### Emergence Deck (v0.1)
- **14 cards**: CARD-00 (meta) through CARD-13 (implementation)
- **Purpose**: Exploration, discovery, rapid iteration
- **Files**: Each card self-identifies with `DeckName` and `DeckMode` headers
- **Location**: `noesis-release/deck/v0.1/`

### Canonical Deck (v1.0)
- **12 cards**: CARD-0 (package) through CARD-11 (execution)
- **Purpose**: Authoritative specification, preservation
- **Files**: Each card self-identifies with `DeckName` and `DeckMode` headers
- **Location**: `noesis-release/deck/v1.0/`

---

## Template Organization

Templates are stored in three locations:

1. **Base Templates** (`noesis-release/templates/`)
   - Minimal structure
   - Quick start
   - Deck-agnostic

2. **Version-Specific Templates** (`noesis-release/templates/v0.1/` and `v1.0/`)
   - Complete blank card sets
   - Mirrors deck structure
   - Numbered for sequential filling

3. **Enhanced Templates** (`noesis-templates/templates/`)
   - Enhanced with detailed guidance
   - Includes LLM_FILL_PROMPT_TEMPLATE
   - Production-ready sections

**Usage Rule**: Users can start from any template location. All templates work with both decks (enforcement differs by deck mode).

---

## Governance File Hierarchy

1. **POLICY.md** — Canonical governance source of truth
2. **.github/copilot-instructions.md** — Operational guide for AI agents
3. **WHICH_DECK.md** — User-facing deck selection
4. **CHANGELOG.md** — Historical record
5. **Deck READMEs** — Deck-specific rules and context

---

## Version Control Semantics

- **v0.x** = Emergence Deck line (experimental, breaking changes allowed)
- **v1.x** = Canonical Deck line (stable, backward compatible)
- **File paths** = Keep version numbers (`/v0.1/`, `/v1.0/`) for machine stability
- **Human text** = Always use paired naming ("Emergence Deck (v0.1)")

---

## Card Identity Requirements

Every card must include:
```
DeckName: νόησις Emergence Deck | νόησις Canonical Deck
DeckMode: Emergence Deck (v0.x) | Canonical Deck (v1.x)
```

This ensures cards remain self-identifying after copy/paste travel.

---

## Distribution Rules

- **Portability**: All content works as plain markdown
- **No tooling**: Copy/paste workflow only
- **Self-contained**: Each file includes authorship and license
- **Deck-aware**: Cards know which deck they belong to

---

Structure precedes automation.  
Thinking is treated as engineering.
