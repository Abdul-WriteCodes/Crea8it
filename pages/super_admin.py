"""
pages/super_admin.py — Platform-owner oversight dashboard.

Shows every organization running on Crea8it, member/program counts,
and a suspend/reactivate control. Only reachable if profile.role ==
'super_admin' — RLS backs this up at the database level too, so even
a routing mistake here can't leak another org's data to the wrong role.
"""

import streamlit as st
from utils.db import (
    require_role, get_all_organizations, get_org_stats,
    suspend_organization, delete_organization, logout,
)
from utils.theme import page_header, sidebar_account


def show():
    require_role("super_admin")

    sidebar_account(
        role_label="Platform owner",
        name="Super admin",
        on_logout=lambda: (logout(), st.rerun()),
    )

    page_header("Platform overview", "Every organization running a program on Crea8it.")

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
            confirm_key = f"confirm_delete_{org['id']}"
            if st.session_state.get(confirm_key):
                st.error(
                    f"This permanently deletes **{org['name']}** and everything "
                    "in it — members, programs, progress, reflections, payment "
                    "codes. This cannot be undone."
                )
                typed = st.text_input(
                    "Type the organization name to confirm",
                    key=f"delete_input_{org['id']}",
                )
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(
                        "Confirm delete", key=f"do_delete_{org['id']}",
                        type="primary", disabled=(typed != org["name"]),
                    ):
                        delete_organization(org["id"])
                        st.session_state.pop(confirm_key, None)
                        st.success(f"{org['name']} deleted.")
                        st.rerun()
                with col_b:
                    if st.button("Cancel", key=f"cancel_delete_{org['id']}"):
                        st.session_state.pop(confirm_key, None)
                        st.rerun()
            else:
                if st.button("Delete organization", key=f"delete_{org['id']}"):
                    st.session_state[confirm_key] = True
                    st.rerun()

    st.divider()
    st.metric("Total organizations", len(orgs))
    st.metric("Total participants across all orgs", total_members)
