"""
pages/super_admin.py — Platform-owner oversight dashboard.

Shows every organization running on Crea8it, member/program counts,
and a suspend/reactivate control. Only reachable if profile.role ==
'super_admin' — RLS backs this up at the database level too, so even
a routing mistake here can't leak another org's data to the wrong role.
"""

import streamlit as st
from utils.db import require_role, get_all_organizations, get_org_stats, suspend_organization, logout
from utils.theme import page_header


def show():
    require_role("super_admin")

    col1, col2 = st.columns([5, 1])
    with col1:
        page_header("Platform overview", "Every organization running a program on Crea8it.")
    with col2:
        st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
        if st.button("Log out"):
            logout()
            st.rerun()

    orgs = get_all_organizations()

    if not orgs:
        st.info("No organizations yet.")
        return

    total_members = 0
    for org in orgs:
        stats = get_org_stats(org["id"])
        total_members += stats["member_count"] or 0

        with st.expander(f"{org['name']}  —  {org['org_code']}  "
                          f"{'🟢' if org['is_active'] else '🔴 suspended'}"):
            col1, col2, col3 = st.columns(3)
            col1.metric("Members", stats["member_count"] or 0)
            col2.metric("Programs", stats["program_count"] or 0)
            col3.metric("Plan", org["plan"])

            st.write(f"**Admin:** {org['admin_name']}")
            st.write(f"**WhatsApp:** {org['admin_whatsapp']}")
            st.write(f"**Email:** {org['admin_email']}")

            if org["is_active"]:
                if st.button("Suspend organization", key=f"suspend_{org['id']}"):
                    suspend_organization(org["id"], False)
                    st.rerun()
            else:
                if st.button("Reactivate organization", key=f"reactivate_{org['id']}"):
                    suspend_organization(org["id"], True)
                    st.rerun()

    st.divider()
    st.metric("Total organizations", len(orgs))
    st.metric("Total participants across all orgs", total_members)
