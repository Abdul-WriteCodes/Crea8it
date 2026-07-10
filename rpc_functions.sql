-- ═══════════════════════════════════════════════════════════════
-- RPC functions — the only sanctioned bypass of RLS.
-- These run as the function OWNER (security definer), not the
-- caller, so they can safely create the org_id-tagged profile row
-- for a user during signup, before that user has any org_id yet.
-- ═══════════════════════════════════════════════════════════════

-- ── org_code generator (prefix from name + random digits) ──────
create or replace function generate_org_code(org_name text) returns text as $$
declare
  prefix text;
  suffix text;
  candidate text;
begin
  prefix := upper(regexp_replace(substring(org_name from 1 for 5), '[^A-Za-z]', '', 'g'));
  if length(prefix) < 3 then
    prefix := rpad(prefix, 3, 'X');
  end if;
  loop
    suffix := lpad(floor(random() * 10000)::text, 4, '0');
    candidate := prefix || suffix;
    exit when not exists (select 1 from organizations where org_code = candidate);
  end loop;
  return candidate;
end;
$$ language plpgsql security definer;

-- ── Step 1 of org signup: create the org + org_admin profile ───
-- Called right after auth.sign_up() succeeds, using the new user's id.
create or replace function create_organization_and_admin(
  p_user_id uuid,
  p_org_name text,
  p_admin_name text,
  p_admin_whatsapp text,
  p_admin_email text
) returns table (org_id uuid, org_code text) as $$
declare
  new_org_id uuid;
  new_code text;
begin
  -- guard: this user must not already have a profile
  if exists (select 1 from profiles where id = p_user_id) then
    raise exception 'User already has a profile';
  end if;

  new_code := generate_org_code(p_org_name);

  insert into organizations (name, org_code, admin_name, admin_whatsapp, admin_email)
  values (p_org_name, new_code, p_admin_name, p_admin_whatsapp, p_admin_email)
  returning id into new_org_id;

  insert into profiles (id, org_id, role, full_name, whatsapp, email)
  values (p_user_id, new_org_id, 'org_admin', p_admin_name, p_admin_whatsapp, p_admin_email);

  return query select new_org_id, new_code;
end;
$$ language plpgsql security definer;

-- ── Step 1 of participant signup: join an org via its code ──────
-- Called right after auth.sign_up() succeeds, using the new user's id.
-- p_payment_code is optional — pass null if the org doesn't require one.
create or replace function join_org_with_code(
  p_user_id uuid,
  p_org_code text,
  p_full_name text,
  p_whatsapp text,
  p_email text,
  p_payment_code text default null
) returns uuid as $$
declare
  target_org_id uuid;
  code_row payment_codes%rowtype;
begin
  if exists (select 1 from profiles where id = p_user_id) then
    raise exception 'User already has a profile';
  end if;

  select id into target_org_id from organizations
    where org_code = upper(p_org_code) and is_active = true;

  if target_org_id is null then
    raise exception 'Invalid or inactive organization code';
  end if;

  if p_payment_code is not null then
    select * into code_row from payment_codes
      where org_id = target_org_id and code = p_payment_code and used = false;
    if not found then
      raise exception 'Invalid or already-used payment code';
    end if;
    update payment_codes set used = true where id = code_row.id;
  end if;

  insert into profiles (id, org_id, role, full_name, whatsapp, email)
  values (p_user_id, target_org_id, 'participant', p_full_name, p_whatsapp, p_email);

  return target_org_id;
end;
$$ language plpgsql security definer;

-- ── Bootstrap: you, the platform owner, as super_admin ──────────
-- Run manually once, after creating your own auth.users account
-- through Supabase Auth (sign up normally first, then run this
-- with your resulting user id).
-- insert into profiles (id, org_id, role, full_name, email)
-- values ('<your-auth-user-id>', null, 'super_admin', 'Abdul', 'you@example.com');
