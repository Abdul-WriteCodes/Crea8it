/*
  Crea8it — shared site shell (nav + footer)
  ------------------------------------------
  Every page holds <div id="site-nav"></div> and <div id="site-footer"></div>.
  This block builds them, so a nav/footer change is made ONCE, here.
*/
(function () {
    "use strict";

    var LAB_URL   = "https://lab.crea8it.com/";
    var COMMUNITY = "https://chat.whatsapp.com/Gbm13AqaNSt24MAxszzkcB";

    // [href, label, icon]  — items with a #hash are never marked "active"
    var NAV = [
        ["/",                        "Home",           "icon-home"],
        ["programs.html",            "Programs",       "icon-rocket"],
        ["resources.html",           "Resources",      "icon-book-open"],
        ["projects.html",            "Products",       "icon-toolbox"],
        ["impact.html",              "Impact",         "icon-trophy"],
        ["/#submit-request",         "Submit Request", "icon-send"]
    ];

    // [heading, [[href, label, opensNewTab]]]
    var FOOTER = [
        ["Explore",       [["/","Home"],["programs.html","Programs"],["resources.html","Resources"],["projects.html","Products"],["impact.html","Impacts"]]],
        ["Organizations", [["run-a-cohort.html","Run a Cohort"],["organisation-terms.html","Organisation Terms"]]],
        ["Connect",       [[LAB_URL,"Enter Lab"],[COMMUNITY,"Join on WhatsApp",true]]],
        ["Legal & Help",  [["faqs.html","FAQs"],["terms.html","Terms of Service"],["privacy.html","Privacy & Cookies"]]]
    ];

    var SOCIALS = `<div class="footer-socials"><!-- Twitter / X --><a href="https://twitter.com/abdul_git07" target="_blank" rel="noopener" aria-label="Twitter / X"><svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.746l7.73-8.835L1.254 2.25H8.08l4.262 5.636 5.901-5.636Zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg></a><!-- LinkedIn --><a href="https://linkedin.com/in/anafiabdul" target="_blank" rel="noopener" aria-label="LinkedIn"><svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg></a><!-- Blogger --><a href="https://abdulbuilds.blogspot.com" target="_blank" rel="noopener" aria-label="Blog"><svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M21.976 24H2.026C.9 24 0 23.1 0 21.976V2.026C0 .9.9 0 2.026 0h19.95C23.1 0 24 .9 24 2.026v19.95C24 23.1 23.1 24 21.976 24zm-3.953-8.353c0-1.18-.966-2.135-2.15-2.135h-.592c-.363 0-.66-.295-.66-.655v-1.714c0-1.18-.966-2.136-2.15-2.136H8.13c-1.184 0-2.15.956-2.15 2.136v5.358c0 1.18.966 2.136 2.15 2.136h9.743c1.184 0 2.15-.956 2.15-2.136v-.854zm0-7.177c0-1.18-.966-2.136-2.15-2.136H8.13c-1.184 0-2.15.956-2.15 2.136v.427c0 1.18.966 2.136 2.15 2.136h7.743c1.184 0 2.15-.956 2.15-2.136v-.427zm-3.103 7.603H9.08a.642.642 0 0 1 0-1.284h5.84a.642.642 0 0 1 0 1.284zm0-2.991H9.08a.642.642 0 0 1 0-1.284h5.84a.642.642 0 0 1 0 1.284zm0-4.275H9.08a.642.642 0 0 1 0-1.284h5.84a.642.642 0 0 1 0 1.284z"/></svg></a></div>`;

    function pageKey() {
        var p = location.pathname.split("/").pop() || "index";
        return p.replace(/\.html$/, "");
    }
    function hrefKey(h) { return h.split("#")[0].replace(/^\//, "").replace(/\.html$/, "") || "index"; }
    function isActive(h) {
        return h.indexOf("#") === -1 && h.indexOf("http") !== 0 && hrefKey(h) === pageKey();
    }

    function navHTML() {
        var links = NAV.map(function (n) {
            var cls = isActive(n[0]) ? ' class="active" aria-current="page"' : "";
            return '<a href="' + n[0] + '"' + cls + '>' + n[1] +
                   '<svg class="icon icon-trail"><use href="#' + n[2] + '"/></svg></a>';
        }).join("");
        return '<nav aria-label="Main">' +
            '<div class="container nav-wrapper">' +
              '<a href="/" class="logo-block" style="text-decoration:none;cursor:pointer;">' +
                '<div class="logo">Crea8it Studio</div><div class="logo-sub"></div></a>' +
              '<button class="nav-toggle" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="nav-links">' +
                '<span></span><span></span><span></span></button>' +
              '<div class="nav-links" id="nav-links">' + links +
                '<a href="' + LAB_URL + '" class="nav-lab">Enter Lab' +
                '<svg class="icon icon-trail"><use href="#icon-terminal"/></svg></a>' +
              '</div>' +
            '</div></nav>';
    }

    function footerHTML() {
        var cols = FOOTER.map(function (c) {
            var items = c[1].map(function (l) {
                var cls = isActive(l[0]) ? ' class="active"' : "";
                var ext = l[2] ? ' target="_blank" rel="noopener"' : "";
                return '<a href="' + l[0] + '"' + cls + ext + '>' + l[1] + '</a>';
            }).join("");
            return '<div class="footer-links-col"><div class="footer-links-heading">' + c[0] +
                   '</div><nav class="footer-links">' + items + '</nav></div>';
        }).join("");
        return '<footer><div class="container footer-inner">' +
            '<div class="footer-logo">Crea8it Studio</div>' +
            '<p class="footer-tagline">BUILD<svg class="icon icon-trail"><use href="#icon-gear"/></svg> ° LAUNCH<svg class="icon icon-trail"><use href="#icon-rocket"/></svg> ° LEARN<svg class="icon icon-trail"><use href="#icon-adapt"/></svg> ° WIN<svg class="icon icon-trail"><use href="#icon-trophy"/></svg></p>' +
            '<div class="footer-columns">' + cols + '</div>' +
            SOCIALS +
            '<p class="footer-copy">© ' + new Date().getFullYear() + ' Crea8it Studio — Built for builders.</p>' +
            '</div></footer>';
    }

    function wireToggle() {
        var nav = document.querySelector("nav[aria-label='Main']");
        if (!nav) return;
        var btn = nav.querySelector(".nav-toggle");
        var panel = nav.querySelector(".nav-links");
        function setOpen(open) {
            panel.classList.toggle("open", open);
            btn.setAttribute("aria-expanded", open ? "true" : "false");
            btn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
        }
        btn.addEventListener("click", function (e) {
            e.stopPropagation();
            setOpen(!panel.classList.contains("open"));
        });
        panel.addEventListener("click", function (e) { if (e.target.closest("a")) setOpen(false); });
        document.addEventListener("click", function (e) { if (!nav.contains(e.target)) setOpen(false); });
        document.addEventListener("keydown", function (e) { if (e.key === "Escape") setOpen(false); });
        window.addEventListener("resize", function () { if (window.innerWidth > 768) setOpen(false); });
    }

    // "Home" icon isn't in the per-page sprite, so add it once here
    function addHomeIcon() {
        if (document.getElementById("icon-home")) return;
        var s = document.createElement("div");
        s.innerHTML = '<svg style="display:none" aria-hidden="true"><symbol id="icon-home" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 11l9-8 9 8"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/></symbol></svg>';
        document.body.insertBefore(s.firstChild, document.body.firstChild);
    }

    function mount() {
        addHomeIcon();
        var n = document.getElementById("site-nav");
        var f = document.getElementById("site-footer");
        if (n) n.outerHTML = navHTML();      // outerHTML (not innerHTML) keeps nav a direct child,
        if (f) f.outerHTML = footerHTML();   // so position:sticky still works
        wireToggle();
    }

    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount);
    else mount();
})();

/*
  Crea8it — shared render functions
  ----------------------------------
  Reads from assets/js/site-data.js and paints cards into whichever
  container is on the current page. Load site-data.js BEFORE this file.
*/

function programDetailsHTML(p) {
    if (!p.covers || !p.covers.length) return "";
    const who = p.audience ? `<p class="cd-label">Program Structure</p><p>${p.audience}</p>` : "";
    const items = p.covers.map(c => `<li>${c}</li>`).join("");
    return `
        <details class="card-details">
            <summary>What's inside</summary>
            <div class="card-details-body">
                ${who}
                <p class="cd-label">What it Covers</p>
                <ul>${items}</ul>
            </div>
        </details>`;
}

function programCardHTML(p) {
    const iconSpan = p.icon ? `<svg class="icon icon-lead"><use href="#${p.icon}"/></svg>` : "";
    const priceInner = p.priceLabel || "Coming Soon";
    return `
<div class="card index-card tilt-card ${p.rot || ""}">
    <div class="pin"></div>
    <div class="card-photo">
        <img src="${p.img}" alt="${p.title}">
    </div>
    <div class="card-body">
        <span class="card-tag ${p.tagClass}">${iconSpan}${p.tag}</span>
        <h3>${p.title}</h3>
        <p>${p.description}</p>
        ${programDetailsHTML(p)}
        <div class="card-footer">
            <div class="price program-price">${priceInner}</div>
            <a href="${p.ctaLink}" class="btn-buy" target="_blank" rel="noopener">${p.ctaText}</a>
        </div>
    </div>
</div>`;
}

function resourceCardHTML(r) {
    const iconSpan = r.icon ? `<svg class="icon icon-lead"><use href="#${r.icon}"/></svg>` : "";
    return `
<div class="card index-card tilt-card ${r.rot || ""}">
    <div class="pin"></div>
    <div class="price-sticker" style="${r.stickerStyle || ""}">${r.priceSticker}</div>
    <div class="card-photo playbook-photo">
        <img src="${r.img}" alt="${r.title} cover">
    </div>
    <div class="card-body">
        <span class="card-tag ${r.tagClass}">${iconSpan}${r.tag}</span>
        <h3>${r.title}</h3>
        <p>${r.description}</p>
        <div class="card-footer">
            <div class="price">${r.priceLabel}</div>
            <a href="${r.ctaLink}" class="btn-buy">${r.ctaText}</a>
        </div>
    </div>
</div>`;
}

function quoteCardHTML(t, rot) {
    return `
<div class="card index-card tilt-card quote-card ${rot || ""}">
    <div class="pin"></div>
    <div class="card-body">
        <span class="quote-mark">"</span>
        <p class="quote-text">${t.quote}</p>
        <div class="quote-who"><strong>${t.name || "Anonymous"}</strong>${t.role ? " — " + t.role : ""}</div>
    </div>
</div>`;
}

function renderList(containerId, items, cardFn, limit) {
    const el = document.getElementById(containerId);
    if (!el) return;
    const list = limit ? items.slice(0, limit) : items;
    el.innerHTML = list.map(cardFn).join("\n");
}

function renderPrograms(containerId, limit) {
    renderList(containerId, PROGRAMS, programCardHTML, limit);
}

function renderResources(containerId, limit) {
    renderList(containerId, RESOURCES, resourceCardHTML, limit);
}

function renderQuoteTestimonials(containerId, limit, sectionIdToHideIfEmpty) {
    const quotes = TESTIMONIALS.filter(t => t.type === "quote");
    const rots = ["rot--1", "rot--2", "rot--3", "rot--4", "rot--5"];
    const el = document.getElementById(containerId);
    if (!el) return;

    if (!quotes.length && sectionIdToHideIfEmpty) {
        const section = document.getElementById(sectionIdToHideIfEmpty);
        if (section) section.style.display = "none";
        return;
    }

    const list = limit ? quotes.slice(0, limit) : quotes;
    el.innerHTML = list.map((t, i) => quoteCardHTML(t, rots[i % rots.length])).join("\n");
}

/* Builds the polaroid carousel slides/dots from photo-type testimonials,
   then wires up the same drag/swipe behaviour as before. */
function renderPhotoCarousel(wrapSelector) {
    const wrap = document.querySelector(wrapSelector);
    if (!wrap) return;
    const photos = TESTIMONIALS.filter(t => t.type === "photo");
    if (!photos.length) { wrap.style.display = "none"; return; }

    const track = wrap.querySelector(".carousel-track");
    const dotsWrap = wrap.querySelector(".carousel-dots");

    track.innerHTML = photos.map(t => `
<div class="carousel-slide">
    <div class="polaroid testimonial-polaroid">
        <div class="tape tc"></div>
        <img src="${t.img}" alt="${t.alt || ""}">
        <figcaption class="hand">${t.caption || ""}</figcaption>
    </div>
</div>`).join("\n");

    dotsWrap.innerHTML = photos.map((_, i) => `<span class="dot${i === 0 ? " active" : ""}"></span>`).join("\n");

    initCarousel(wrap);
}

function initCarousel(wrap) {
    const track = wrap.querySelector(".carousel-track");
    const slides = wrap.querySelectorAll(".carousel-slide");
    const dots = wrap.querySelectorAll(".dot");
    const prev = wrap.querySelector(".carousel-prev");
    const next = wrap.querySelector(".carousel-next");
    const total = slides.length;
    if (!total) return;
    let current = 0;

    function goTo(index) {
        current = (index + total) % total;
        track.style.transform = `translateX(-${current * 100}%)`;
        dots.forEach((d, i) => d.classList.toggle("active", i === current));
    }

    if (prev) prev.addEventListener("click", () => goTo(current - 1));
    if (next) next.addEventListener("click", () => goTo(current + 1));
    dots.forEach((d, i) => d.addEventListener("click", () => goTo(i)));

    let startX = 0;
    track.addEventListener("touchstart", e => { startX = e.touches[0].clientX; }, { passive: true });
    track.addEventListener("touchend", e => {
        const diff = startX - e.changedTouches[0].clientX;
        if (Math.abs(diff) > 40) goTo(diff > 0 ? current + 1 : current - 1);
    });

    let mouseStartX = 0, isDragging = false;
    track.addEventListener("mousedown", e => { isDragging = true; mouseStartX = e.clientX; });
    track.addEventListener("mouseup", e => {
        if (!isDragging) return;
        isDragging = false;
        const diff = mouseStartX - e.clientX;
        if (Math.abs(diff) > 40) goTo(diff > 0 ? current + 1 : current - 1);
    });
    track.addEventListener("mouseleave", () => { isDragging = false; });
}

function initCountdowns() {
    function pad(n) { return String(n).padStart(2, "0"); }

    function buildCountdown(el, launchDate) {
        function tick() {
            const now = new Date();
            const diff = launchDate - now;

            if (diff <= 0) {
                el.innerHTML = '<span class="price-open"><svg class="icon icon-lead"><use href="#icon-dot"/></svg>Now Open!</span>';
                return;
            }

            const days = Math.floor(diff / (1000 * 60 * 60 * 24));
            const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            const secs = Math.floor((diff % (1000 * 60)) / 1000);

            el.innerHTML = `
                <div class="countdown">
                    <div class="cd-block"><span class="cd-num">${pad(days)}</span><span class="cd-label">Days</span></div>
                    <span class="cd-sep">:</span>
                    <div class="cd-block"><span class="cd-num">${pad(hours)}</span><span class="cd-label">Hrs</span></div>
                    <span class="cd-sep">:</span>
                    <div class="cd-block"><span class="cd-num">${pad(mins)}</span><span class="cd-label">Min</span></div>
                    <span class="cd-sep">:</span>
                    <div class="cd-block"><span class="cd-num">${pad(secs)}</span><span class="cd-label">Sec</span></div>
                </div>`;
        }

        tick();
        setInterval(tick, 1000);
    }

    document.querySelectorAll(".card[data-launch]").forEach(function (card) {
        const raw = card.getAttribute("data-launch");
        if (!raw) return;

        const launchDate = new Date(raw);
        if (isNaN(launchDate)) return;

        const priceEl = card.querySelector(".program-price");
        if (priceEl) buildCountdown(priceEl, launchDate);
    });
}

/* Flip-polaroid hero photo (used on index + shelf-style hero sections) */
function initFlipPolaroid(wrapId, captionId, captions) {
    const wrap = document.getElementById(wrapId);
    if (!wrap) return;

    const imgs = wrap.querySelectorAll(".flip-img");
    const captionEl = document.getElementById(captionId);
    if (imgs.length < 2) return;

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduceMotion) return;

    let current = 0;
    setInterval(function () {
        imgs[current].classList.remove("active");
        current = (current + 1) % imgs.length;
        imgs[current].classList.add("active");
        if (captionEl && captions[current]) captionEl.textContent = captions[current];
    }, 4000);
  }
