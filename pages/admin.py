import streamlit as st
from utils.db import (
    get_current_profile, logout, get_all_programs, create_program, delete_program,
    set_active_program, get_active_program, get_active_week, set_active_week,
    get_program_weeks, save_program_week, delete_week_from_program,
    get_prompt, set_prompt, get_all_participants, get_last_active_map,
    get_all_reflections, save_feedback, wipe_all_progress,
    create_payment_codes, get_org_payment_codes, get_my_organization,
)
from utils.notify import build_whatsapp_link
from utils.theme import page_header, subheading


def _flash(key: str, kind: str, msg: str):
    st.session_state[f"_flash_{key}"] = (kind, msg)


def _show_flash(key: str):
    fkey = f"_flash_{key}"
    if fkey in st.session_state:
        kind, msg = st.session_state.pop(fkey)
        getattr(st, kind)(msg)


def show():
    profile = get_current_profile()
    if not profile:
        st.error("Session expired. Please log in again.")
        st.stop()

    org_id = profile["org_id"]

    col1, col2 = st.columns([5, 1])
    with col1:
        page_header("🧩 Cohort admin", f"Logged in as {profile['full_name']}")
    with col2:
        st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
        if st.button("Log out"):
            logout()
            st.rerun()

    org = get_my_organization(org_id)
    if org:
        st.markdown(f"""
<div style="background:rgba(0,180,216,0.08);border:1px solid #00B4D8;
            border-radius:10px;padding:14px 18px;margin:4px 0 20px;
            display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;">
  <div>
    <span style="color:#8BA0B8;font-size:0.8rem;">Your organization code — share this with participants</span><br>
    <span style="font-family:'DM Mono',monospace;font-size:1.3rem;font-weight:700;color:#00B4D8;
                 letter-spacing:0.08em;">{org['org_code']}</span>
  </div>
  <div style="color:#4A6080;font-size:0.75rem;">{org['name']}</div>
</div>
""", unsafe_allow_html=True)

    tab_programs, tab_content, tab_members, tab_reflections, tab_codes = st.tabs(
        ["📚 Programs", "📝 Week content", "👥 Members", "💬 Reflections", "🔑 Payment codes"]
    )

    # ═══════════════════════════════════════════════════════════
    # Programs
    # ═══════════════════════════════════════════════════════════
    with tab_programs:
        _show_flash("programs")
        programs = get_all_programs(org_id)

        subheading("Create a new program", color="var(--teal)")
        with st.form("create_program_form"):
            name = st.text_input("Program name")
            unit_label = st.text_input("Unit label", value="Week", help="e.g. 'Week', 'Module', 'Sprint'")
            submitted = st.form_submit_button("Create program")
        if submitted and name.strip():
            create_program(org_id, name.strip(), unit_label.strip() or "Week")
            _flash("programs", "success", f"Program '{name}' created.")
            st.rerun()

        st.divider()
        subheading("Your programs", color="var(--gold)")
        if not programs:
            st.info("No programs yet — create one above.")
        for p in programs:
            with st.expander(f"{'🟢 ' if p['is_active'] else ''}{p['name']} ({p['unit_label']})"):
                st.write(f"Active week: **{p['active_week']}**")
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    if not p["is_active"] and st.button("Set as active program", key=f"activate_{p['id']}"):
                        set_active_program(org_id, p["id"])
                        st.rerun()
                with col_b:
                    new_week = st.number_input("Set active week", min_value=1, value=p["active_week"],
                                               key=f"week_input_{p['id']}")
                    if st.button("Update active week", key=f"update_week_{p['id']}"):
                        set_active_week(p["id"], int(new_week))
                        _flash("programs", "success", "Active week updated.")
                        st.rerun()
                with col_c:
                    if st.button("Delete program", key=f"delete_{p['id']}", type="secondary"):
                        delete_program(p["id"])
                        _flash("programs", "warning", f"Program '{p['name']}' deleted.")
                        st.rerun()

    # ═══════════════════════════════════════════════════════════
    # Week content editor
    # ═══════════════════════════════════════════════════════════
    with tab_content:
        _show_flash("content")
        programs = get_all_programs(org_id)
        if not programs:
            st.info("Create a program first.")
        else:
            program_names = {p["id"]: p["name"] for p in programs}
            selected_pid = st.selectbox("Program", list(program_names.keys()),
                                        format_func=lambda pid: program_names[pid])

            weeks = get_program_weeks(selected_pid)
            existing_week_nums = sorted(weeks.keys())
            week_num = st.number_input("Week / unit number", min_value=1,
                                       value=(max(existing_week_nums) + 1) if existing_week_nums else 1)

            current = weeks.get(int(week_num), {"title": "", "theme": "", "materials": [], "tasks": []})

            with st.form(f"content_form_{week_num}"):
                title = st.text_input("Title", value=current["title"])
                theme = st.text_input("Theme", value=current["theme"])

                st.caption("Materials (one per line, format: `type|label`, e.g. `video|Intro to prompting`)")
                materials_raw = st.text_area(
                    "Materials", height=100,
                    value="\n".join(f"{m['type']}|{m['label']}" for m in current["materials"])
                )

                st.caption("Tasks (one per line)")
                tasks_raw = st.text_area("Tasks", height=120, value="\n".join(current["tasks"]))

                prompt_val = st.text_area(
                    "Reflection prompt (shown once all tasks for this week are done)",
                    value=get_prompt(selected_pid, int(week_num)), height=80
                )

                save_btn = st.form_submit_button("Save week content")

            if save_btn:
                materials = []
                for line in materials_raw.splitlines():
                    if "|" in line:
                        t, label = line.split("|", 1)
                        materials.append({"type": t.strip(), "label": label.strip()})
                tasks = [t.strip() for t in tasks_raw.splitlines() if t.strip()]

                save_program_week(org_id, selected_pid, int(week_num), title.strip(),
                                  theme.strip(), materials, tasks)
                set_prompt(org_id, selected_pid, int(week_num), prompt_val)
                _flash("content", "success", f"Week {int(week_num)} saved.")
                st.rerun()

            if int(week_num) in weeks:
                if st.button("Delete this week", type="secondary"):
                    delete_week_from_program(selected_pid, int(week_num))
                    _flash("content", "warning", f"Week {int(week_num)} deleted.")
                    st.rerun()

    # ═══════════════════════════════════════════════════════════
    # Members
    # ═══════════════════════════════════════════════════════════
    with tab_members:
        members = get_all_participants(org_id)
        last_active = get_last_active_map(org_id)

        subheading(f"Members ({len(members)})", color="var(--teal)")
        if not members:
            st.info("No participants have joined yet. Share your organization code with them.")
        for m in members:
            la = last_active.get(m["id"], "never")
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{m['full_name']}**")
                    st.caption(f"{m['email']} · {m.get('whatsapp','')}")
                    st.caption(f"Last active: {la}")
                with col2:
                    link = build_whatsapp_link(m.get("whatsapp", ""),
                                               f"Hi {m['full_name'].split()[0]}, checking in on your progress!")
                    if link:
                        st.link_button("WhatsApp", link, width='stretch')

        active_program = get_active_program(org_id)
        if active_program:
            st.divider()
            if st.button("⚠️ Wipe all progress for this program", type="secondary"):
                st.session_state["_confirm_wipe"] = True
            if st.session_state.get("_confirm_wipe"):
                st.warning("This deletes ALL progress and reflections for the active program. This can't be undone.")
                if st.button("Yes, permanently wipe it"):
                    wipe_all_progress(org_id, active_program["id"])
                    st.session_state.pop("_confirm_wipe", None)
                    st.success("Progress wiped.")
                    st.rerun()

    # ═══════════════════════════════════════════════════════════
    # Reflections review
    # ═══════════════════════════════════════════════════════════
    with tab_reflections:
        active_program = get_active_program(org_id)
        if not active_program:
            st.info("No active program set.")
        else:
            reflections = get_all_reflections(org_id, active_program["id"])
            if not reflections:
                st.info("No reflections submitted yet.")
            for r in sorted(reflections, key=lambda x: (x["week"], x.get("profiles", {}).get("full_name", ""))):
                person = r.get("profiles") or {}
                with st.expander(f"Week {r['week']} — {person.get('full_name', 'Unknown')}"):
                    st.write(r["response"])
                    fb_key = f"fb_{r['id']}"
                    feedback_val = st.text_area("Your feedback", value=r.get("feedback") or "", key=fb_key)
                    if st.button("Save feedback", key=f"save_{r['id']}"):
                        save_feedback(r["id"], feedback_val)
                        st.success("Feedback saved.")
                        st.rerun()

    # ═══════════════════════════════════════════════════════════
    # Payment codes
    # ═══════════════════════════════════════════════════════════
    with tab_codes:
        subheading("Generate payment/access codes", color="var(--gold)")
        st.caption("Optional — leave this empty if participants can join with just your organization code.")
        with st.form("add_codes_form", clear_on_submit=True):
            codes_raw = st.text_area("New codes (one per line)", height=100)
            submitted = st.form_submit_button("Add codes")

        if submitted:
            if not codes_raw.strip():
                st.warning("Enter at least one code first.")
            else:
                try:
                    create_payment_codes(org_id, codes_raw.splitlines())
                except Exception as e:
                    st.error(f"Couldn't add codes: {e}")
                else:
                    st.success("Codes added.")
                    st.rerun()

        st.divider()
        codes = get_org_payment_codes(org_id)
        used = sum(1 for c in codes if c["used"])
        st.write(f"**{len(codes)}** total codes, **{used}** used, **{len(codes) - used}** remaining.")

        # Deliberately NOT using st.dataframe() here — it routes through
        # pandas/pyarrow for Arrow serialization, and that native code path
        # has been unstable on some very new Python builds (segfaults seen
        # on Python 3.14 + pyarrow 25.x). A plain markdown table avoids that
        # dependency entirely for what's just a short list of codes.
        if codes:
            rows = "".join(
                f"| `{c['code']}` | {'✅ used' if c['used'] else '⬜ available'} |\n"
                for c in codes
            )
            st.markdown(f"| Code | Status |\n|---|---|\n{rows}")
        else:
            st.caption("No codes yet.")
