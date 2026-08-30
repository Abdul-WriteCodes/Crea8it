import streamlit as st
from utils.db import (
    get_current_profile, logout, get_active_program, get_active_week,
    get_program_weeks, get_progress, mark_task_done, get_reflection,
    submit_reflection, get_prompt, touch_last_active, get_week_completion_stats,
    get_task_submissions, submit_task_file,
    get_library_resources, get_resource_download_url,
)
from utils.theme import (
    apply_css, page_header, section_label, week_badge,
    task_card, upload_task_card, material_card, reflection_box, feedback_box, kpi_card,
    resource_card, sidebar_account,
)
import time

# get_progress / get_reflection / get_task_submissions are cached and
# invalidated inside utils/db.py itself now (short ttl + .clear() on every
# write), so there's no need to duplicate that caching here in session
# state. Calling them directly also means a rerun after mark_task_done()
# etc. sees the fresh value immediately, since the write already cleared
# the underlying cache — no more manual st.session_state.pop(...) dance.


def show():
    apply_css()

    profile = get_current_profile()
    if not profile:
        st.error("Session expired. Please log in again.")
        st.stop()

    org_id = profile["org_id"]
    participant_id = profile["id"]
    first_name = profile["full_name"].split()[0]

    active_program = get_active_program(org_id)

    sidebar_account(
        role_label="Participant",
        name=first_name,
        subtitle=profile.get("email", ""),
        status_lines=[f"{active_program['unit_label']}: {active_program.get('name','')}"] if active_program
                     else ["No active program yet"],
        on_logout=lambda: (logout(), st.rerun()),
    )

    touch_last_active(org_id, participant_id)

    # ── Celebration handler ────────────────────────────────────
    celebrate = st.session_state.pop("celebrate", None)
    unit_label = active_program["unit_label"] if active_program else "Week"
    if celebrate == "tasks":
        w = st.session_state.pop("celebrate_week", "")
        st.toast(f"{unit_label} {w} tasks complete! Now write your reflection 🎉", icon="🏅")
        st.balloons()
    elif celebrate == "reflection":
        w = st.session_state.pop("celebrate_week", "")
        st.toast(f"{unit_label} {w} reflection submitted — great work! 🙌", icon="📝")
        st.balloons()
    elif celebrate == "task_single":
        st.toast("Task marked complete!", icon="✅")

    # ── Header ────────────────────────────────────────────────
    page_header(f"Welcome back, {first_name}", profile.get("email", ""))

    top_program, top_library = st.tabs(["🗓 My Program", "📚 Library"])

    with top_library:
        show_library(org_id)

    with top_program:
        if not active_program:
            st.info("Your organization hasn't activated a program yet. Check back soon, "
                     "or reach out to your cohort admin.")
        else:
            show_program(profile, active_program, org_id, participant_id, first_name, unit_label)


