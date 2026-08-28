-- ═══════════════════════════════════════════════════════════════
-- Crea8it Labs — Multi-tenant schema (Supabase / Postgres)
-- Three roles: super_admin (you), org_admin (cohort operator), participant
-- ═══════════════════════════════════════════════════════════════

-- ── Organizations ─────────────────────────────────────────────
create table organizations (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  org_code text unique not null,          -- e.g. "AICRE4821" — participants join with this
  admin_name text not null,               -- org admin's display name
  admin_whatsapp text not null,           -- used by participants to reach their org admin
  admin_email text not null,
  plan text not null default 'free',      -- free | pro | enterprise (drives limits/billing)
  is_active boolean not null default true, -- super_admin can suspend an org
  created_at timestamptz not null default now()
);

-- ── Profiles ──────────────────────────────────────────────────
-- One row per auth.users entry. Role + org_id live here, and RLS
-- policies everywhere else key off this table via auth.uid().
create table profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  org_id uuid references organizations(id),   -- null for super_admin
  role text not null check (role in ('super_admin', 'org_admin', 'participant')),
  full_name text not null,
  whatsapp text,
  email text not null,
  created_at timestamptz not null default now()
);

-- ── Payment codes (per-org, used at participant registration) ──
create table payment_codes (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references organizations(id),
  code text not null,
  used boolean not null default false,
  created_at timestamptz not null default now(),
  unique (org_id, code)
);

-- ── Programs (an org can run several at once) ───────────────────
create table programs (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references organizations(id),
  name text not null,
  unit_label text not null default 'Week',
  is_active boolean not null default false,   -- is this the org's currently-selected program
  active_week int not null default 1,         -- which week/unit is unlocked for participants
  created_at timestamptz not null default now()
);

-- ── Program content (title/theme/materials/tasks/prompt per unit) ─
create table program_content (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references organizations(id),
  program_id uuid not null references programs(id) on delete cascade,
  week int not null,
  type text not null check (type in ('title', 'theme', 'material', 'task', 'prompt')),
  order_index int not null default 0,
  value text not null default '',
  extra text default ''
);

-- ── Progress ─────────────────────────────────────────────────
create table progress (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references organizations(id),
  participant_id uuid not null references profiles(id),
  program_id uuid not null references programs(id),
  week int not null,
  task_index int not null,
  completed_at timestamptz not null default now(),
  unique (participant_id, program_id, week, task_index)
);

-- ── Reflections & feedback ───────────────────────────────────
create table reflections (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references organizations(id),
  participant_id uuid not null references profiles(id),
  program_id uuid not null references programs(id),
  week int not null,
  response text not null default '',
  feedback text default '',
  submitted_at timestamptz not null default now(),
  unique (participant_id, program_id, week)
);

-- ── Last active (heartbeat for org admin dashboards) ─────────
create table last_active (
  org_id uuid not null references organizations(id),
  participant_id uuid primary key references profiles(id),
  last_active_at timestamptz not null default now()
);

-- ── Resources (org-wide library — reusable across programs & tasks) ─
-- Not scoped to a program/week, unlike program_content materials —
-- this is what makes it survive an org switching its active program,
-- and lets the same resource be pointed to from multiple programs'
-- weekly materials or task links instead of being re-typed each time.
create table resources (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references organizations(id),
  title text not null,
  description text default '',
  resource_type text not null default 'article'
    check (resource_type in ('article', 'video', 'pdf', 'doc', 'tool', 'other')),
  source_type text not null check (source_type in ('link', 'file')),
  url text,          -- set when source_type = 'link'
  file_path text,    -- set when source_type = 'file' (private storage object path)
  file_name text,
  tags text[] not null default '{}',
  created_by uuid references profiles(id),
  created_at timestamptz not null default now()
);
-- One row per (participant, program, week, task_index) — a task is
-- only "done" for progress-tracking purposes once status='approved';
-- see dashboard.py, which checks this table instead of `progress`
-- for any task flagged upload_required.
create table task_submissions (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references organizations(id),
  participant_id uuid not null references profiles(id),
  program_id uuid not null references programs(id),
  week int not null,
  task_index int not null,
  file_path text not null,      -- storage object path (private bucket), not a public URL
  file_name text not null,
  status text not null default 'pending' check (status in ('pending', 'approved', 'needs_revision')),
  reviewer_feedback text default '',
  submitted_at timestamptz not null default now(),
  reviewed_at timestamptz,
  unique (participant_id, program_id, week, task_index)
);

