# Architecture

## Components

| Part | Tech | Responsibility |
|---|---|---|
| Frontend | React 19, Vite, CoreUI | Upload, dashboard, scan history and detail views |
| API | FastAPI | `/api/scans` endpoints, validation, error handling |
| Scan engines | Python | Rules, drift, risk scoring (deterministic) |
| AI layer | Gemini via `google-genai` | Plain-language summary of findings |
| Storage | Supabase (Postgres) | Scan history, one row per scan |

## Scan pipeline

1. **Parse** (`app/utils/parser.py`): accepts `.json`, `.yaml`, `.yml` up to
   1 MB. YAML is loaded with `safe_load`, so no code can be executed from an
   upload.
2. **Extract resources** (`app/services/scan_service.py`): a flat object is one
   `generic` resource; `{"resources": [...]}` gives several typed resources
   (`s3_bucket`, `iam_user`, ...).
3. **Rules** (`app/services/rule_engine.py`, `app/rules/*.yaml`): each rule
   applies to the resource types listed in `resource_types`. If the control is
   missing, `on_missing` decides: `fail`, `info` or `skip`.
4. **Drift** (`app/services/drift_engine.py`): diffs the resource against its
   baseline (`app/core/baseline.py`), including nested keys. Paths already
   judged by a rule are skipped so a problem is reported once.
5. **Risk** (`app/services/risk_engine.py`): fixed deductions per severity
   (critical 40, high 20, medium 8, low 3, info 0). The worst finding caps the
   level: any critical means at best "High Risk"; any high means at best
   "Moderate". The result lists the reasons.
6. **AI summary** (`app/ai/analyzer.py`): optional. Gets only structured,
   truncated findings, is told to treat them as untrusted data, and cannot
   change severities. If it fails, the scan is saved without it.
7. **Store** (`app/services/scan_repository.py`): Supabase when configured,
   otherwise in memory.

## Security decisions

- The backend uses the Supabase **service role** key, server-side only. The
  `scans` table has row-level security on with no policies, so the public anon
  key cannot read it.
- Severity and score are always computed by code, never by the AI.
- Raw uploads never reach the AI model (prompt-injection defense).
- Upload size is capped before parsing.
- Unhandled errors are logged server-side; clients get a generic message.

## Data model (`scans` table)

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | primary key |
| `created_at` | timestamptz | default `now()` |
| `filename` | text | |
| `resources_scanned` | int | |
| `risk_score` | int | 0–100 |
| `risk_level` | text | Excellent / Good / Moderate / High Risk / Critical |
| `findings_count` | int | |
| `severity_counts` | jsonb | `{critical, high, medium, low, info}` |
| `risk` | jsonb | score details and explanation |
| `findings` | jsonb | list of findings |
| `ai_summary` | text | nullable |

## Planned

- Supabase Auth, `org_id` on every table, RLS policies per organization.
- Baseline approval: versioned, per-org baselines stored in the database.
- Connectors that pull live configuration (AWS first) instead of uploads.
- Remediation verification by re-scanning and comparing.
- Append-only audit log.
