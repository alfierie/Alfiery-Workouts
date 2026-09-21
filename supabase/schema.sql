-- Alfiery Workouts — Supabase schema.
--
-- Paste this whole file into your project's SQL Editor and press Run, once.
-- Safe to re-run: every statement is idempotent.
--
-- Security model: row level security is on, and every policy is scoped to
-- `auth.uid() = user_id`. The app ships a *publishable* key, so without these
-- policies anyone who found your URL could read your log. The anon role is
-- deliberately granted nothing at all.

create table if not exists public.entries (
  id          uuid        primary key,
  user_id     uuid        not null default auth.uid() references auth.users (id) on delete cascade,
  date        date        not null,
  exercise    text        not null,
  weight_kg   numeric     not null check (weight_kg >= 0),
  reps        integer     not null check (reps > 0),
  sets        integer     not null check (sets > 0),
  notes       text        not null default '',
  -- Deletions are tombstoned rather than removed, so a delete made offline still
  -- propagates to your other devices instead of the row reappearing.
  deleted     boolean     not null default false,
  updated_at  timestamptz not null default now()
);

-- The only query pattern: "everything for this user, ordered by version".
create index if not exists entries_user_updated_idx
  on public.entries (user_id, updated_at);

alter table public.entries enable row level security;

drop policy if exists "own rows: select" on public.entries;
drop policy if exists "own rows: insert" on public.entries;
drop policy if exists "own rows: update" on public.entries;
drop policy if exists "own rows: delete" on public.entries;

create policy "own rows: select" on public.entries
  for select to authenticated
  using (auth.uid() = user_id);

create policy "own rows: insert" on public.entries
  for insert to authenticated
  with check (auth.uid() = user_id);

create policy "own rows: update" on public.entries
  for update to authenticated
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

create policy "own rows: delete" on public.entries
  for delete to authenticated
  using (auth.uid() = user_id);

-- Least-privilege grants. Note the absence of `anon`: signed-out requests must
-- not reach this table at all.
revoke all on public.entries from anon;
grant select, insert, update, delete on public.entries to authenticated;

-- Confirm the table is exposed to the Data API. Newer projects require tables to
-- be opted in under Project Settings → Data API → Exposed tables. If `test
-- connection` in the app reports a 404 with "relation does not exist", that
-- toggle is the cause, not the SQL.