-- ═══════════════════════════════════════════════════════════════
-- Helper functions — read the caller's role/org straight from
-- their own profile row. Every RLS policy below calls these
-- instead of repeating the subquery.
-- ═══════════════════════════════════════════════════════════════

create or replace function auth_role() returns text as $$
  select role from profiles where id = auth.uid();
$$ language sql stable security definer;

create or replace function auth_org_id() returns uuid as $$
  select org_id from profiles where id = auth.uid();
$$ language sql stable security definer;

create or replace function is_super_admin() returns boolean as $$
  select auth_role() = 'super_admin';
$$ language sql stable;

-- ═══════════════════════════════════════════════════════════════
-- Enable RLS on every tenant-scoped table
-- ═══════════════════════════════════════════════════════════════

alter table organizations enable row level security;
alter table profiles enable row level security;
alter table payment_codes enable row level security;
alter table programs enable row level security;
alter table program_content enable row level security;
alter table progress enable row level security;
alter table reflections enable row level security;
alter table last_active enable row level security;
alter table task_submissions enable row level security;
alter table resources enable row level security;

-- ── organizations ─────────────────────────────────────────────
create policy "super_admin sees all orgs" on organizations
  for select using (is_super_admin());

create policy "org members see own org" on organizations
  for select using (id = auth_org_id());

create policy "org_admin updates own org" on organizations
  for update using (id = auth_org_id() and auth_role() = 'org_admin');

create policy "anyone can insert an org at signup" on organizations
  for insert with check (true);   -- org creation happens pre-auth-session; tightened via a signup RPC in practice

-- ── profiles ──────────────────────────────────────────────────
create policy "user reads own profile" on profiles
  for select using (id = auth.uid());

create policy "org_admin reads org profiles" on profiles
  for select using (org_id = auth_org_id() and auth_role() = 'org_admin');

create policy "super_admin reads all profiles" on profiles
  for select using (is_super_admin());

create policy "user inserts own profile at signup" on profiles
  for insert with check (id = auth.uid());

-- ── payment_codes ─────────────────────────────────────────────
create policy "org_admin manages own codes" on payment_codes
  for all using (org_id = auth_org_id() and auth_role() = 'org_admin');

create policy "super_admin manages all codes" on payment_codes
  for all using (is_super_admin());

-- participants need to check a code's validity at registration time,
-- before they have a profile/org_id — handled via a SECURITY DEFINER
-- RPC (see schema notes below), not a direct table policy.

-- ── programs ──────────────────────────────────────────────────
create policy "org sees own programs" on programs
  for select using (org_id = auth_org_id());

create policy "org_admin manages own programs" on programs
  for insert with check (org_id = auth_org_id() and auth_role() = 'org_admin');

create policy "org_admin updates own programs" on programs
  for update using (org_id = auth_org_id() and auth_role() = 'org_admin');

create policy "super_admin sees all programs" on programs
  for select using (is_super_admin());

-- ── program_content ───────────────────────────────────────────
create policy "org sees own program content" on program_content
  for select using (org_id = auth_org_id());

create policy "org_admin writes own program content" on program_content
  for insert with check (org_id = auth_org_id() and auth_role() = 'org_admin');

create policy "org_admin updates own program content" on program_content
  for update using (org_id = auth_org_id() and auth_role() = 'org_admin');

create policy "org_admin deletes own program content" on program_content
  for delete using (org_id = auth_org_id() and auth_role() = 'org_admin');

-- ── progress ──────────────────────────────────────────────────
create policy "participant manages own progress" on progress
  for all using (participant_id = auth.uid());

create policy "org_admin views org progress" on progress
  for select using (org_id = auth_org_id() and auth_role() = 'org_admin');

create policy "super_admin views all progress" on progress
  for select using (is_super_admin());

-- ── reflections ───────────────────────────────────────────────
create policy "participant manages own reflections" on reflections
  for all using (participant_id = auth.uid());

