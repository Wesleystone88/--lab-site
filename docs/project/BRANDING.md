# νόησις Artifact Deck — Branding Guidelines

Author: Timothy Wesley Stone  
License: Open / Shareable

## Official Name

**νόησις Artifact Deck** (Greek: "noesis" - meaning intellect, understanding, cognition)

Alternative spellings:
- νόησις (canonical, Greek characters, preferred in documentation)
- noesis (ASCII-safe, filesystem-friendly, code identifiers)
- vóṇōs (legacy, deprecated)
- vónoįs (legacy, deprecated)
- vonos (legacy, deprecated)

## Deck Identity

Always use full paired naming in human-facing text:

✅ **Correct:**
- "νόησις Emergence Deck (v0.1)"
- "νόησις Canonical Deck (v1.0)"

❌ **Incorrect:**
- "v0.1" alone
- "Emergence Deck" without version
- "noesis v1.0" (missing deck name)

## Folder Naming Conventions

### Distribution Packages
- `noesis-release/` — Main framework distribution (lowercase, hyphenated)
- `noesis-templates/` — Enhanced templates package (lowercase, hyphenated)

### Rationale
- Lowercase for cross-platform compatibility
- ASCII-safe "noesis" for filesystem compatibility
- Hyphens over underscores for readability
- Short prefixes for easy tab-completion
- No spaces for terminal-friendliness

## File Naming Conventions

### Master Deck Files
- `noesis-emergence-deck-v0.1.md` (lowercase kebab-case)
- `noesis-canonical-deck-v1.0.md` (lowercase kebab-case)

### Template Master Files
- `noesis-emergence-template.md`
- `noesis-canonical-template.md`

### Individual Cards
Pattern: `{number}_CARD-{id}_{NAME}_{description}.md`

**Emergence Deck (14 cards):**
- `00_CARD-00_DECK_SCHEMA_Meta_Card.md`
- `01_CARD-01_WRITE_UP_Raw_Narrative_Intake.md`
- `13_CARD-13_IMPLEMENTATION.md`

**Canonical Deck (12 cards):**
- `00_CARD-0_PACKAGE_Domain_Envelope.md`
- `01_CARD-1_WRITE_UP_Narrative_Anchor.md`
- `11_CARD-11_EXECUTION_Build_Plan.md`

### Base Templates
- `PACKAGE_TEMPLATE.md` (all caps, generic)
- `CARD_TEMPLATE.md` (all caps, generic)
- `LLM_FILL_PROMPT_TEMPLATE.md` (all caps, usage guidance)

### Rationale
- Master files: lowercase for consistency with modern conventions
- Cards: SCREAMING_CASE for section names (WRITE_UP, INTENT, etc.)
- Numbers prefix for lexicographic sorting
- Hyphens for multi-word file names
- Templates stay generic (no branding in filename)

## Governance Documents

Core files at repository root:
- `POLICY.md` — Constitutional governance source
- `CHANGELOG.md` — Version history
- `WHICH_DECK.md` — Deck selection guide
- `README.md` — Project overview
- `PROJECT_STRUCTURE.md` — Detailed organization
- `BUILD_SUMMARY.md` — Build verification
- `BRANDING.md` — This file
- `.github/copilot-instructions.md` — AI agent guide

## Terminology Standards

### Deck References
- "Emergence Deck" — exploration, ideation
- "Canonical Deck" — specification, authority
- Never: "the v0.1", "the Canonical", "deck v1.0"

### Version References
- Use bare versions in technical contexts only:
  - Folder paths: `deck/v0.1/`
  - File references: `noesis-emergence-deck-v0.1.md`
  - Git tags: `v0.1.0`, `v1.0.0`

### Framework References
- "νόησις Artifact Deck" or "νόησις framework"
- "artifact deck" (generic concept)
- "card" (individual specification artifact)

## Visual Identity

### Headers
Standard header format for all authored files:

```markdown
# Title

Author: Timothy Wesley Stone  
License: Open / Shareable
```

### Emoji Conventions (optional)
From WHICH_DECK.md:
- 🟡 Emergence Deck
- 🔵 Canonical Deck
- 🔁 Promotion workflow

### Typography
- Use Greek characters in documentation: νόησις
- Use ASCII-safe in paths: noesis
- Never mix: don't use "νόησις_release" or "noesis_DECK"

## Anti-Patterns

❌ **Don't:**
- Use underscores in new folder names (old: `vonois_release`)
- Use all caps for markdown filenames (old: `VONOIS_Emergence_Deck_(v0.1).md`)
- Reference versions without deck name in prose
- Mix branding variants (vonois vs vonos vs vóṇōs vs noesis)
- Use spaces in filesystem names

✅ **Do:**
- Use hyphens for multi-word folders (`noesis-release`)
- Use lowercase kebab-case for master files (`noesis-emergence-deck-v0.1.md`)
- Always pair deck name with version in human-facing text
- Prefer νόησις in documentation, noesis in filesystem
- Keep filesystem names terse and terminal-friendly

## Migration History

### January 19, 2026 - Greek Branding Update
- Renamed `vonos-release/` → `noesis-release/` (ASCII-safe Greek)
- Renamed `vonos-templates/` → `noesis-templates/`
- Renamed `vonos-emergence-deck-v0.1.md` → `noesis-emergence-deck-v0.1.md`
- Renamed `vonos-canonical-deck-v1.0.md` → `noesis-canonical-deck-v1.0.md`
- Updated all documentation: vóṇōs → νόησις (Greek characters)
- Updated all 26 card DeckName fields
- Updated all path references across documentation

### January 2026 - Professional Branding Update
- Renamed `vonois_release/` → `vonos-release/`
- Renamed `vonois_templates_upgrade_pack/` → `vonos-templates/`
- Renamed `VONOIS_Emergence_Deck_(v0.1).md` → `vonos-emergence-deck-v0.1.md`
- Renamed `VONOIS_Canonical_Deck_(v1.0).md` → `vonos-canonical-deck-v1.0.md`
- Updated all documentation with new paths
- Standardized terminology across 30+ files

### Rationale
User request: "correct spelling νόησις with these exact characters"

Goal: Use authentic Greek characters (νόησις = noesis = intellect, understanding) in documentation while maintaining ASCII-safe filesystem names (noesis).

---

**Remember:** This isn't an engine, it's a helper. Names should be clean, memorable, and copy/paste friendly.
