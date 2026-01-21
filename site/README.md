# noesis-lab.com Website

**Domain**: https://noesis-lab.com

This directory contains the **presentation layer** for the νόησις project - website content, assets, and generated builds.

## Organizational Principle

Following the gaming card collection metaphor:
- **Product** (card system) lives in `../decks/`, `../templates/`, `../docs/`
- **Website** (this directory) references but never contains the product

Like Magic: The Gathering separates card data from Gatherer website, or Pokémon TCG separates physical cards from pokemon.com.

## Structure

```
site/
├── index.html              # Main landing page
├── assets/
│   ├── css/
│   │   └── style.css       # Website styles
│   ├── images/             # Graphics, logos, screenshots
│   └── js/                 # Client-side scripts (if needed)
├── content/                # Blog posts, tutorials (future)
├── build/                  # Generated site (gitignored)
└── README.md               # This file
```

## Development

This is a static HTML/CSS site. No build process required.

### Local Preview

Open `index.html` directly in a browser, or use a simple HTTP server:

```bash
# Python 3
python -m http.server 8000

# Node.js (if http-server is installed)
npx http-server .

# VS Code Live Server extension
# Right-click index.html → "Open with Live Server"
```

Then visit: http://localhost:8000

### Deployment

Static site can be deployed to:
- GitHub Pages
- Netlify
- Vercel
- Any static hosting service

## File Structure Separation

**Product files** (`../decks/`, `../templates/`, `../docs/`) are version-controlled, cryptographically seeded artifacts.

**Website files** (`site/`) are presentation layer - HTML, CSS, images, generated content.

The website can display, showcase, and present cards - the separation is about **file organization**, not content access. Like how Magic: The Gathering keeps card data files separate from Gatherer website files, but the website displays the cards.

**Source of Truth**: Card markdown files in `../decks/` (versioned, seeded)  
**Presentation Layer**: Website in `site/` (can embed, display, reference cards)

## Copyright & Licensing

The νόησις system, brand, and website are proprietary intellectual property:
- **Copyright © 2026 Timothy Wesley Stone. All Rights Reserved.**
- Individual cards may be shared/used with attribution (see ../LICENSE)
- System architecture, methodology, and website design are protected IP

Like collectible trading cards: you can share cards you have, but can't manufacture copies of the entire system.

## Links to Product

All links in `index.html` point to GitHub repository paths:
- Card decks: `../decks/engineering/`, `../decks/exploration/`
- Templates: `../decks/templates/`
- Documentation: `../docs/foundation/`

These links work when deployed because they reference the GitHub repository directly.

---

Author: Timothy Wesley Stone  
License: Open / Shareable
