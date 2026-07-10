# Crea8it Labs — Multi-tenant (Supabase edition)

This is the multi-tenant rebuild of Crea8it: instead of one Google
Sheet running one cohort, any number of organizations can each run
their own program, with you (the platform owner) holding oversight
across all of them.

## Three roles

- **super_admin** (you) — sees every organization, member counts,
  can suspend/reactivate any org. Lands on `pages/super_admin.py`.
- **org_admin** (a cohort operator) — manages their own programs,
  week content, members, reflections, and payment codes. Lands on
  `pages/admin.py`. Scoped entirely to their own `org_id` — both by
  the app code and by Postgres Row-Level Security.
- **participant** — joins an org via its `org_code`, works through
  weekly tasks and reflections. Lands on `pages/dashboard.py`.

## Setup

1. **Create a Supabase project** at supabase.com if you don't have one.
2. **Run the SQL**, in this order, in the Supabase SQL editor:
   - `schema.sql` (tables + RLS policies)
   - `rpc_functions.sql` (org signup / join-by-code logic)
3. **Copy secrets**: `.streamlit/secrets.toml.example` →
   `.streamlit/secrets.toml`, fill in your project's URL and **anon**
   key (Project Settings → API). Never use the service_role key here.
4. **Install dependencies**: `pip install -r requirements.txt`
5. **Bootstrap yourself as super_admin**:
   - Run the app, use "Start your own cohort" OR just sign up any
     way that creates an `auth.users` row for you (e.g. temporarily
     use the join flow, then fix the role after).
   - In the Supabase SQL editor, run:
     ```sql
     update profiles set role = 'super_admin', org_id = null
     where email = 'you@example.com';
     ```
6. **Run it**: `streamlit run app.py`

## What changed from the original single-tenant app

- `utils/sheets.py` → `utils/db.py` (Supabase, not Google Sheets)
- `utils/auth.py` → now a thin wrapper; real auth is Supabase Auth,
  not hand-rolled PBKDF2. Every session carries a real user JWT, so
  RLS policies actually enforce org isolation at the database level.
- `pages/register.py` now has three flows: `show_join()` (participant
  joins via org_code), `show_org_signup()` (new cohort operator
  creates an org), `show_login()` (everyone).
- New `pages/super_admin.py` — your oversight dashboard.
- `pages/dashboard.py` and `pages/admin.py` — same UI/UX as before,
  data calls swapped to the new multi-tenant functions.
- `utils/theme.py` and `utils/notify.py` are unchanged — no data
  dependency, so nothing to migrate there.

## Notes / things to double check before going live

- The org-signup and payment-code flows are functional but not yet
  wired to actual payment collection (Flutterwave, etc.) — add that
  the same way BizTrack-OS does it, gating org `plan` upgrades.
- Password reset for participants isn't wired up yet — Supabase Auth
  supports this out of the box (`client.auth.reset_password_email`),
  worth adding to `register.py`.
- The avatar/social-proof strip from the original landing page was
  left out of the rebuilt `register.py` to keep this pass focused on
  the data-layer migration — drop your existing avatar HTML back in
  if you want it.
