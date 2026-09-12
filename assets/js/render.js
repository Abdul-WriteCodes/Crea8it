/*
  Crea8it — shared render functions
  ----------------------------------
  Reads from assets/js/site-data.js and paints cards into whichever
  container is on the current page. Load site-data.js BEFORE this file.
*/

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
