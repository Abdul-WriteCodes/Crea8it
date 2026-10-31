/*
  Crea8it — certificate verification
  ----------------------------------
  Calls the public Supabase RPC verify_certificate(p_code) with the ANON key.
  That key is public by design: it can only run functions granted to "anon", and the
  only one granted is verify_certificate, which returns name/program/org/cohort/date/status.

  >>> Before this page works, paste your two Supabase values below
      (Dashboard → Project Settings → API → Project URL and "anon public" key).
      NEVER paste the service_role key here.
*/
(function () {
    "use strict";

    var SUPABASE_URL      = "https://taaselqbqzhzimfosezv.supabase.co";   // e.g. https://abcdxyz.supabase.co
    var SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRhYXNlbHFicXpoemltZm9zZXp2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM2MzI5ODIsImV4cCI6MjA5OTIwODk4Mn0.ThDu9dgrOLAWAWpwWUAEzv6YVI8DHAk6gbQCvDD5fMg";

    var form   = document.getElementById("verify-form");
    var input  = document.getElementById("cert-id");
    var btn    = document.getElementById("verify-btn");
    var out    = document.getElementById("verify-result");
    var CODE_RE = /^C8L-\d{4}-[A-Z0-9]{4,12}$/;   // random codes AND legacy numeric ones (C8L-2026-0347)

    function configured() {
        return SUPABASE_URL.indexOf("PASTE_") !== 0 && SUPABASE_ANON_KEY.indexOf("PASTE_") !== 0;
    }

    function el(tag, cls, text) {
        var n = document.createElement(tag);
        if (cls) n.className = cls;
        if (text != null) n.textContent = text;     // textContent only: names come from the database
        return n;
    }

    function fmtDate(iso) {
        var d = new Date(iso + "T00:00:00Z");
        if (isNaN(d.getTime())) return iso;
        return d.toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });
    }

    var ICON_OK  = "M3.5 9.5l3.5 3.5 7.5-8";
    var ICON_BAD = "M4 4l10 10M14 4L4 14";
    var VERIFY_BASE = "https://crea8it.com/verify?id=";
    var REPORT_EMAIL = "Abdulwrite77@gmail.com";
    // Crea8it's own cohorts: Crea8it Studio is already the issuer, so no separate "Delivered by" line.
    var OWN_ORGS = ["crea8it studio", "crea8it labs"];

    // Static artwork (no database content), same puzzle-piece mark as the printed certificate.
    var MARK_SVG =
        '<svg viewBox="0 0 64 64" width="54" height="54" role="img" aria-label="Crea8it logo">' +
        '<circle cx="32" cy="32" r="30" fill="#F8F4EC" stroke="#161B22" stroke-width="1.6"/>' +
        '<circle cx="32" cy="32" r="26.5" fill="none" stroke="#A67C3D" stroke-width=".8"/>' +
        '<g transform="translate(32 32) scale(0.9) translate(-28 -20)">' +
        '<path d="M10 10 L20 10 A5 5 0 1 1 28 10 L38 10 L38 20 A5 5 0 1 1 38 28 L38 38 L28 38 A5 5 0 1 0 20 38 L10 38 L10 28 A5 5 0 1 0 10 20 Z" fill="#161B22"/>' +
        '<circle cx="24" cy="24" r="3.6" fill="#A67C3D"/></g></svg>';

    function icon(path) {
        var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.setAttribute("viewBox", "0 0 18 18"); svg.setAttribute("aria-hidden", "true");
        var p = document.createElementNS("http://www.w3.org/2000/svg", "path");
        p.setAttribute("d", path); svg.appendChild(p);
        return svg;
    }

    function badge(kind, text, path) {
        var b = el("div", "verify-badge " + kind);
        b.appendChild(icon(path)); b.appendChild(document.createTextNode(text));
        return b;
    }

    function show(node) { out.replaceChildren(node); out.hidden = false; }

    function message(kind, badgeText, path, text) {
        var card = el("div", "verify-card");
        card.appendChild(badge(kind, badgeText, path));
        card.appendChild(el("p", "verify-msg", text));
        show(card);
    }

    function cell(grid, label, value) {
        var w = el("div", "vc-cell");
        w.appendChild(el("div", "vc-label", label));
        w.appendChild(el("div", "vc-value", value));
        grid.appendChild(w);
    }

    function copyText(text, btn, doneLabel) {
        var original = btn.textContent;
        function ok() { btn.textContent = doneLabel; setTimeout(function () { btn.textContent = original; }, 1600); }
        function fallback() {
            var t = document.createElement("textarea");
            t.value = text; t.setAttribute("readonly", ""); t.style.position = "fixed"; t.style.opacity = "0";
            document.body.appendChild(t); t.select();
            try { if (document.execCommand("copy")) ok(); } catch (e) { /* ignore */ }
            document.body.removeChild(t);
        }
        if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(ok, fallback);
        else fallback();
    }

    function checkedAt() {
        return new Date().toLocaleString("en-GB", { day: "numeric", month: "long", year: "numeric", hour: "2-digit", minute: "2-digit" });
    }

    function render(code, c) {
        var valid = c.status === "valid";
        var card = el("div", "verify-cert " + (valid ? "is-valid" : "is-revoked"));
        var frame = el("div", "vc-frame");

        // Brand header
        var brand = el("div", "vc-brand");
        var mark = el("div", "vc-mark"); mark.innerHTML = MARK_SVG;   // static constant, no db data
        brand.appendChild(mark);
        brand.appendChild(el("div", "vc-word", "CREA8IT STUDIO"));
        brand.appendChild(el("div", "vc-sub", "COHORT-BASED AI PROGRAMS"));
        frame.appendChild(brand);

        // Status
        var status = el("div", "vc-status");
        var seal = el("div", "vc-seal"); seal.appendChild(icon(valid ? ICON_OK : ICON_BAD));
        status.appendChild(seal);
        var st = el("div", "vc-status-text");
        st.appendChild(el("div", "vc-status-title", valid ? "Verified certificate" : "Certificate revoked"));
        st.appendChild(el("div", "vc-status-sub", valid
            ? "This certificate is genuine and was issued by Crea8it Studio."
            : "This certificate has been revoked and is no longer valid."));
        status.appendChild(st);
        frame.appendChild(status);

        // Holder + program
        frame.appendChild(el("div", "vc-awarded", "is hereby awarded to"));
        frame.appendChild(el("div", "vc-name", c.holder_name));
        var prog = el("div", "vc-prog"); prog.appendChild(document.createTextNode("for completing "));
        prog.appendChild(el("strong", null, c.program_name)); frame.appendChild(prog);

        // Details
        var grid = el("div", "vc-grid");
        cell(grid, "Issued by", "Crea8it Studio");
        var org = (c.org_name || "").trim();
        if (org && OWN_ORGS.indexOf(org.toLowerCase()) === -1) cell(grid, "Delivered by", org);
        if (c.cohort_label) cell(grid, "Cohort", c.cohort_label);
        cell(grid, "Date issued", fmtDate(c.issued_at));
        if (c.duration_weeks) cell(grid, "Duration", c.duration_weeks + " weeks");
        frame.appendChild(grid);

        // ID + actions
        var idrow = el("div", "vc-idrow");
        idrow.appendChild(el("span", "vc-idlabel", "Certificate ID"));
        idrow.appendChild(el("code", "vc-id", code));
        frame.appendChild(idrow);

        var actions = el("div", "vc-actions");
        var b1 = el("button", "vc-btn", "Copy verification link"); b1.type = "button";
        b1.addEventListener("click", function () { copyText(VERIFY_BASE + encodeURIComponent(code), b1, "Link copied"); });
        var b2 = el("button", "vc-btn", "Copy ID"); b2.type = "button";
        b2.addEventListener("click", function () { copyText(code, b2, "ID copied"); });
        var rep = el("a", "vc-btn vc-btn-quiet", "Report a problem");
        rep.href = "mailto:" + REPORT_EMAIL + "?subject=" + encodeURIComponent("Certificate verification issue: " + code);
        actions.appendChild(b1); actions.appendChild(b2); actions.appendChild(rep);
        frame.appendChild(actions);

        frame.appendChild(el("div", "vc-checked", "Checked against Crea8it\u2019s records on " + checkedAt()));
        card.appendChild(frame);
        show(card);
    }

    function verify(raw) {
        var code = (raw || "").trim().toUpperCase();
        input.value = code;
        if (!code) { out.hidden = true; return; }
        if (!CODE_RE.test(code)) {
            message("none", "Not recognised", ICON_BAD,
                "That doesn\u2019t look like a Crea8it certificate ID. IDs look like C8L-2026-K7QX9PMA \u2014 check it against the certificate and try again.");
            return;
        }
        if (!configured()) {
            message("none", "Not set up yet", ICON_BAD, "Verification isn\u2019t switched on for this site yet. Please check back soon.");
            return;
        }
        btn.disabled = true;
        show(el("p", "verify-msg", "Checking\u2026"));
        fetch(SUPABASE_URL.replace(/\/$/, "") + "/rest/v1/rpc/verify_certificate", {
            method: "POST",
            headers: { "Content-Type": "application/json", "apikey": SUPABASE_ANON_KEY, "Authorization": "Bearer " + SUPABASE_ANON_KEY },
            body: JSON.stringify({ p_code: code })
        }).then(function (r) {
            if (!r.ok) throw new Error("HTTP " + r.status);
            return r.json();
        }).then(function (rows) {
            if (rows && rows.length) render(code, rows[0]);
            else message("none", "No match", ICON_BAD,
                "We couldn\u2019t find a certificate with that ID. Check for typos \u2014 if it\u2019s correct, the certificate may not be genuine.");
        }).catch(function () {
            message("none", "Couldn\u2019t check", ICON_BAD, "We couldn\u2019t reach the verification service. Check your connection and try again.");
        }).then(function () { btn.disabled = false; });
    }

    form.addEventListener("submit", function (e) {
        e.preventDefault();
        var code = input.value.trim().toUpperCase();
        if (history.replaceState) history.replaceState(null, "", code ? "?id=" + encodeURIComponent(code) : location.pathname);
        verify(code);
    });

    var q = new URLSearchParams(location.search).get("id");
    if (q) verify(q);
})();
