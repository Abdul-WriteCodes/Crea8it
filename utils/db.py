"""
utils/db.py — Supabase data layer for Crea8it (multi-tenant)

Replaces utils/sheets.py entirely. Function shapes are kept as close
as possible to the original sheets.py so pages/*.py changes are
mostly import swaps + threading org_id/program_id through.

IMPORTANT: uses the ANON key + a per-session authenticated client
(sign_in_with_password). Never use the SERVICE_ROLE key here — doing
so bypasses every RLS policy in schema.sql.
"""

from __future__ import annotations
import streamlit as st
from supabase import create_client, Client


# ═══════════════════════════════════════════════════════════════
# Client bootstrap
# ═══════════════════════════════════════════════════════════════

@st.cache_resource
def _base_client() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"])


def get_client() -> Client:
    return st.session_state.get("sb_client", _base_client())


# ═══════════════════════════════════════════════════════════════
# Auth: sign up / sign in / sign out
# ═══════════════════════════════════════════════════════════════

def sign_up(email: str, password: str) -> str:
    client = _base_client()
    res = client.auth.sign_up({"email": email, "password": password})
    if res.user is None:
        raise Exception("Sign up failed — check email/password requirements.")
    return res.user.id


def sign_in(email: str, password: str) -> Client:
    client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"])
    res = client.auth.sign_in_with_password({"email": email, "password": password})
    if res.user is None:
        raise Exception("Invalid email or password.")
    st.session_state["sb_client"] = client
    st.session_state["user_id"] = res.user.id
    return client


def sign_out():
    client = get_client()
    try:
        client.auth.sign_out()
    finally:
        for key in list(st.session_state.keys()):
            st.session_state.pop(key, None)


def is_logged_in() -> bool:
    return st.session_state.get("user_id") is not None


# ═══════════════════════════════════════════════════════════════
# Profile / role resolution
# ═══════════════════════════════════════════════════════════════

def get_current_profile() -> dict | None:
    if "profile" in st.session_state:
        return st.session_state["profile"]
    user_id = st.session_state.get("user_id")
    if not user_id:
        return None
    client = get_client()
    # Deliberately NOT using .single() here — that raises a hard APIError
    # when zero rows come back (e.g. a signup that got interrupted between
    # creating the auth user and creating the profile row). We want a
    # graceful None instead of crashing the whole app on that edge case.
    res = client.table("profiles").select("*").eq("id", user_id).execute()
    if not res.data:
        return None
    st.session_state["profile"] = res.data[0]
    return res.data[0]


def require_role(*allowed_roles: str) -> dict:
    profile = get_current_profile()
    if not profile or profile["role"] not in allowed_roles:
        st.error("You don't have access to this page.")
        st.stop()
    return profile


def logout():
    sign_out()


def get_current_participant() -> dict | None:
    """Alias kept for parity with the old sheets.py-based auth.py."""
    return get_current_profile()


# ═══════════════════════════════════════════════════════════════
# Org signup (org_admin path) + participant join-by-code
# ═══════════════════════════════════════════════════════════════

def register_organization(org_name: str, admin_name: str, admin_whatsapp: str,
                           admin_email: str, password: str) -> dict:
    user_id = sign_up(admin_email, password)
    client = sign_in(admin_email, password)
    try:
        res = client.rpc("create_organization_and_admin", {
            "p_user_id": user_id,
            "p_org_name": org_name,
            "p_admin_name": admin_name,
            "p_admin_whatsapp": admin_whatsapp,
            "p_admin_email": admin_email,
        }).execute()
    except Exception:
        # Don't leave a logged-in session with no profile behind —
        # that's exactly what caused the crash-on-reload bug.
        sign_out()
        raise
    st.session_state.pop("profile", None)
    row = res.data[0]
    return {"org_id": row["org_id"], "org_code": row["org_code"]}


def is_valid_org_code(org_code: str) -> bool:
    """Uses the check_org_code_valid RPC — a direct table query here would
    always return zero rows for anonymous (not-yet-signed-up) visitors,
    since RLS correctly blocks anon reads of the organizations table."""
    client = get_client()
    res = client.rpc("check_org_code_valid", {"p_org_code": org_code.strip()}).execute()
    return bool(res.data)


def join_organization(org_code: str, full_name: str, whatsapp: str, email: str,
                       password: str, payment_code: str | None = None) -> str:
    user_id = sign_up(email, password)
    client = sign_in(email, password)
    try:
        res = client.rpc("join_org_with_code", {
            "p_user_id": user_id,
            "p_org_code": org_code.strip().upper(),
            "p_full_name": full_name,
            "p_whatsapp": whatsapp,
            "p_email": email,
            "p_payment_code": payment_code,
        }).execute()
    except Exception:
        sign_out()
        raise
    st.session_state.pop("profile", None)
    return res.data


# ═══════════════════════════════════════════════════════════════
# Payment codes (org_admin manages these for their own org)
# ═══════════════════════════════════════════════════════════════

