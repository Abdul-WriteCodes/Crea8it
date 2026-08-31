import os
import base64
import streamlit as st

from utils.theme import apply_css
from utils.db import (
    is_valid_org_code, join_organization, register_organization, sign_in,
)
from config import PROGRAM_NAME

LAB_CSS = """
<style>
.lp-hero { padding: 18px 0 16px; text-align: center; }
.lp-wordmark {
  font-family: 'Syne', sans-serif;
  font-size: 2.5rem;
  font-weight: 800;
  letter-spacing: -0.04em;
  line-height: 1.05;
  margin-bottom: 10px;
}
.lp-tagline {
  font-size: 0.88rem;
  color: #8BA0B8;
  letter-spacing: 0.06em;
  margin-bottom: 14px;
}
.lp-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #111827;
  border: 1px solid #1F2D3D;
  border-radius: 20px;
  padding: 6px 16px;
  font-family: 'DM Mono', monospace;
  font-size: 0.65rem;
  color: #4A6080;
  letter-spacing: 0.1em;
}
.lp-badge-dot { color: #22c55e; }
.lab-icon-strip {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 10px;
  padding: 16px 0 20px;
}
.lab-icon-pill {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  background: #111827;
  border: 1px solid #1F2D3D;
  border-radius: 20px;
  padding: 6px 14px;
  font-family: 'DM Mono', monospace;
  font-size: 0.62rem;
  color: #8BA0B8;
  white-space: nowrap;
}
.sp-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 4px 0 8px;
}
.sp-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 10px;
}
.sp-avatars { display: flex; align-items: center; }
.sp-avatar {
  width: 38px; height: 38px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #0A1628;
  margin-left: -10px;
  box-shadow: 0 0 0 2px #00B4D8;
}
.sp-avatars img:first-child { margin-left: 0; }
.sp-text { font-size: 0.82rem; color: #8BA0B8; line-height: 1.45; text-align: left; }
.sp-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: #22c55e;
  display: inline-block;
  margin-right: 5px;
  box-shadow: 0 0 5px #22c55e;
}
.sp-blurb {
  font-size: 11px;
  color: #6B7280;
  text-align: center;
  line-height: 1.7;
  max-width: 300px;
  margin: 0 auto 20px;
}
.lp-trust-strip {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 20px;
  padding: 18px 0 10px;
}
.lp-trust-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: 'DM Mono', monospace;
  font-size: 0.62rem;
  color: #4A6080;
}
.lp-check { color: #00C896; }
</style>
"""

LAB_SVG_INJECTOR = """
<script>
(function() {
  var old = window.parent.document.getElementById('lab-bg-svg');
  if (old) old.remove();

  var styleId = 'lab-bg-svg-style';
  if (!window.parent.document.getElementById(styleId)) {
    var s = window.parent.document.createElement('style');
    s.id = styleId;
    s.textContent = [
      '#lab-bg-svg {',
      '  position: fixed;',
      '  top: 0; left: 0;',
      '  width: 100vw; height: 100vh;',
      '  pointer-events: none;',
      '  z-index: 0;',
      '}'
    ].join('');
    window.parent.document.head.appendChild(s);
  }

  var svgMarkup = `<svg id="lab-bg-svg" viewBox="0 0 800 900"
    preserveAspectRatio="xMidYMid slice"
    xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <circle cx="740" cy="90" r="80" fill="none" stroke="#00B4D8" stroke-width="0.7" opacity="0.2"/>
  <circle cx="740" cy="90" r="55" fill="none" stroke="#00B4D8" stroke-width="0.5" opacity="0.14"/>
  <circle cx="740" cy="90" r="8"  fill="#00B4D8" opacity="0.28"/>
  <circle cx="60" cy="780" r="70" fill="none" stroke="#F5A623" stroke-width="0.7" opacity="0.18"/>
  <circle cx="60" cy="780" r="45" fill="none" stroke="#F5A623" stroke-width="0.5" opacity="0.12"/>
  <circle cx="60" cy="780" r="6"  fill="#F5A623" opacity="0.25"/>
  <circle cx="790" cy="520" r="60" fill="none" stroke="#00C896" stroke-width="0.6" opacity="0.16"/>
  <circle cx="790" cy="520" r="38" fill="none" stroke="#00C896" stroke-width="0.4" opacity="0.10"/>
  <circle cx="790" cy="520" r="5"  fill="#00C896" opacity="0.25"/>
  </svg>`;

  var parser = new window.parent.DOMParser();
  var doc = parser.parseFromString(svgMarkup, 'image/svg+xml');
  var svg = doc.documentElement;
  window.parent.document.body.appendChild(svg);
})();
</script>
"""

