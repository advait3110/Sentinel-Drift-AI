-- Run once in Supabase: Dashboard -> SQL Editor -> New query -> paste -> Run.

create extension if not exists pgcrypto;

create table if not exists public.scans (
  id                uuid primary key default gen_random_uuid(),
  created_at        timestamptz not null default now(),
  filename          text not null,
  resources_scanned integer not null,
  risk_score        integer not null check (risk_score between 0 and 100),
  risk_level        text not null,
  findings_count    integer not null,
  severity_counts   jsonb not null default '{}'::jsonb,
  risk              jsonb not null,
  findings          jsonb not null,
  ai_summary        text
);

create index if not exists scans_created_at_idx on public.scans (created_at desc);

-- Lock the table down. With RLS on and no policies, only the backend's
-- service role key can read or write it; the public anon key cannot.
-- When auth + multi-tenancy are added, add an org_id column and policies.
alter table public.scans enable row level security;
