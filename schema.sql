-- Run this once in the Supabase SQL Editor.
create table if not exists public.citation_snapshots (
    observed_on date primary key,
    total_citations integer not null check (total_citations >= 0),
    year_citations integer not null check (year_citations >= 0),
    fetched_at timestamptz not null default now()
);

alter table public.citation_snapshots enable row level security;

-- The app uses the Supabase anon key and needs read-only access.
-- GitHub Actions uses the service-role key to insert/update daily snapshots.
create policy "Allow public read of citation snapshots"
on public.citation_snapshots
for select
to anon, authenticated
using (true);

-- Do NOT add an anon insert/update policy. Keep the service-role key
-- only in GitHub Actions secrets, never in browser code or public repos.