ICON_STRIP_HTML = """
<div class="lab-icon-strip">
  <div class="lab-icon-pill">
    <svg width="11" height="14" viewBox="0 0 11 14" fill="none" xmlns="http://www.w3.org/2000/svg">
      <line x1="3.5" y1="0" x2="3.5" y2="5.5" stroke="#00B4D8" stroke-width="1.1" stroke-linecap="round"/>
      <line x1="7.5" y1="0" x2="7.5" y2="5.5" stroke="#00B4D8" stroke-width="1.1" stroke-linecap="round"/>
      <line x1="1.5" y1="0" x2="9.5" y2="0"   stroke="#00B4D8" stroke-width="1.1" stroke-linecap="round"/>
      <polygon points="3.5,5.5 0.5,12 10.5,12 7.5,5.5" fill="none" stroke="#00B4D8"
               stroke-width="0.9" stroke-linejoin="round"/>
      <ellipse cx="5.5" cy="12" rx="4.5" ry="1.2" fill="none" stroke="#00B4D8"
               stroke-width="0.6" opacity="0.5"/>
    </svg>
    Flask lab
  </div>
  <div class="lab-icon-pill">
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="7" cy="7" r="2" stroke="#F5A623" stroke-width="1"/>
      <ellipse cx="7" cy="7" rx="6" ry="2.2" fill="none" stroke="#F5A623" stroke-width="0.8"
               transform="rotate(-30, 7, 7)" opacity="0.6"/>
      <ellipse cx="7" cy="7" rx="6" ry="2.2" fill="none" stroke="#F5A623" stroke-width="0.8"
               transform="rotate(30, 7, 7)" opacity="0.6"/>
      <ellipse cx="7" cy="7" rx="6" ry="2.2" fill="none" stroke="#F5A623" stroke-width="0.8"
               opacity="0.45"/>
    </svg>
    AI/ML circuits
  </div>
  <div class="lab-icon-pill">
    <svg width="14" height="12" viewBox="0 0 14 12" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="2"  cy="2"  r="2" fill="#0D1117" stroke="#00C896" stroke-width="0.8"/>
      <circle cx="12" cy="2"  r="2" fill="#0D1117" stroke="#00C896" stroke-width="0.8"/>
      <circle cx="7"  cy="10" r="2" fill="#0D1117" stroke="#00C896" stroke-width="0.8"/>
      <line x1="4"  y1="2"  x2="10" y2="2"  stroke="#00C896" stroke-width="0.6"/>
      <line x1="2"  y1="4"  x2="7"  y2="8"  stroke="#00C896" stroke-width="0.6"/>
      <line x1="12" y1="4"  x2="7"  y2="8"  stroke="#00C896" stroke-width="0.6"/>
    </svg>
    Neural paths
  </div>
  <div class="lab-icon-pill">
    <svg width="14" height="10" viewBox="0 0 14 10" fill="none" xmlns="http://www.w3.org/2000/svg">
      <polyline points="0,7 3,7 4.5,1.5 7,9 9.5,4 11,7 14,7"
                stroke="#8BA0B8" stroke-width="0.9"
                stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    Live signals
  </div>
</div>
"""


