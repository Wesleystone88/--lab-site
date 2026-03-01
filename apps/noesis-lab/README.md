# νόησις — Noesis Lab

Research site for the νόησις routed cognitive architecture.

## Stack

- **Frontend**: React 19 + Vite + TypeScript + Tailwind CSS
- **Backend**: Netlify Functions (Node.js / TypeScript)
- **Hosting**: Netlify

## Structure

```
noesis-lab/
├── frontend/               # React 19 + Vite SPA
│   ├── src/
│   │   ├── pages/          # Home, Results, Architecture, Agent, Environment, About
│   │   ├── components/     # Nav, Footer
│   │   └── styles/         # globals.css (Tailwind + custom)
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── netlify/
│   └── functions/          # access-request.ts, contact.ts
├── netlify.toml
├── package.json
└── .env.example
```

## Local Development

```bash
# Install frontend dependencies
cd frontend && npm install

# Start dev server
npm run dev
# → http://localhost:5173
```

## Deploy to Netlify

1. Push repo to GitHub
2. Connect to Netlify (New site → Import from Git)
3. Netlify auto-detects `netlify.toml`:
   - Build command: `npm run build`
   - Publish dir: `dist`
   - Functions dir: `netlify/functions`
4. Set environment variables in Netlify dashboard if needed

## Pages

| Route | Description |
|-------|-------------|
| `/` | Home — hero, stats, architecture overview |
| `/results` | Evidence — episode traces, learning curves, expandable raw traces |
| `/architecture` | 7-layer system walkthrough |
| `/agent` | SextBioRAG — 6-pillar cognitive system deep dive |
| `/environment` | Environment service + access request form |
| `/about` | Lab mission, what this is and isn't |

## Adding Email Notifications (Access Requests)

In `netlify/functions/access-request.ts`, the form data is currently logged. To send email notifications:

1. Add Resend (recommended): `npm install resend` in functions
2. Set `RESEND_API_KEY` in Netlify environment variables  
3. Uncomment and configure the email send block in the function

---

© 2026 Timothy Wesley Stone · Noesis Lab · All Rights Reserved  
νόησις™ — Intelligence, Engineered
