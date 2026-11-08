# Sentinel Drift AI — Backend

FastAPI service that scans configuration files for security misconfigurations
and drift from an approved baseline, scores the risk, adds an optional AI
summary (Gemini), and stores every scan in Supabase.

## Structure

```
backend/
├── app/
│   ├── main.py                  App setup, CORS, error handlers, /health
│   ├── api/scans.py             POST/GET /api/scans endpoints
│   ├── ai/analyzer.py           Gemini summary (explains, never scores)
│   ├── core/config.py           Settings from .env
│   ├── core/baseline.py         Approved baselines per resource type
│   ├── database/supabase_client.py
│   ├── rules/security_rules.yaml   Security rules as data
│   ├── schemas/finding.py       Typed models (Finding, ScanResult, ...)
│   ├── services/
│   │   ├── scan_service.py      Full scan pipeline
│   │   ├── rule_engine.py       Evaluates YAML rules
│   │   ├── drift_engine.py      Baseline comparison
│   │   ├── risk_engine.py       Score + risk level + explanation
│   │   ├── scan_repository.py   Supabase / in-memory storage
│   │   └── normalize.py         Shared helpers
│   └── utils/parser.py          JSON/YAML upload parsing
├── migrations/001_create_scans.sql
├── tests/
├── uploads/                     Sample configs to try
├── requirements.txt
├── Dockerfile
└── .env.example
```

## Setup (Windows, Command Prompt)

```cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env`:
- `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` (Supabase → Project Settings → API).
  Without them the app still runs, using in-memory storage that is lost on restart.
- `GEMINI_API_KEY` (optional). Without it, scans run without an AI summary.

Create the table once: Supabase → SQL Editor → paste
`migrations/001_create_scans.sql` → Run.

## Run

```cmd
python -m pytest
uvicorn app.main:app --reload --port 8000
```

- Health: http://localhost:8000/health
- API docs: http://localhost:8000/docs

## API

| Method | Path | Description |
|---|---|---|
| POST | `/api/scans` | Upload `.json` / `.yaml` / `.yml` (form field `file`, max 1 MB). Returns the stored scan. |
| GET | `/api/scans?limit=50` | Recent scans, summary only. |
| GET | `/api/scans/{id}` | One scan with all findings. |

## Upload formats

Single resource (flat):
```json
{ "public": false, "encrypted": true, "mfa_enabled": true }
```

Multiple resources:
```yaml
resources:
  - id: my-bucket
    type: s3_bucket
    config: { public: false, encrypted: true }
```

See `uploads/` for complete examples.

## Adding a rule

Add an entry to `app/rules/security_rules.yaml` (or a new `.yaml` file in that
folder). Operators: `equals`, `not_equals`, `in`, `not_in`, `gte`, `lte`,
`exists`. `on_missing`: `fail`, `info` or `skip`. Rules are validated at
startup; a broken rule stops the server with a clear error.

## Not built yet

Authentication, multi-tenancy (org_id + RLS policies), baseline approval
workflow, cloud connectors, remediation verification.
