import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

st.set_page_config(
    page_title="Crea8it Labs",
    page_icon="🧩",
    layout="centered",
)

from utils.theme import apply_css
from utils.db import is_logged_in, get_current_profile
from utils.auth import is_super_admin, is_org_admin, is_participant

# ── Route BEFORE any UI renders ───────────────────────────────
if is_logged_in():
    profile = get_current_profile()
    apply_css()

    if profile is None:
        # session exists but profile row is missing/still propagating
        st.error("We couldn't load your account. Please try logging in again.")
        from utils.db import logout
        logout()
        st.rerun()

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
