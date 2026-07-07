import hashlib
import os
import binascii
import streamlit as st
from utils.sheets import get_participant, touch_last_active, set_participant_password


# ── Password hashing (PBKDF2-HMAC-SHA256, stdlib only — no extra
#    dependency needed on Streamlit Cloud) ───────────────────────

def hash_password(password: str, salt: bytes = None) -> str:
    if salt is None:
        salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return binascii.hexlify(salt).decode() + ":" + binascii.hexlify(dk).decode()


def _verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, hash_hex = stored.split(":")
        salt = binascii.unhexlify(salt_hex)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
        return binascii.hexlify(dk).decode() == hash_hex
    except Exception:
        return False


def _normalize_phone(raw: str) -> str:
    """Keep digits only, so '+2348012345678', '2348012345678' and
    '08012345678' all compare equal on their last 9 digits."""
    digits = "".join(ch for ch in str(raw) if ch.isdigit())
    return digits[-9:] if len(digits) >= 9 else digits


def _set_session(participant: dict):
    st.session_state["participant"] = participant
    st.session_state["logged_in"] = True
    touch_last_active(participant.get("email", ""))


def login_participant(email: str, password: str) -> bool:
    """Normal email + password login for returning participants.
    Returns False if the email is unknown, no password has been set yet
    (route those through first_time_set_password instead), or the
    password is wrong."""
    participant = get_participant(email)
    if not participant:
        return False
    stored_hash = str(participant.get("password_hash", "")).strip()
    if not stored_hash or not _verify_password(password, stored_hash):
        return False
    _set_session(participant)
    return True


def has_password_set(email: str) -> bool | None:
    """True/False if the account exists, None if the email isn't found."""
    participant = get_participant(email)
    if not participant:
        return None
    return bool(str(participant.get("password_hash", "")).strip())


def first_time_set_password(email: str, phone: str, new_password: str) -> bool:
    """One-time password setup for accounts that registered before password
    login existed (or whose password was reset by admin). Requires the
    WhatsApp number on file to match, so setting up a password isn't itself
    a way to hijack someone else's account just by knowing their email."""
    participant = get_participant(email)
    if not participant:
        return False

    stored_phone = _normalize_phone(participant.get("phone", ""))
    given_phone = _normalize_phone(phone)
    if not stored_phone or not given_phone or stored_phone != given_phone:
        return False

    password_hash = hash_password(new_password)
    set_participant_password(email, password_hash)
    participant["password_hash"] = password_hash
    _set_session(participant)
    return True


def login_after_registration(email: str) -> bool:
    """Trusted direct login right after a successful registration — no
    password check needed since the payment code was already verified
    and the password was just set during registration itself."""
    participant = get_participant(email)
    if participant:
        _set_session(participant)
        return True
    return False


def logout():
    st.session_state["participant"] = None
    st.session_state["logged_in"] = False
    st.session_state["is_admin"] = False
    # Clear program-state keys so the next login always re-reads from the
    # sheet instead of inheriting stale session values.
    for key in ("_active_program_id", "_active_unit_label",
                "active_week", "active_week_last_check",
                "login_stage", "login_email"):
        st.session_state.pop(key, None)


def is_logged_in() -> bool:
    return st.session_state.get("logged_in", False)


def get_current_participant() -> dict | None:
    return st.session_state.get("participant", None)


def login_admin(password: str) -> bool:
    from config import ADMIN_PASSWORD
    if password == ADMIN_PASSWORD:
        st.session_state["is_admin"] = True
        return True
    return False


def is_admin() -> bool:
    return st.session_state.get("is_admin", False)