def create_payment_codes(org_id: str, codes: list[str]):
    client = get_client()
    rows = [{"org_id": org_id, "code": c.strip()} for c in codes if c.strip()]
    if rows:
        # upsert, not insert: re-submitting the same codes (e.g. a double
        # click, or the text area still holding old text after a rerun)
        # would otherwise hit the (org_id, code) unique constraint and
        # raise an uncaught error.
        client.table("payment_codes").upsert(rows, on_conflict="org_id,code").execute()


def get_org_payment_codes(org_id: str) -> list[dict]:
    client = get_client()
    res = client.table("payment_codes").select("*").eq("org_id", org_id).execute()
    return res.data


# ═══════════════════════════════════════════════════════════════
# Programs
# ═══════════════════════════════════════════════════════════════

def get_all_programs(org_id: str) -> list[dict]:
    client = get_client()
    res = (client.table("programs").select("*").eq("org_id", org_id)
           .order("created_at").execute())
    return res.data


def create_program(org_id: str, name: str, unit_label: str = "Week") -> dict:
    client = get_client()
    res = client.table("programs").insert({
        "org_id": org_id, "name": name, "unit_label": unit_label,
    }).execute()
    return res.data[0]


def delete_program(program_id: str):
    client = get_client()
    client.table("programs").delete().eq("id", program_id).execute()


def set_active_program(org_id: str, program_id: str):
    """Marks one program as the org's active one, deactivating the rest."""
    client = get_client()
    client.table("programs").update({"is_active": False}).eq("org_id", org_id).execute()
    client.table("programs").update({"is_active": True}).eq("id", program_id).execute()


def get_active_program(org_id: str) -> dict | None:
    client = get_client()
    res = (client.table("programs").select("*")
           .eq("org_id", org_id).eq("is_active", True)
           .limit(1).execute())
    return res.data[0] if res.data else None


def get_active_week(program_id: str) -> int:
    client = get_client()
    res = client.table("programs").select("active_week").eq("id", program_id).single().execute()
    return res.data["active_week"] if res.data else 1


def set_active_week(program_id: str, week: int):
    client = get_client()
    client.table("programs").update({"active_week": week}).eq("id", program_id).execute()


# ═══════════════════════════════════════════════════════════════
# Program content (title / theme / materials / tasks / prompt)
# ═══════════════════════════════════════════════════════════════

def get_program_weeks(program_id: str) -> dict:
    """Same shape as the old sheets.py: {week: {title, theme, materials[], tasks[]}}"""
    client = get_client()
    res = (client.table("program_content").select("*")
           .eq("program_id", program_id)
           .order("week").order("order_index").execute())

    weeks: dict = {}
    for row in res.data:
        w = row["week"]
        if w not in weeks:
            weeks[w] = {"title": "", "theme": "", "materials": [], "tasks": []}
        rtype, value, extra = row["type"], row["value"], row.get("extra", "")
        if rtype == "title":
            weeks[w]["title"] = value
        elif rtype == "theme":
            weeks[w]["theme"] = value
        elif rtype == "material":
            weeks[w]["materials"].append({"type": extra or "article", "label": value})
        elif rtype == "task":
            weeks[w]["tasks"].append(value)
    return weeks


def save_program_week(org_id: str, program_id: str, week: int, title: str, theme: str,
                       materials: list[dict], tasks: list[str]):
    client = get_client()
    (client.table("program_content").delete()
     .eq("program_id", program_id).eq("week", week)
     .in_("type", ["title", "theme", "material", "task"]).execute())

    rows = [
        {"org_id": org_id, "program_id": program_id, "week": week, "type": "title", "value": title, "order_index": 0},
        {"org_id": org_id, "program_id": program_id, "week": week, "type": "theme", "value": theme, "order_index": 0},
    ]
    for idx, mat in enumerate(materials):
        rows.append({"org_id": org_id, "program_id": program_id, "week": week, "type": "material",
                     "value": mat.get("label", ""), "extra": mat.get("type", "article"), "order_index": idx})
    for idx, task in enumerate(tasks):
        rows.append({"org_id": org_id, "program_id": program_id, "week": week, "type": "task",
                     "value": task, "order_index": idx})

    client.table("program_content").insert(rows).execute()


def delete_week_from_program(program_id: str, week: int):
    client = get_client()
    client.table("program_content").delete().eq("program_id", program_id).eq("week", week).execute()


def get_prompt(program_id: str, week: int) -> str:
    client = get_client()
    res = (client.table("program_content").select("value")
           .eq("program_id", program_id).eq("week", week).eq("type", "prompt")
           .limit(1).execute())
    return res.data[0]["value"] if res.data else ""


def set_prompt(org_id: str, program_id: str, week: int, prompt: str):
    client = get_client()
    client.table("program_content").delete().eq("program_id", program_id).eq("week", week).eq("type", "prompt").execute()
    if prompt.strip():
        client.table("program_content").insert({
            "org_id": org_id, "program_id": program_id, "week": week,
            "type": "prompt", "value": prompt.strip(),
        }).execute()


# ═══════════════════════════════════════════════════════════════
# Progress
# ═══════════════════════════════════════════════════════════════

