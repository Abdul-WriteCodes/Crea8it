/*
  Crea8it — shared content data
  ------------------------------
  Add a program, resource, or testimonial ONCE here and it will show up
  everywhere it's supposed to: the homepage teaser sections AND the
  dedicated full pages (programs.html / resources.html / impact.html).

  Nothing here needs a build step — it's plain JS read directly by
  assets/js/render.js in each page.
*/

const PROGRAMS = [
    {
        id: "career-acceleration",
        title: "Career Acceleration",
        icon: "icon-mic",
        tag: "Active",
        tagClass: "open",
        img: "assets/Scr1.jpg",
        rot: "rot--1",
        description: "A career launch program for ambitious builders ready to gain valuable AI-era skills and real opportunities.",
        priceLabel: "--",
        ctaText: "Register →",
        ctaLink: "https://wa.me/2348096506034?text=Hi%20Abdul%2C%20I%27m%20interested%20in%20the%20AI%20Career%20Acceleration%20program%20-%20saw%20it%20on%20Crea8it.%20Can%20you%20tell%20me%20more%3F"
    },
        {
        id: "data-analysis",
        title: "Data Analysis",
        icon: "icon-toolbox",
        tag: "Active",
        tagClass: "open",
        img: "assets/Scr4.jpg",
        rot: "rot--4",
        description: "A hands-on program for turning raw, messy data into insights that actually inform decisions — cleaning, running the right statistical tests, and presenting findings that hold up.",
        priceLabel: "--", // TODO: add price
        ctaText: "Register →",
        ctaLink: "https://wa.me/2348096506034?text=Hi%20Abdul%2C%20I%27m%20interested%20in%20the%20Data%20Analysis%20program%20-%20saw%20it%20on%20Crea8it.%20Can%20you%20tell%20me%20more%3F"
    },
    {
        id: "research-data-analysis",
        title: "Research and Data Analysis",
        icon: "icon-flask",
        tag: "Active",
        tagClass: "open",
        img: "assets/Scr5.jpg",
        rot: "rot--5",
        description: "A hands-on program covering the full research pipeline — from framing the right question and designing the study, to collecting, cleaning, and analyzing the data that answers it.",
        priceLabel: "--", // TODO: add price
        ctaText: "Register →",
        ctaLink: "https://wa.me/2348096506034?text=Hi%20Abdul%2C%20I%27m%20interested%20in%20the%20Research%20and%20Data%20Analysis%20program%20-%20saw%20it%20on%20Crea8it.%20Can%20you%20tell%20me%20more%3F"
    },
    {
        id: "research-technical-writing",
        title: "Research and Technical Writing",
        icon: "icon-book",
        tag: "Active",
        tagClass: "open",
        img: "assets/Scr6.jpg",
        rot: "rot--6",
        description: "A hands-on program for developing and monetizing academic research writing and technical/business writing — real skills, real paid output.",
        priceLabel: "--", // TODO: add price
        ctaText: "Register →",
        ctaLink: "https://wa.me/2348096506034?text=Hi%20Abdul%2C%20I%27m%20interested%20in%20the%20Research%20and%20Technical%20Writing%20program%20-%20saw%20it%20on%20Crea8it.%20Can%20you%20tell%20me%20more%3F"
    },
    {
        id: "build-in-public",
        title: "Build in Public Challenge",
        icon: null,
        tag: "Active",
        tagClass: "open",
        img: "assets/Scr2.jpg",
        rot: "rot--2",
        description: "A hands-on execution program that encourages builders to stop overthinking and start shipping.",
        priceLabel: "--",
        ctaText: "Join Challenge →",
        ctaLink: "https://wa.me/2348096506034?text=Hi%20Abdul%2C%20I%27d%20like%20to%20join%20the%20Build%20in%20Public%20Challenge%20-%20saw%20it%20on%20Crea8it."
    },
    {
        id: "zero-to-one",
        title: "Zero to 1",
        icon: "icon-flask",
        tag: "Active",
        tagClass: "open",
        img: "assets/Scr3.jpg",
        rot: "rot--3",
        description: "An idea validation and startup launch program for founders and indie hackers building real businesses from scratch. You don't just learn here — you EXECUTE.",
        priceLabel: "--",
        ctaText: "Register →",
        ctaLink: "https://wa.me/2348096506034?text=Hi%20Abdul%2C%20I%27d%20like%20to%20join%20the%20Zero%20to%201%20lab%20program-%20saw%20it%20on%20Crea8it."
    }
];

const RESOURCES = [
    {
        id: "enter-ai",
        title: "Enter AI",
        icon: "icon-book",
        tag: "Playbook",
        tagClass: "open",
        img: "assets/EntAI.jpg",
        rot: "rot--4",
        priceLabel: "₦5,000",
        priceSticker: "₦5,000",
        stickerStyle: "",
        description: "A comprehensive guide for AI career launch. Over 10 downloads 📥 and counting · 20% of active readers 🧑‍🏫 have successfully broken into AI 🚀 · No CS degree is not a barrier · real steps and tested strategies 🧩.",
        ctaText: "Get Book →",
        ctaLink: "https://flutterwave.com/pay/uuzhcwanejde?dl=1"
    },
    {
        id: "talk-to-the-machine",
        title: "Talk to the Machine",
        icon: "icon-book",
        tag: "Playbook",
        tagClass: "soon",
        img: "assets/T2M.jpeg",
        rot: "rot--5",
        priceLabel: "Free",
        priceSticker: "Free",
        stickerStyle: "background:var(--accent3);color:#0c1a15;",
        description: "A practical field guide to working with AI tools day-to-day — prompts, workflows, and mental models for getting real output instead of generic answers.",
        ctaText: "Get Book →",
        ctaLink: "https://app.box.com/s/qluhjskz4smsz0158nij9qmz4a28al6d"
    }
];

/*
  Two testimonial shapes are supported:
  - type "photo"  → a screenshot / shout-out image, shown in the polaroid carousel
  - type "quote"  → a written testimonial, shown as a quote card on impact.html
  Mix and match freely — add as many of either as you like.
*/
const TESTIMONIALS = [
    {
        id: "testx1",
        type: "photo",
        img: "assets/Testx1.png",
        alt: "Reader testimonial 1",
        caption: "reader love 💚"
    }
    {
       id: "testx2",
       type: "quote",
       quote: "Crea8it took me from 'I have an idea' to a shipped product in 3 weeks.",
       name: "Jane Doe",
       role: "Founder, XYZ"
    }
];
