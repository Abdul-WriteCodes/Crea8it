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

    // Same mark as the printed certificate: the Crea8it Lab logo inside an ink + brass ring.
    // The image is a static file (no database content). If it can't load, the ring is removed so a
    // broken-image icon is never shown and the card still reads correctly with just the name.
    var LOGO_SRC = "assets/images/crea8it-logo.png";
    function emblem() {
        var ring = el("div", "vc-emblem");
        var img = document.createElement("img");
        img.className = "vc-logo"; img.src = LOGO_SRC; img.alt = "Crea8it Lab logo";
        img.width = 64; img.height = 55; img.decoding = "async";
        img.addEventListener("error", function () { if (ring.parentNode) ring.parentNode.removeChild(ring); });
        ring.appendChild(img);
        return ring;
    }

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
        return new Date().toLocaleString("en-GB", { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" });
    }

    function render(code, c) {
        var valid = c.status === "valid";
        var card = el("div", "verify-cert " + (valid ? "is-valid" : "is-revoked"));
        var frame = el("div", "vc-frame");

        // Brand header: ring emblem above the issuer name, as on the printed certificate
        var brand = el("div", "vc-brand");
        brand.appendChild(emblem());
        brand.appendChild(el("div", "vc-word", "CREA8IT STUDIO"));
        frame.appendChild(brand);

        // Status
        var status = el("div", "vc-status");
        var seal = el("div", "vc-seal"); seal.appendChild(icon(valid ? ICON_OK : ICON_BAD));
        status.appendChild(seal);
        var st = el("div", "vc-status-text");
        st.appendChild(el("div", "vc-status-title", valid ? "Verified certificate" : "Certificate revoked"));
        st.appendChild(el("div", "vc-status-sub", valid
            ? "Issued by Crea8it Studio."
            : "No longer valid."));
        status.appendChild(st);
        frame.appendChild(status);

        // Holder + program
        frame.appendChild(el("div", "vc-awarded", "is hereby awarded to"));
        frame.appendChild(el("div", "vc-name", c.holder_name));
        var prog = el("div", "vc-prog"); prog.appendChild(document.createTextNode("for completing "));
        prog.appendChild(el("strong", null, c.program_name)); frame.appendChild(prog);

        // Details ("Issued by" is already in the header and status, so it is not repeated)
        var grid = el("div", "vc-grid");
        cell(grid, "Date issued", fmtDate(c.issued_at));
        if (c.duration_weeks) cell(grid, "Duration", c.duration_weeks + " weeks");
        if (c.cohort_label) cell(grid, "Cohort", c.cohort_label);
        var org = (c.org_name || "").trim();
        if (org && OWN_ORGS.indexOf(org.toLowerCase()) === -1) cell(grid, "Delivered by", org);
        frame.appendChild(grid);

        // ID (tap to copy) + actions
        var idb = el("button", "vc-id"); idb.type = "button";
        idb.setAttribute("aria-label", "Copy certificate ID " + code);
        idb.appendChild(el("span", "vc-idlabel", "ID"));
        idb.appendChild(el("span", "vc-idcode", code));
        var idcopy = el("span", "vc-idcopy", "Copy"); idb.appendChild(idcopy);
        idb.addEventListener("click", function () { copyText(code, idcopy, "Copied"); });
        frame.appendChild(idb);

        var actions = el("div", "vc-actions");
        var b1 = el("button", "vc-btn", "Copy link"); b1.type = "button";
        b1.addEventListener("click", function () { copyText(VERIFY_BASE + encodeURIComponent(code), b1, "Link copied"); });
        var rep = el("a", "vc-btn vc-btn-quiet", "Report a problem");
        rep.href = "mailto:" + REPORT_EMAIL + "?subject=" + encodeURIComponent("Certificate verification issue: " + code);
        actions.appendChild(b1); actions.appendChild(rep);
        frame.appendChild(actions);

        frame.appendChild(el("div", "vc-checked", "Checked " + checkedAt()));
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
