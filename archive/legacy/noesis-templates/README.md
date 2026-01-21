# νόησις Enhanced Templates

Author: Timothy Wesley Stone  
License: Open / Shareable

Enhanced, production-ready templates for the νόησις Artifact Deck framework.
- Human-first, portable, engine-agnostic
- Forces concrete, operational specs (not vague notes)
- Works for both Emergence Deck (v0.x) and Canonical Deck (v1.x)

## Files
- templates/PACKAGE_TEMPLATE.md
- templates/CARD_TEMPLATE.md
- templates/LLM_FILL_PROMPT_TEMPLATE.md

## How to use
1) Drop these into your existing νόησις repo under /templates
2) When starting a new project, copy PACKAGE_TEMPLATE first
3) Then copy CARD_TEMPLATE for each card you want to create
4) Optional: use LLM_FILL_PROMPT_TEMPLATE to have any model draft content safely

## Deck-Agnostic Design
Templates work with both decks. Usage strictness differs:
- **Emergence Deck**: Partial filling allowed, gates diagnostic
- **Canonical Deck**: Complete filling required, gates binding
