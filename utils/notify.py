"""
Zero-infrastructure WhatsApp outreach.

No Meta Business account, no Twilio, no template approval, no API tokens.
This just builds a `wa.me` deep link that opens WhatsApp (app or web) with
the message pre-filled. Abdul reviews it and hits send himself, from his
own WhatsApp number.

Trade-off, stated plainly: this is one click per person, not automatic.
For a cohort this size that's a fair trade — it keeps the personal touch
that's already worked for distribution, with none of the Meta/Twilio setup
overhead (business verification, approved sender number, template review).
If the cohort size grows into the hundreds across concurrent programs,
that's the point to revisit the official API.
"""
from urllib.parse import quote

DEFAULT_COUNTRY_CODE = "234"  # Nigeria


def _digits_only(raw: str) -> str:
    return "".join(ch for ch in str(raw) if ch.isdigit())


def to_international(phone: str, default_country_code: str = DEFAULT_COUNTRY_CODE) -> str:
    """Best-effort normalize a phone number to the digits-only international
    format wa.me expects (no '+'), e.g.:
      '08012345678'     -> '2348012345678'
      '+2348012345678'  -> '2348012345678'
      '2348012345678'   -> '2348012345678'
    """
    digits = _digits_only(phone)
    if not digits:
        return ""
    if digits.startswith("00"):
        digits = digits[2:]
    if digits.startswith("0"):
        digits = default_country_code + digits[1:]
    elif not digits.startswith(default_country_code) and len(digits) <= 10:
        digits = default_country_code + digits
    return digits


def build_whatsapp_link(phone: str, message: str) -> str:
    """Return a wa.me deep link with the message pre-filled and URL-encoded.
    Returns '' if the phone number can't be normalized (so callers can hide
    the button instead of showing a dead link)."""
    number = to_international(phone)
    if not number:
        return ""
    return f"https://wa.me/{number}?text={quote(message)}"
