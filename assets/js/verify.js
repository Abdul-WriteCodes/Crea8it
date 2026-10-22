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

    var SUPABASE_URL      = "PASTE_SUPABASE_PROJECT_URL";   // e.g. https://abcdxyz.supabase.co
    var SUPABASE_ANON_KEY = "PASTE_SUPABASE_ANON_KEY";

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

    function badge(kind, text, path) {
        var b = el("div", "verify-badge " + kind);
        var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.setAttribute("viewBox", "0 0 18 18"); svg.setAttribute("aria-hidden", "true");
        var p = document.createElementNS("http://www.w3.org/2000/svg", "path");
        p.setAttribute("d", path); svg.appendChild(p);
        b.appendChild(svg); b.appendChild(document.createTextNode(text));
        return b;
    }

    function show(node) { out.replaceChildren(node); out.hidden = false; }

    function message(kind, badgeText, path, text) {
        var card = el("div", "verify-card");
        card.appendChild(badge(kind, badgeText, path));
        card.appendChild(el("p", "verify-msg", text));
        show(card);
    }

    function meta(dl, label, value) {
        var w = el("div");
        w.appendChild(el("dt", null, label)); w.appendChild(el("dd", null, value));
        dl.appendChild(w);
    }

    function render(code, c) {
        var valid = c.status === "valid";
        var card = el("div", "verify-card");
        card.appendChild(valid ? badge("ok", "Valid certificate", ICON_OK)
                               : badge("bad", "Revoked \u2014 no longer valid", ICON_BAD));
        var who = el("div");
        who.appendChild(el("div", "verify-label", "Awarded to"));
        who.appendChild(el("div", "verify-name", c.holder_name));
        var prog = el("div", "verify-prog"); prog.appendChild(document.createTextNode("for completing "));
        prog.appendChild(el("strong", null, c.program_name)); who.appendChild(prog);
        card.appendChild(who);
        var dl = el("dl", "verify-meta");
        meta(dl, "Organisation", c.org_name);
        if (c.cohort_label) meta(dl, "Cohort", c.cohort_label);
        meta(dl, "Date issued", fmtDate(c.issued_at));
        if (c.duration_weeks) meta(dl, "Duration", c.duration_weeks + " weeks");
        card.appendChild(dl);
        card.appendChild(el("div", "verify-id", "ID " + code));
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