def _avatar_strip_html() -> str:
    avatar_files = [f"user{i}.jpeg" for i in range(1, 7)]
    imgs_html = ""
    base_dir = os.path.dirname(os.path.dirname(__file__))  # project root
    for i, fname in enumerate(avatar_files):
        path = os.path.join(base_dir, "assets", "avatars", fname)
        if os.path.exists(path):
            with open(path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
                # Inline width/height/style (not just the .sp-avatar class)
                # so the browser sizes these correctly the instant the tag
                # arrives, instead of briefly painting the raw full-size
                # image and reflowing once the separate CSS block loads.
                margin = "0" if i == 0 else "-10px"
                imgs_html += (
                    f'<img src="data:image/jpeg;base64,{encoded}" '
                    f'width="38" height="38" '
                    f'style="width:38px;height:38px;border-radius:50%;object-fit:cover;'
                    f'border:2px solid #0A1628;margin-left:{margin};'
                    f'box-shadow:0 0 0 2px #00B4D8;display:inline-block;vertical-align:middle;" '
                    f'class="sp-avatar" alt="cohort member" />'
                )
    return imgs_html


# ═══════════════════════════════════════════════════════════════
# Tab 1: Participant joins an existing org via org_code
# ═══════════════════════════════════════════════════════════════

def _join_tab():
    st.markdown("""
    <div class="alert-warn" style="margin:16px 0 20px;">
      <strong>How to join a Program:</strong>
      Fill your biodata and the Organization Code issued by your
      cohort admin to unlock your program.
    </div>
    """, unsafe_allow_html=True)

    with st.form("join_form"):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name")
        with col2:
            email = st.text_input("Email Address")

        col3, col4 = st.columns(2)
        with col3:
            whatsapp = st.text_input("WhatsApp Number", placeholder="+2348012345678")
        with col4:
            org_code = st.text_input("Organization Code", placeholder="e.g. AICRE4821")

        col5, col6 = st.columns(2)
        with col5:
            new_password = st.text_input("Create Password", type="password")
        with col6:
            confirm_password = st.text_input("Confirm Password", type="password")

        payment_code = st.text_input("Payment Code (leave blank if none required)", value="")
        submitted = st.form_submit_button("Create My Account →", width='stretch')

    if submitted:
        if not all([full_name, email, whatsapp, org_code, new_password, confirm_password]):
            st.error("Please fill in all required fields.")
            return
        if len(new_password) < 6:
            st.error("Password should be at least 6 characters.")
            return
        if new_password != confirm_password:
            st.error("Passwords don't match.")
            return

        with st.spinner("Checking organization code..."):
            if not is_valid_org_code(org_code):
                st.error("That organization code isn't valid or is no longer active. "
                          "Double-check it with your cohort admin.")
                return

        with st.spinner("Setting up your account..."):
            try:
                join_organization(
                    org_code=org_code,
                    full_name=full_name.strip(),
                    whatsapp=whatsapp.strip(),
                    email=email.strip().lower(),
                    password=new_password,
                    payment_code=payment_code.strip() or None,
                )
            except Exception as e:
                msg = str(e)
                if "Invalid or already-used payment code" in msg:
                    st.error("That payment code isn't valid or has already been used.")
                else:
                    st.error(f"Couldn't complete registration: {e}")
                return

        st.success(f"Welcome, {full_name.split()[0]}! Your account is ready — switch to "
                   f"'Already Registered' to log in.")


# ═══════════════════════════════════════════════════════════════
# Tab 2: New cohort operator starts their own organization
# ═══════════════════════════════════════════════════════════════

def _start_cohort_tab():
    st.markdown("""
    <div class="alert-warn" style="margin:16px 0 20px;">
      <strong>Run your own program.</strong>
      This creates your organization and admin login. You'll get a
      unique organization code to share with your participants —
      your WhatsApp contact is shown to them so they can reach you
      directly.
    </div>
    """, unsafe_allow_html=True)

    with st.form("org_signup_form"):
        org_name = st.text_input("Organization / cohort name")
        col1, col2 = st.columns(2)
        with col1:
            admin_name = st.text_input("Your name")
        with col2:
            admin_whatsapp = st.text_input("Your WhatsApp number", placeholder="+2348012345678")
        admin_email = st.text_input("Your email")
        col3, col4 = st.columns(2)
        with col3:
            password = st.text_input("Create Password", type="password")
        with col4:
            confirm_password = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Create My Organization →", width='stretch')

    if submitted:
        if not all([org_name, admin_name, admin_whatsapp, admin_email, password, confirm_password]):
            st.error("Please fill in every field.")
            return
        if len(password) < 6:
            st.error("Password should be at least 6 characters.")
            return
        if password != confirm_password:
            st.error("Passwords don't match.")
            return

        with st.spinner("Creating your organization..."):
            try:
                result = register_organization(org_name.strip(), admin_name.strip(),
                                                admin_whatsapp.strip(), admin_email.strip().lower(),
                                                password)
            except Exception as e:
                st.error(f"Couldn't create your organization: {e}")
                return

        st.success(
            f"Organization created! Your join code is **{result['org_code']}** — "
            f"share this with participants so they can register. You're logged in now."
        )
        st.rerun()


# ═══════════════════════════════════════════════════════════════
# Tab 3: Everyone logs in here (super_admin / org_admin / participant)
# ═══════════════════════════════════════════════════════════════

def _login_tab():
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in →", width='stretch')

    if submitted:
        if not email or not password:
            st.error("Please enter both your email and password.")
            return
        with st.spinner("Logging in..."):
            try:
                sign_in(email.strip().lower(), password)
            except Exception:
                st.error("Incorrect email or password. Please try again.")
                return
        st.rerun()


# ═══════════════════════════════════════════════════════════════
# Full landing page — matches the original single-tenant layout:
# hero + icon strip + avatar strip once, then one expander with tabs
# ═══════════════════════════════════════════════════════════════

def _flatten(html: str) -> str:
    """Strip leading whitespace from every line of an HTML fragment.
    Needed because these fragments get built from indented Python
    triple-quoted strings and then combined together — if any line
    still carries 4+ literal leading spaces when it reaches st.markdown,
    Markdown's own rules treat it as an indented code block and render
    it as literal text instead of parsing it as HTML."""
    return "\n".join(line.lstrip() for line in html.strip("\n").split("\n"))


def show():
    apply_css()
    st.markdown(LAB_CSS, unsafe_allow_html=True)
    st.html(LAB_SVG_INJECTOR)

    imgs_html = _avatar_strip_html()
    avatar_block = _flatten(f"""
        <div class="sp-section">
          <div class="sp-wrap">
            <div class="sp-avatars">{imgs_html}</div>
            <div class="sp-text">
              <span><span class="sp-dot"></span>Used by 100+ Builders</span>
            </div>
          </div>
          <p class="sp-blurb">
            Join the builders turning
            <span style="color:#FFD700;">ideas into real products, careers, and startups</span>
            — from scratch, with grit and resilience, in the most creative way.
          </p>
        </div>
        """) if imgs_html else ""

    # CSS + hero + icon strip + avatar strip go out as ONE markdown call
    # (one wire message) instead of several, so the browser never has a
    # gap between "images arrived" and "their CSS arrived" to paint in.
    # _flatten() strips every line down to zero leading whitespace so
    # nesting avatar_block/ICON_STRIP_HTML here can't trigger Markdown's
    # indented-code-block rule.
    st.markdown(_flatten(f"""
    <div class="lp-hero">
      <div class="lp-wordmark">
        <span style="color:#FFD700;">📟 </span><br><span style="color:#00B4D8;">Crea8Lab</span>
      </div>
      <div class="lp-tagline">
        Build ⚙️ &nbsp;●&nbsp; Launch 🚀 &nbsp;●&nbsp; Learn 🤸🏻 &nbsp;●&nbsp; Win 🏆
      </div>
      <div class="lp-badge">
        <span class="lp-badge-dot">●</span> Multi-cohort platform
        <span class="lp-badge-dot">●</span> Open now
      </div>
    </div>
    {_flatten(ICON_STRIP_HTML)}
    {avatar_block}
    """), unsafe_allow_html=True)

    with st.expander("Get Started Here👇: Registration & Login 🔐", expanded=False):
        tab_join, tab_start, tab_login = st.tabs(
            ["✦ New Registration", "🚀 Start a Cohort", "→ 📋 Already Registered"]
        )
        with tab_join:
            _join_tab()
        with tab_start:
            _start_cohort_tab()
        with tab_login:
            _login_tab()

    st.markdown("""
    <div class="lp-trust-strip">
      <div class="lp-trust-item"><span class="lp-check">✓</span> Secure code access</div>
      <div class="lp-trust-item"><span class="lp-check">✓</span> Multi-cohort platform</div>
      <div class="lp-trust-item"><span class="lp-check">✓</span> Built for builders</div>
    </div>
    """, unsafe_allow_html=True)
