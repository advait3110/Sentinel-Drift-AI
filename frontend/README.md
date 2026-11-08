# Sentinel Drift AI — Frontend

React 19 + Vite + CoreUI dashboard for Sentinel Drift AI. It talks to the
FastAPI backend in `../backend`.

## Pages

| Route | Page |
|---|---|
| `#/dashboard` | Current risk score, risk trend, recent scans |
| `#/scan` | Upload a JSON/YAML config and run a scan |
| `#/scans` | Scan history |
| `#/scans/:id` | One scan: score, AI summary, filterable findings |

The app uses `HashRouter`, so URLs contain `#/`. That works on any static host
without rewrite rules.

## Setup (Windows, Command Prompt)

```cmd
cd frontend
npm install
copy .env.example .env
npm start
```

`npm start` runs `vite --open` on http://localhost:3000 and opens the browser.
The backend must be running on http://localhost:8000 (see `../backend/README.md`)
with `CORS_ORIGINS=http://localhost:3000` in its `.env`.

The header badge shows the backend state:
- **API online**: connected, scans saved to Supabase.
- **API online · temporary storage**: connected, but Supabase isn't configured on
  the backend, so scans are lost when it restarts.
- **API offline**: the backend isn't reachable at `VITE_API_URL`.

## Scripts

| Command | What it does |
|---|---|
| `npm start` / `npm run dev` | Dev server on port 3000, opens the browser |
| `npm run build` | Production build into `build/` |
| `npm run serve` | Preview the production build |
| `npm run lint` | ESLint + Prettier checks |

## Structure

```
src/
├── api/client.js          All backend calls
├── config.js              App constants (upload limits, theme key)
├── components/            Layout: header, sidebar, footer, breadcrumb,
│                          API status badge, error boundary, StatCard
├── layout/DefaultLayout.jsx
├── views/
│   ├── dashboard/         Overview
│   ├── scan/              Upload page, result view, findings table
│   ├── history/           Scan list and scan detail
│   ├── error-pages/       Full-page 404 / 500
│   └── NotFound.jsx       In-app 404
├── utils/severity.js      Severity colors, labels, formatting
├── routes.js              Page routes
├── _nav.jsx               Sidebar menu
└── scss/style.scss        Theme + app styles
```

## Configuration

`.env`:
```
VITE_API_URL=http://localhost:8000
```

Upload limits in `src/config.js` match the backend (`MAX_UPLOAD_BYTES`, 1 MB).

## License

The UI is based on the CoreUI Free React Admin Template, MIT licensed (see `LICENSE`).