def show_program(profile, active_program, org_id, participant_id, first_name, unit_label):
    program_id = active_program["id"]
    active_week = active_program["active_week"]
    PROGRAM_WEEKS = get_program_weeks(program_id)
    week_keys = sorted(PROGRAM_WEEKS.keys())

    progress = get_progress(participant_id, program_id)
    submissions = get_task_submissions(participant_id, program_id)

    total_tasks = sum(len(PROGRAM_WEEKS[w]["tasks"]) for w in week_keys if w <= active_week)
    completed_tasks = sum(len(v) for v in progress.values())
    pct = min(100, int((completed_tasks / total_tasks * 100) if total_tasks else 0))

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        kpi_card("Current unit", f"{unit_label} {active_week}", icon="🗓")
    with col_b:
        kpi_card("Tasks done", f"{completed_tasks}/{total_tasks}", icon="✅")
    with col_c:
        kpi_card("Progress", f"{pct}%", icon="📈")

    section_label("Overall completion")
    st.progress(pct / 100)
    st.markdown("<div style='margin-bottom:1.5rem;'></div>", unsafe_allow_html=True)

    if not week_keys:
        st.info("No program content has been published yet. Check back soon.")
        return

    tabs = st.tabs([f"{unit_label} {w}" for w in week_keys])

    for tab, week_num in zip(tabs, week_keys):
        week_data = PROGRAM_WEEKS[week_num]
        locked = week_num > active_week

        with tab:
            st.markdown(f"""
<div style="display:flex;align-items:center;gap:12px;padding:6px 0 4px;">
  <div style="font-family:'Syne',sans-serif;font-size:1.15rem;font-weight:700;color:#F0F4F8;">
    {week_data['title']}
  </div>
  {week_badge(week_num, active_week)}
</div>
<div style="font-size:0.82rem;color:#4A6080;margin-bottom:1.25rem;font-style:italic;">
  {week_data['theme']}
</div>""", unsafe_allow_html=True)

            if locked:
                st.markdown("""
<div style="background:rgba(255,255,255,0.02);border:1px dashed #1F2D3D;
            border-radius:14px;padding:36px;text-align:center;margin:8px 0;">
  <div style="font-size:2rem;margin-bottom:10px;">🔒</div>
  <div style="color:#4A6080;font-size:0.88rem;line-height:1.6;">
    This week unlocks when the cohort progresses.<br>Keep up with your current tasks.
  </div>
</div>""", unsafe_allow_html=True)
                continue

            finished, total = get_week_completion_stats(program_id, week_num, len(week_data["tasks"]))
            if total > 1:
                st.markdown(
                    f'<div style="font-size:0.78rem;color:#8BA0B8;margin:-4px 0 14px;">'
                    f'👥 <strong>{finished}/{total}</strong> builders have finished all '
                    f'{unit_label.lower()} {week_num} tasks</div>',
                    unsafe_allow_html=True
                )

            section_label("This week's materials", color="var(--teal)")
            icon_map = {
                "book": "📖", "video": "🎥", "article": "📄", "worksheet": "📝",
                "template": "🗂️", "portfolio": "💼", "portfolio task": "💼",
                "assignment": "🧩", "link": "🔗", "podcast": "🎧", "quiz": "❓",
                "slides": "📊", "code": "💻", "tool": "🛠️",
            }
            for mat in week_data["materials"]:
                icon = icon_map.get(mat["type"].strip().lower(), "🔗")
                material_card(icon, mat["label"])

            section_label("Your tasks", color="var(--gold)")
            week_done = progress.get(week_num, [])

            for idx, task in enumerate(week_data["tasks"]):
                done = idx in week_done

                if not task["upload_required"]:
                    if done:
                        task_card(task["text"], done=True)
                    else:
                        task_card(task["text"], done=False)
                        checked = st.checkbox("Mark as complete", key=f"task_{week_num}_{idx}", value=False)
                        if checked:
                            mark_task_done(org_id, participant_id, program_id, week_num, idx)
                            touch_last_active(org_id, participant_id)
                            if len(week_done) + 1 == len(week_data["tasks"]):
                                st.session_state["celebrate"] = "tasks"
                                st.session_state["celebrate_week"] = week_num
                            else:
                                st.session_state["celebrate"] = "task_single"
                            st.rerun()
                    continue

                # ── upload-required task ──
                sub = submissions.get((week_num, idx))
                sub_status = sub["status"] if sub else "not_submitted"
                upload_task_card(task["text"], sub_status, sub["file_name"] if sub else "")

                if sub_status == "needs_revision" and sub.get("reviewer_feedback"):
                    feedback_box(f"Reviewer note: {sub['reviewer_feedback']}")

                if sub_status in ("not_submitted", "needs_revision"):
                    uploaded = st.file_uploader(
                        "Upload your file" if sub_status == "not_submitted" else "Re-upload your file",
                        type=["pdf", "docx", "doc", "png", "jpg", "jpeg"],
                        key=f"upload_{week_num}_{idx}",
                    )
                    if uploaded is not None:
                        if uploaded.size > 10 * 1024 * 1024:
                            st.warning("File too large — 10MB max.")
                        elif st.button("Submit for review", key=f"submit_upload_{week_num}_{idx}"):
                            submit_task_file(
                                org_id, participant_id, program_id, week_num, idx,
                                uploaded.getvalue(), uploaded.name, uploaded.type or "application/octet-stream",
                            )
                            touch_last_active(org_id, participant_id)
                            st.session_state["celebrate"] = "task_single"
                            st.rerun()

            st.divider()

            all_tasks_done = len(week_done) == len(week_data["tasks"])
            reflection = get_reflection(participant_id, program_id, week_num)

            if not all_tasks_done:
                remaining = len(week_data["tasks"]) - len(week_done)
                st.markdown(f"""
<div class="alert-info">
  ✏️ Complete <strong>{remaining} more task{"s" if remaining > 1 else ""}</strong>
  to unlock this unit's reflection.
</div>""", unsafe_allow_html=True)

            elif reflection:
                st.markdown(f"""
<div class="alert-success">
  ✅ {unit_label} {week_num} complete — great work, {first_name}!
</div>""", unsafe_allow_html=True)

                with st.expander("📝 Your reflection"):
                    st.markdown(
                        f'<div style="color:#8BA0B8;font-size:0.88rem;line-height:1.65;">'
                        f'{reflection.get("response","")}</div>',
                        unsafe_allow_html=True
                    )

                fb = reflection.get("feedback", "")
                if fb:
                    section_label("Feedback from your cohort admin", color="var(--gold)")
                    feedback_box(fb)

            else:
                prompt = get_prompt(program_id, week_num)
                if prompt:
                    section_label("Weekly reflection", color="var(--gold)")
                    reflection_box(prompt)
                    response = st.text_area(
                        "Your response",
                        placeholder="Write your reflection here — be honest, specific, and thoughtful...",
                        key=f"reflection_input_{week_num}",
                        height=140,
                    )
                    if st.button("Submit reflection →", key=f"submit_ref_{week_num}", type="primary"):
                        if response.strip():
                            submit_reflection(org_id, participant_id, program_id, week_num, response.strip())
                            touch_last_active(org_id, participant_id)
                            st.session_state["celebrate"] = "reflection"
                            st.session_state["celebrate_week"] = week_num
                            st.rerun()
                        else:
                            st.warning("Please write something before submitting.")
                else:
                    st.markdown("""
<div class="alert-success">
  ✅ All tasks done! Your reflection prompt will appear here shortly.
</div>""", unsafe_allow_html=True)

    st.divider()

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        if st.button("🔄 Refresh progress", width='stretch', type="secondary"):
            # Manual override — the cache would self-heal within its ttl
            # anyway, but a button labeled "Refresh" should act on the spot.
            get_progress.clear()
            st.rerun()
    with col_r2:
        if st.button("🔄 Check for new weeks", width='stretch', type="secondary"):
            st.session_state.pop("profile", None)  # forces profile re-fetch
            get_active_program.clear()  # forces active_program re-fetch too
            st.rerun()


