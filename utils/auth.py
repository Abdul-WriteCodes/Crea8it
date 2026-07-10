"""
utils/auth.py — thin wrapper kept for name-compatibility with the
original single-tenant app. All real logic lives in utils/db.py now.
"""

from utils.db import (
    is_logged_in, get_current_profile, get_current_participant,
    logout, require_role,
)


def is_admin() -> bool:
    """True for BOTH org_admin and super_admin — pages that need to
    tell them apart should check profile['role'] directly."""
    profile = get_current_profile()
    return bool(profile and profile["role"] in ("org_admin", "super_admin"))


def is_org_admin() -> bool:
    profile = get_current_profile()
    return bool(profile and profile["role"] == "org_admin")


def is_super_admin() -> bool:
    profile = get_current_profile()
    return bool(profile and profile["role"] == "super_admin")


def is_participant() -> bool:
    profile = get_current_profile()
    return bool(profile and profile["role"] == "participant")
