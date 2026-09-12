import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

st.set_page_config(
    page_title="Crea8it Labs",
    page_icon="🧩",
    layout="centered",
    initial_sidebar_state="expanded",
)

from utils.theme import apply_css
from utils.db import is_logged_in, get_current_profile
from utils.auth import is_super_admin, is_org_admin, is_participant

# ── Logged-out screen: checked FIRST, before any sidebar/page code
# runs, so it renders on a clean page rather than bleeding into
# whatever context (e.g. the sidebar) triggered the logout. ────────
if st.session_state.get("logged_out_redirect_url"):
    url = st.session_state.pop("logged_out_redirect_url")
    apply_css()
    st.markdown(
        f"""
        <div style="max-width:420px;margin:18vh auto 0;text-align:center;
                    padding:2.2rem 1.8rem;border:1px solid var(--border);
                    border-radius:16px;background:var(--surface);">
          <div style="font-size:2rem;margin-bottom:0.4rem;">👋</div>
          <div style="font-family:var(--font-d);font-size:1.3rem;
                      font-weight:700;color:var(--text,#fff);margin-bottom:0.3rem;">
            You've been logged out
          </div>
          <div style="font-family:var(--font-b);font-size:0.92rem;
                      color:var(--muted,#9CA3AF);margin-bottom:1.4rem;">
            Come back anytime — your progress is saved.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.link_button(
            "Return to Crea8it",
            url,
            type="primary",
            width="stretch",
        )
    st.stop()

# ── Route BEFORE any UI renders ───────────────────────────────
if is_logged_in():
    profile = get_current_profile()
    apply_css()

    if profile is None:
        # session exists but profile row is missing/still propagating
        st.error("We couldn't load your account. Please try logging in again.")
        from utils.db import logout_and_redirect
        logout_and_redirect()

    elif profile["role"] == "super_admin":
        import pages.super_admin as super_admin
        super_admin.show()

    elif profile["role"] == "org_admin":
        import pages.admin as admin
        admin.show()

    else:  # participant
        import pages.dashboard as dashboard
        dashboard.show()

else:
    apply_css()
    import pages.register as register
    register.show()
