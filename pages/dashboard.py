import streamlit as st
from utils.db import (
    get_current_profile, logout, get_active_program, get_active_week,
    get_program_weeks, get_progress, mark_task_done, get_reflection,
    submit_reflection, get_prompt, touch_last_active, get_week_completion_stats,
)
from utils.theme import (
    apply_css, page_header, section_label, week_badge,
    task_card, material_card, reflection_box, feedback_box, kpi_card,
)
import time


def get_progress_cached(participant_id: str, program_id: str) -> dict:
    key = f"progress_{program_id}"
    if key not in st.session_state or st.session_state.get(f"{key}_pid") != participant_id:
        st.session_state[key] = get_progress(participant_id, program_id)
        st.session_state[f"{key}_pid"] = participant_id
    return st.session_state[key]


def get_reflection_cached(participant_id: str, program_id: str, week: int) -> dict | None:
    key = f"reflection_{program_id}_{week}"
    if key not in st.session_state:
        st.session_state[key] = get_reflection(participant_id, program_id, week)
    return st.session_state[key]


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
    col1, col2 = st.columns([5, 1])
    with col1:
        page_header(f"Welcome back, {first_name}", profile.get("email", ""))
    with col2:
        st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
        if st.button("Log out", type="secondary"):
            logout()
            st.rerun()

    if not active_program:
        st.info("Your organization hasn't activated a program yet. Check back soon, "
                 "or reach out to your cohort admin.")
        return

    program_id = active_program["id"]
    active_week = active_program["active_week"]
    PROGRAM_WEEKS = get_program_weeks(program_id)
    week_keys = sorted(PROGRAM_WEEKS.keys())

    progress = get_progress_cached(participant_id, program_id)

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
                if done:
                    task_card(task, done=True)
                else:
                    task_card(task, done=False)
                    checked = st.checkbox("Mark as complete", key=f"task_{week_num}_{idx}", value=False)
                    if checked:
                        mark_task_done(org_id, participant_id, program_id, week_num, idx)
                        touch_last_active(org_id, participant_id)
                        if len(week_done) + 1 == len(week_data["tasks"]):
                            st.session_state["celebrate"] = "tasks"
                            st.session_state["celebrate_week"] = week_num
                        else:
                            st.session_state["celebrate"] = "task_single"
                        st.session_state.pop(f"progress_{program_id}", None)
                        st.rerun()

            st.divider()

            all_tasks_done = len(week_done) == len(week_data["tasks"])
            reflection = get_reflection_cached(participant_id, program_id, week_num)

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
                            st.session_state.pop(f"reflection_{program_id}_{week_num}", None)
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
            st.session_state.pop(f"progress_{program_id}", None)
            st.rerun()
    with col_r2:
        if st.button("🔄 Check for new weeks", width='stretch', type="secondary"):
            st.session_state.pop("profile", None)  # forces active_program re-fetch too
            st.rerun()