create policy "org_admin views + gives feedback on org reflections" on reflections
  for select using (org_id = auth_org_id() and auth_role() = 'org_admin');

create policy "org_admin updates feedback field" on reflections
  for update using (org_id = auth_org_id() and auth_role() = 'org_admin');

-- ── last_active ───────────────────────────────────────────────
create policy "participant writes own heartbeat" on last_active
  for insert with check (participant_id = auth.uid());

create policy "participant updates own heartbeat" on last_active
  for update using (participant_id = auth.uid());

create policy "org_admin views org heartbeats" on last_active
  for select using (org_id = auth_org_id() and auth_role() = 'org_admin');

-- ── task_submissions ─────────────────────────────────────────
create policy "participant manages own submissions" on task_submissions
  for all using (participant_id = auth.uid())
  with check (participant_id = auth.uid());

create policy "org_admin views org submissions" on task_submissions
  for select using (org_id = auth_org_id() and auth_role() = 'org_admin');

create policy "org_admin reviews org submissions" on task_submissions
  for update using (org_id = auth_org_id() and auth_role() = 'org_admin');

-- ── storage: task-submissions bucket ────────────────────────
-- Create the bucket itself via the Supabase dashboard/CLI (private,
-- not public) — RLS below assumes object paths of the form
-- "{org_id}/{participant_id}/{program_id}_{week}_{task_index}_{filename}".
create policy "participant manages own storage folder" on storage.objects
  for all using (
    bucket_id = 'task-submissions'
    and (storage.foldername(name))[1] = auth_org_id()::text
    and (storage.foldername(name))[2] = auth.uid()::text
  )
  with check (
    bucket_id = 'task-submissions'
    and (storage.foldername(name))[1] = auth_org_id()::text
    and (storage.foldername(name))[2] = auth.uid()::text
  );

create policy "org_admin reads org storage folder" on storage.objects
  for select using (
    bucket_id = 'task-submissions'
    and (storage.foldername(name))[1] = auth_org_id()::text
    and auth_role() = 'org_admin'
  );

-- ── resources ────────────────────────────────────────────────
-- Any org member can browse the library; only org_admin can curate it.
create policy "org members view org resources" on resources
  for select using (org_id = auth_org_id());

create policy "org_admin adds resources" on resources
  for insert with check (org_id = auth_org_id() and auth_role() = 'org_admin');

create policy "org_admin updates resources" on resources
  for update using (org_id = auth_org_id() and auth_role() = 'org_admin');

create policy "org_admin deletes resources" on resources
  for delete using (org_id = auth_org_id() and auth_role() = 'org_admin');

-- ── storage: org-resources bucket ───────────────────────────
-- Create this bucket in the Supabase dashboard too (private).
-- Path convention: "{org_id}/{resource_id}_{filename}" — unlike
-- task-submissions, ANY org member can read (resources are meant
-- to be shared org-wide), but only org_admin can write.
create policy "org members read org resource files" on storage.objects
  for select using (
    bucket_id = 'org-resources'
    and (storage.foldername(name))[1] = auth_org_id()::text
  );

create policy "org_admin manages org resource files" on storage.objects
  for all using (
    bucket_id = 'org-resources'
    and (storage.foldername(name))[1] = auth_org_id()::text
    and auth_role() = 'org_admin'
  )
  with check (
    bucket_id = 'org-resources'
    and (storage.foldername(name))[1] = auth_org_id()::text
    and auth_role() = 'org_admin'
  );

-- ═══════════════════════════════════════════════════════════════
-- Notes
-- ═══════════════════════════════════════════════════════════════
-- 1. org signup and participant registration (joining via org_code)
--    both need to happen BEFORE the person has a session tied to
--    an org — use two SECURITY DEFINER RPC functions for these two
--    flows specifically (create_organization_and_admin, join_org_with_code)
--    so they can safely bypass the chicken-and-egg RLS problem
--    without opening the tables themselves. See utils/db.py for the
--    Python side of this.
-- 2. Streamlit must use the ANON key + call auth.sign_in_with_password()
--    per session, then reuse that authenticated client for the rest of
--    the session's queries. Using the SERVICE_ROLE key anywhere in the
--    request path bypasses every policy above.
