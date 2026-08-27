import re
import streamlit as st
from utils.db import (
    get_current_profile, logout, get_all_programs, create_program, delete_program,
    set_active_program, get_active_program, get_active_week, set_active_week,
    get_program_weeks, save_program_week, delete_week_from_program,
    get_prompt, set_prompt, get_all_participants, get_last_active_map,
    get_all_reflections, save_feedback, wipe_all_progress,
    create_payment_codes, get_org_payment_codes, get_my_organization,
    get_program_engagement,
    get_pending_submissions, get_submission_download_url, review_submission,
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

    tab_programs, tab_content, tab_members, tab_engagement, tab_reflections, tab_submissions, tab_codes = st.tabs(
        ["📚 Programs", "📝 Week content", "👥 Members", "📊 Engagement",
         "💬 Reflections", "📎 Submissions", "🔑 Payment codes"]
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
            MATERIAL_TYPES = ["book", "video", "article", "worksheet", "template",
                              "portfolio", "assignment", "podcast", "quiz", "slides", "code", "tool"]

            program_names = {p["id"]: p["name"] for p in programs}
            selected_pid = st.selectbox("Program", list(program_names.keys()),
                                        format_func=lambda pid: program_names[pid])
            selected_program = next(p for p in programs if p["id"] == selected_pid)
            unit_label = selected_program.get("unit_label", "Week")

            weeks = get_program_weeks(selected_pid)
            existing_week_nums = sorted(weeks.keys())
            current_active_week = get_active_week(selected_pid)
            week_num = int(st.number_input(
                f"{unit_label} number", min_value=1, max_value=selected_program.get("duration_weeks", 52),
                value=min((max(existing_week_nums) + 1) if existing_week_nums else 1,
                         selected_program.get("duration_weeks", 52))
            ))

            if week_num == current_active_week:
                st.caption(f"🟢 This is the current active {unit_label.lower()} for {selected_program['name']}.")
            else:
                st.caption(f"Current active {unit_label.lower()}: **{current_active_week}**")

            current = weeks.get(week_num, {"title": "", "theme": "", "materials": [], "tasks": []})

            title = st.text_input("Title", value=current["title"],
                                  placeholder=f"e.g. {unit_label} {week_num}: Getting Started",
                                  key=f"title_{week_num}")
            theme = st.text_input("Subtitle / theme", value=current["theme"],
                                  placeholder="e.g. Understand the landscape and why it matters",
                                  key=f"theme_{week_num}")

            st.markdown("**Materials** (up to 8)")
            ex_mats = current["materials"]
            mat_count = st.number_input("How many materials?", min_value=0, max_value=8,
                                        value=len(ex_mats), key=f"mat_n_{week_num}")
            materials = []
            for m in range(int(mat_count)):
                default_label = ex_mats[m]["label"] if m < len(ex_mats) else ""
                default_type = ex_mats[m]["type"] if m < len(ex_mats) else "article"
                mc1, mc2 = st.columns([3, 1])
                with mc1:
                    ml = st.text_input(f"Material {m+1}", value=default_label,
                                       placeholder="e.g. Watch: Intro video", key=f"mat_lbl_{week_num}_{m}")
                with mc2:
                    idx = MATERIAL_TYPES.index(default_type) if default_type in MATERIAL_TYPES else 0
                    mt = st.selectbox("Type", MATERIAL_TYPES, index=idx, key=f"mat_tp_{week_num}_{m}")
                if ml.strip():
                    materials.append({"label": ml.strip(), "type": mt})

            st.markdown("**Activities / Tasks** (up to 10)")
            st.caption("Add an optional resource link to any task — it becomes clickable on the dashboard. "
                       "Check 'Requires file upload' for tasks that need a doc reviewed before they count as done.")
            ex_tasks = current["tasks"]
            task_count = st.number_input("How many tasks?", min_value=0, max_value=10,
                                         value=len(ex_tasks), key=f"task_n_{week_num}")
            tasks = []
            for t in range(int(task_count)):
                raw = ex_tasks[t] if t < len(ex_tasks) else {"text": "", "upload_required": False}
                raw_text = raw["text"]
                # Reverse-parse an existing "text [Open →](url)" back into text + url,
                # so re-opening a saved week pre-fills the Link field correctly.
                m = re.match(r"^(.*?)\s*\[.*?\]\((https?://[^\)]+)\)\s*$", raw_text)
                default_text = m.group(1).strip() if m else raw_text
                default_link = m.group(2).strip() if m else ""
                tc1, tc2, tc3 = st.columns([3, 2, 1.3])
                with tc1:
                    tv = st.text_input(f"Task {t+1}", value=default_text,
                                       placeholder="e.g. Complete the worksheet", key=f"task_{week_num}_{t}")
                with tc2:
                    tl = st.text_input(f"Link {t+1} (optional)", value=default_link,
                                       placeholder="https://...", key=f"task_link_{week_num}_{t}")
                with tc3:
                    st.markdown("<div style='margin-top:1.8rem;'></div>", unsafe_allow_html=True)
                    upload_req = st.checkbox("Requires file upload", value=raw.get("upload_required", False),
                                             key=f"task_upload_{week_num}_{t}")
                if tv.strip():
                    task_text = f"{tv.strip()} [Open →]({tl.strip()})" if tl.strip() else tv.strip()
                    tasks.append({"text": task_text, "upload_required": upload_req})

            prompt_val = st.text_area(
                "Reflection prompt (shown once all tasks for this week are done)",
                value=get_prompt(selected_pid, week_num), height=80,
                key=f"prompt_{week_num}"
            )

            also_activate = st.checkbox(
                f"Also make {unit_label} {week_num} the active {unit_label.lower()} for participants",
                value=False, key=f"also_activate_{week_num}",
                disabled=(week_num == current_active_week),
            )

            save_col, activate_col, delete_col = st.columns(3)
            with save_col:
                if st.button(f"💾 Save {unit_label} {week_num}", type="primary", key=f"save_{week_num}"):
                    if not title.strip():
                        st.warning("Title is required.")
                    elif not tasks:
                        st.warning("Add at least one task before saving.")
                    else:
                        save_program_week(org_id, selected_pid, week_num, title.strip(),
                                          theme.strip(), materials, tasks)
                        set_prompt(org_id, selected_pid, week_num, prompt_val)
                        msg = (f"{unit_label} {week_num} — '{title.strip()}' saved. "
                               f"{len(materials)} material(s), {len(tasks)} task(s).")
                        if also_activate:
                            set_active_week(selected_pid, week_num)
                            msg += f" It's now the active {unit_label.lower()}."
                        _flash("content", "success", msg)
                        st.rerun()

            with activate_col:
                # Only offer to activate a week whose content has already been saved —
                # activating an empty week would show participants nothing to do.
                if int(week_num) in weeks and week_num != current_active_week:
                    if st.button(f"✅ Set as active {unit_label.lower()}", key=f"activate_content_{week_num}"):
                        set_active_week(selected_pid, week_num)
                        _flash("content", "success",
                              f"{unit_label} {week_num} is now the active {unit_label.lower()}.")
                        st.rerun()

            with delete_col:
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
    # Task submissions (upload-required tasks awaiting review)
    # ═══════════════════════════════════════════════════════════
    with tab_submissions:
        active_program = get_active_program(org_id)
        if not active_program:
            st.info("No active program set.")
        else:
            pending = get_pending_submissions(org_id, active_program["id"])
            if not pending:
                st.info("No submissions waiting for review. 🎉")
            for s in pending:
                person = s.get("profiles") or {}
                with st.expander(f"Week {s['week']}, Task {s['task_index'] + 1} — {person.get('full_name', 'Unknown')}"):
                    st.write(f"**File:** {s['file_name']}")
                    try:
                        url = get_submission_download_url(s["file_path"])
                        if url:
                            st.link_button("⬇ Download / view file", url)
                    except Exception as e:
                        st.warning(f"Couldn't generate a download link: {e}")

                    fb_key = f"sub_fb_{s['id']}"
                    feedback_val = st.text_area("Feedback (shown to the participant)", key=fb_key)
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("✅ Approve", key=f"approve_{s['id']}", type="primary"):
                            review_submission(s, "approved", feedback_val)
                            st.success("Approved — this task now counts toward their progress.")
                            st.rerun()
                    with col_b:
                        if st.button("↩ Send back for revision", key=f"revise_{s['id']}"):
                            if not feedback_val.strip():
                                st.warning("Add a note explaining what needs fixing before sending back.")
                            else:
                                review_submission(s, "needs_revision", feedback_val)
                                st.success("Sent back — the participant can re-upload.")
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