def show_library(org_id: str):
    """Org-wide resource library — independent of whichever program is
    currently active, so resources stay reachable across cohort switches
    and aren't re-typed per program."""
    section_label("Browse resources", color="var(--teal)")

    col_s, col_t = st.columns([3, 2])
    with col_s:
        search = st.text_input("Search", placeholder="Search by title or description...",
                                key="lib_search", label_visibility="collapsed")
    with col_t:
        all_resources = get_library_resources(org_id)
        all_tags = sorted({t for r in all_resources for t in (r.get("tags") or [])})
        tag = st.selectbox("Filter by tag", options=[""] + all_tags,
                            format_func=lambda t: "All tags" if t == "" else t,
                            key="lib_tag", label_visibility="collapsed")

    resources = get_library_resources(org_id, search=search, tag=tag)

    if not resources:
        st.info("No resources here yet." if not (search or tag)
                 else "No resources match that search/filter.")
        return

    def _render_resource(r):
        with st.container(border=True):
            resource_card(r)
            if r["source_type"] == "link":
                st.link_button("Open →", r["url"], width='stretch')
            else:
                try:
                    url = get_resource_download_url(r["file_path"])
                    if url:
                        st.link_button("⬇ Download", url, width='stretch')
                except Exception:
                    st.caption("Couldn't generate a download link for this file.")

    # Once a specific tag filter or search is applied, results are
    # already narrow — show them as a flat list. Otherwise, group by
    # tag so the library stays browsable as it grows past a handful
    # of items. Untagged resources get their own group at the end.
    if tag or search:
        for r in resources:
            _render_resource(r)
        return

    grouped: dict[str, list] = {t: [] for t in all_tags}
    untagged = []
    for r in resources:
        r_tags = r.get("tags") or []
        if not r_tags:
            untagged.append(r)
        for t in r_tags:
            grouped.setdefault(t, []).append(r)

    for t in all_tags:
        items = grouped.get(t) or []
        if not items:
            continue
        with st.expander(f"{t} ({len(items)})", expanded=(t == all_tags[0])):
            for r in items:
                _render_resource(r)

    if untagged:
        with st.expander(f"Untagged ({len(untagged)})", expanded=not all_tags):
            for r in untagged:
                _render_resource(r)
