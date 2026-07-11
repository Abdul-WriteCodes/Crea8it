import streamlit as st
from utils.db import (
    get_current_profile, logout, get_all_programs, create_program, delete_program,
    set_active_program, get_active_program, get_active_week, set_active_week,
    get_program_weeks, save_program_week, delete_week_from_program,
    get_prompt, set_prompt, get_all_participants, get_last_active_map,
    get_all_reflections, save_feedback, wipe_all_progress,
    create_payment_codes, get_org_payment_codes, get_my_organization,
    get_program_engagement,
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

    org = get_my_organization(org_id)

    col1, col2 = st.columns([5, 1])
    with col1:
        page_header("🧩 Cohort admin", f"Logged in as {profile['full_name']}")
    with col2:
        st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
        if st.button("Log out"):
            logout()
            st.rerun()

    if not org or not org["is_active"]:
        st.markdown("""
<div style="background:rgba(245,166,35,0.08);border:1px solid #F5A623;
            border-radius:10px;padding:20px;margin:8px 0;">
  <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;
              color:#F5A623;margin-bottom:6px;">⏳ Awaiting approval</div>
  <div style="color:#8BA0B8;font-size:0.88rem;line-height:1.6;">
    Your organization has been created, but a Crea8it platform admin
    needs to approve it before you can start building your program or
    inviting participants. This is usually quick — check back shortly,
    or reach out if it's been a while.
  </div>
</div>""", unsafe_allow_html=True)
        return

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

    tab_programs, tab_content, tab_members, tab_engagement, tab_reflections, tab_codes = st.tabs(
        ["📚 Programs", "📝 Week content", "👥 Members", "📊 Engagement", "💬 Reflections", "🔑 Payment codes"]
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
            col_a, col_b = st.columns(2)
            with col_a:
                unit_label = st.text_input("Unit label", value="Week", help="e.g. 'Week', 'Module', 'Sprint'")
            with col_b:
                duration_weeks = st.number_input(
                    "Duration", min_value=1, max_value=52, value=4,
                    help="How many units this program runs for — 1, 2, 6, 12... your call."
                )
            submitted = st.form_submit_button("Create program")
        if submitted and name.strip():
            create_program(org_id, name.strip(), unit_label.strip() or "Week", int(duration_weeks))
            _flash("programs", "success", f"Program '{name}' created — {int(duration_weeks)} {unit_label or 'Week'}(s).")
            st.rerun()

        st.divider()
        subheading("Your programs", color="var(--gold)")
        if not programs:
            st.info("No programs yet — create one above.")
        for p in programs:
            with st.expander(f"{'🟢 ' if p['is_active'] else ''}{p['name']} ({p['unit_label']})"):
                st.write(f"Active week: **{p['active_week']}** of **{p.get('duration_weeks', '—')}**")
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    if not p["is_active"] and st.button("Set as active program", key=f"activate_{p['id']}"):
                        set_active_program(org_id, p["id"])
                        st.rerun()
                with col_b:
                    new_week = st.number_input(
                        "Set active week", min_value=1, max_value=p.get("duration_weeks", 52),
                        value=min(p["active_week"], p.get("duration_weeks", 52)),
                        key=f"week_input_{p['id']}"
                    )
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
            selected_program = next(p for p in programs if p["id"] == selected_pid)

            weeks = get_program_weeks(selected_pid)
            existing_week_nums = sorted(weeks.keys())
            week_num = st.number_input(
                "Week / unit number", min_value=1, max_value=selected_program.get("duration_weeks", 52),
                value=min((max(existing_week_nums) + 1) if existing_week_nums else 1,
                         selected_program.get("duration_weeks", 52))
            )

            current = weeks.get(int(week_num), {"title": "", "theme": "", "materials": [], "tasks": []})

            title = st.text_input("Title", value=current["title"], key=f"title_{week_num}")
            theme = st.text_input("Theme", value=current["theme"], key=f"theme_{week_num}")

            st.caption("Materials — add as many rows as you need. Type is free text: "
                      "'video', 'article', 'portfolio task', anything.")
            materials_df = st.data_editor(
                [{"type": m["type"], "label": m["label"]} for m in current["materials"]] or
                [{"type": "video", "label": ""}],
                num_rows="dynamic",
                key=f"materials_editor_{week_num}",
                column_config={
                    "type": st.column_config.TextColumn("Type", width="small"),
                    "label": st.column_config.TextColumn("Description", width="large"),
                },
                width='stretch',
            )

            st.caption("Tasks — add as many as this week needs, one row each.")
            tasks_df = st.data_editor(
                [{"task": t} for t in current["tasks"]] or [{"task": ""}],
                num_rows="dynamic",
                key=f"tasks_editor_{week_num}",
                column_config={
                    "task": st.column_config.TextColumn("Task description", width="large"),
                },
                width='stretch',
            )

            prompt_val = st.text_area(
                "Reflection prompt (shown once all tasks for this week are done)",
                value=get_prompt(selected_pid, int(week_num)), height=80,
                key=f"prompt_{week_num}"
            )

            if st.button("💾 Save week content", type="primary", key=f"save_{week_num}"):
                materials = [
                    {"type": row["type"].strip(), "label": row["label"].strip()}
                    for row in materials_df
                    if row.get("type", "").strip() and row.get("label", "").strip()
                ]
                tasks = [row["task"].strip() for row in tasks_df if row.get("task", "").strip()]

                if not tasks:
                    st.warning("Add at least one task before saving.")
                else:
                    save_program_week(org_id, selected_pid, int(week_num), title.strip(),
                                      theme.strip(), materials, tasks)
                    set_prompt(org_id, selected_pid, int(week_num), prompt_val)
                    _flash("content", "success",
                          f"Week {int(week_num)} saved — {len(materials)} material(s), {len(tasks)} task(s).")
                    st.rerun()

            if int(week_num) in weeks:
                if st.button("Delete this week", type="secondary", key=f"delete_{week_num}"):
                    delete_week_from_program(selected_pid, int(week_num))
                    _flash("content", "warning", f"Week {int(week_num)} deleted.")
                    st.rerun()

    # ═══════════════════════════════════════════════════════════
    # Engagement
    # ═══════════════════════════════════════════════════════════
    with tab_engagement:
        programs = get_all_programs(org_id)
        if not programs:
            st.info("Create a program first.")
        else:
            program_names = {p["id"]: p["name"] for p in programs}
            eng_pid = st.selectbox("Program", list(program_names.keys()),
                                   format_func=lambda pid: program_names[pid], key="engagement_program_select")

            engagement = get_program_engagement(org_id, eng_pid)

            if not engagement:
                st.info("No participants yet for this program.")
            else:
                total = len(engagement)
                fully_engaged = sum(1 for e in engagement if e["pct"] >= 80)
                avg_pct = round(sum(e["pct"] for e in engagement) / total) if total else 0

                col1, col2, col3 = st.columns(3)
                col1.metric("Participants", total)
                col2.metric("Avg. completion", f"{avg_pct}%")
                col3.metric("Highly engaged (80%+)", fully_engaged)

                st.divider()
                for e in engagement:
                    with st.container(border=True):
                        col_a, col_b = st.columns([3, 2])
                        with col_a:
                            st.write(f"**{e['full_name']}**")
                            st.caption(f"{e['email']} · {e['whatsapp']}")
                            st.caption(f"Last active: {e['last_active']}")
                        with col_b:
                            st.progress(e["pct"] / 100,
                                       text=f"{e['tasks_done']}/{e['tasks_total']} tasks ({e['pct']}%)")
                            st.caption(
                                f"{e['weeks_completed']}/{e['weeks_total']} weeks fully done · "
                                f"{e['reflections_submitted']} reflection(s) submitted"
                            )

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