def get_progress(participant_id: str, program_id: str) -> dict:
    """Returns {week: [task_index, ...]} for this participant/program."""
    client = get_client()
    res = (client.table("progress").select("week, task_index")
           .eq("participant_id", participant_id).eq("program_id", program_id).execute())
    out: dict = {}
    for row in res.data:
        out.setdefault(row["week"], []).append(row["task_index"])
    return out


def mark_task_done(org_id: str, participant_id: str, program_id: str, week: int, task_index: int):
    client = get_client()
    client.table("progress").upsert({
        "org_id": org_id, "participant_id": participant_id, "program_id": program_id,
        "week": week, "task_index": task_index,
    }, on_conflict="participant_id,program_id,week,task_index").execute()


def get_all_progress(org_id: str) -> list[dict]:
    client = get_client()
    res = client.table("progress").select("*").eq("org_id", org_id).execute()
    return res.data


def wipe_all_progress(org_id: str, program_id: str):
    client = get_client()
    client.table("progress").delete().eq("org_id", org_id).eq("program_id", program_id).execute()
    client.table("reflections").delete().eq("org_id", org_id).eq("program_id", program_id).execute()


def get_week_completion_stats(program_id: str, week: int, task_count: int) -> tuple[int, int]:
    client = get_client()
    res = client.table("progress").select("participant_id").eq("program_id", program_id).eq("week", week).execute()
    counts: dict = {}
    for row in res.data:
        counts[row["participant_id"]] = counts.get(row["participant_id"], 0) + 1
    finished = sum(1 for c in counts.values() if c >= task_count)
    total = len(counts)
    return finished, total


# ═══════════════════════════════════════════════════════════════
# Reflections & feedback
# ═══════════════════════════════════════════════════════════════

def get_reflection(participant_id: str, program_id: str, week: int) -> dict | None:
    client = get_client()
    res = (client.table("reflections").select("*")
           .eq("participant_id", participant_id).eq("program_id", program_id).eq("week", week)
           .limit(1).execute())
    return res.data[0] if res.data else None


def submit_reflection(org_id: str, participant_id: str, program_id: str, week: int, response: str):
    client = get_client()
    client.table("reflections").upsert({
        "org_id": org_id, "participant_id": participant_id, "program_id": program_id,
        "week": week, "response": response,
    }, on_conflict="participant_id,program_id,week").execute()


def get_feedback(participant_id: str, program_id: str, week: int) -> str:
    r = get_reflection(participant_id, program_id, week)
    return (r or {}).get("feedback", "") or ""


def save_feedback(reflection_id: str, feedback: str):
    client = get_client()
    client.table("reflections").update({"feedback": feedback}).eq("id", reflection_id).execute()


def get_all_reflections(org_id: str, program_id: str) -> list[dict]:
    client = get_client()
    res = (client.table("reflections").select("*, profiles(full_name, whatsapp, email)")
           .eq("org_id", org_id).eq("program_id", program_id).execute())
    return res.data


# ═══════════════════════════════════════════════════════════════
# Participants / members
# ═══════════════════════════════════════════════════════════════

def get_all_participants(org_id: str) -> list[dict]:
    client = get_client()
    res = client.table("profiles").select("*").eq("org_id", org_id).eq("role", "participant").execute()
    return res.data


def get_org_members(org_id: str) -> list[dict]:
    return get_all_participants(org_id)


# ═══════════════════════════════════════════════════════════════
# Last active (heartbeat)
# ═══════════════════════════════════════════════════════════════

def touch_last_active(org_id: str, participant_id: str):
    """Best-effort heartbeat — never let this crash the page it's called
    from. Losing a last-active timestamp is harmless; crashing someone's
    whole dashboard over it is not."""
    try:
        client = get_client()
        client.table("last_active").upsert({
            "org_id": org_id, "participant_id": participant_id,
        }, on_conflict="participant_id").execute()
    except Exception:
        pass


def get_last_active_map(org_id: str) -> dict:
    client = get_client()
    res = client.table("last_active").select("participant_id, last_active_at").eq("org_id", org_id).execute()
    return {row["participant_id"]: row["last_active_at"] for row in res.data}


# ═══════════════════════════════════════════════════════════════
# Super admin oversight
# ═══════════════════════════════════════════════════════════════

def get_all_organizations() -> list[dict]:
    client = get_client()
    res = client.table("organizations").select("*").execute()
    return res.data


def get_org_stats(org_id: str) -> dict:
    client = get_client()
    members = client.table("profiles").select("id", count="exact").eq("org_id", org_id).eq("role", "participant").execute()
    programs = client.table("programs").select("id", count="exact").eq("org_id", org_id).execute()
    return {"member_count": members.count, "program_count": programs.count}


def get_my_organization(org_id: str) -> dict | None:
    """org_admin's own org record — backed by the 'org members see own org'
    RLS policy, so this only ever returns the caller's own organization."""
    client = get_client()
    res = client.table("organizations").select("*").eq("id", org_id).limit(1).execute()
    return res.data[0] if res.data else None


def suspend_organization(org_id: str, active: bool):
    client = get_client()
    client.table("organizations").update({"is_active": active}).eq("id", org_id).execute()
