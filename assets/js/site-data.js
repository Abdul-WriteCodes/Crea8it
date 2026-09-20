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
        title: "Break into Tech",
        icon: "icon-mic",
        tag: "Active",
        tagClass: "open",
        img: "assets/Brk2tech.jpeg",
        rot: "rot--1",
        description: "A career launch program for ambitious tech career aspirants ready to break into tech, learn valuable AI-era skills and access real opportunities.",
        audience: "Three(3) weeks, 9 Live Sessions, and 3 Task Assessments.", // DRAFT: edit to match the real program
        covers: ["Tech Ecosystem Breakdown", "Tech Career Direction & Specialisation Discovery", "Digital, AI & Professional Skills Development", "Personalised Tech Entry Roadmap & Positioning Strategy"],
        priceLabel: "Free",
        ctaText: "Register →",
        ctaLink: "https://wa.me/2348096506034?text=Hi%20Abdul%2C%20I%27m%20interested%20in%20the%20AI%20Career%20Acceleration%20program%20-%20saw%20it%20on%20Crea8it.%20Can%20you%20tell%20me%20more%3F"
    },
        {
        id: "data-analysis",
        title: "Quant + Qual Analysis",
        icon: "icon-toolbox",
        tag: "Active",
        tagClass: "open",
        img: "assets/Q&Q.jpeg",
        rot: "rot--4",
        description: "A hands-on program for turning raw, messy data into insights that actually inform decisions — cleaning, running the right statistical tests, and presenting findings that hold up.",
        audience: "Six(6) Weeks, 18 Live Sessions, 6 Tasks Assessments + 1 Capstone Project.", // DRAFT: edit to match the real program
        covers: ["Quantitative Data Analysis Mastery", "Qualitative Data Analysis Mastery", "Research Data Management", "Skill Monetisation & Distribution"],
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
        img: "assets/R&D.jpeg",
        rot: "rot--5",
        description: "A hands-on program covering the full research pipeline — from framing the right question and designing the study, to collecting, cleaning, and analyzing the data that answers it.",
        audience: "Six(6) Weeks, 18 Live Sessions, 6 Tasks Assessmemts and 1 Capstone Project.", // DRAFT: edit to match the real program
        covers: ["Level 7 Writing Skill for Research & Custom Essay", "Advanced Data Analysis with Statistical Software", "End-to-End Research Methodology", "Research Skill Monetisation & Distribution"],
        priceLabel: "--", // TODO: add price
        ctaText: "Register →",
        ctaLink: "https://wa.me/2348096506034?text=Hi%20Abdul%2C%20I%27m%20interested%20in%20the%20Research%20and%20Data%20Analysis%20program%20-%20saw%20it%20on%20Crea8it.%20Can%20you%20tell%20me%20more%3F"
    },
    {
        id: "research-technical-writing",
        title: "Technical Writing",
        icon: "icon-book",
        tag: "Active",
        tagClass: "open",
        img: "assets/Techwrite.jpeg",
        rot: "rot--6",
        description: "A hands-on program for developing and monetizing Technical and business writing skills.",
        audience: "Four(4) Weeks, 12 Live Sessions, 4 Tasks & 1 Capstone Project.", // DRAFT: edit to match the real program
        covers: ["Technical & Business Writing Foundations", "Information Architecture & Documentation", "Information Mapping & Source Evaluation", "Technical Writing Portfolio Development & Monetization"],
        priceLabel: "--", // TODO: add price
        ctaText: "Register →",
        ctaLink: "https://wa.me/2348096506034?text=Hi%20Abdul%2C%20I%27m%20interested%20in%20the%20Research%20and%20Technical%20Writing%20program%20-%20saw%20it%20on%20Crea8it.%20Can%20you%20tell%20me%20more%3F"
    },
    {
        id: "build-in-public",
        title: "Applied AI and Productivity",
        icon: null,
        tag: "Active",
        tagClass: "open",
        img: "assets/AppliedAI.jpeg",
        rot: "rot--2",
        description: "A hands-on programme for learning how to use AI tools, build AI-powered workflows, automate tasks and apply AI to real-world professional and business problems..",
        audience: "Four(4) Weeks, 12 Live Sessions, 4 Tasks and 1 Capstone Projects.", // DRAFT: edit to match the real program
        covers: ["AI Foundation & Prompt Mastery", "AI Tools Mastery & Application", "AI Workflow & Integration", "AI Skills Monetisation & Distribution"],
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
        audience: "Founders and indie hackers building real businesses from scratch.", // DRAFT: edit to match the real program
        covers: ["Validating your idea", "Launching your startup", "Executing: you don't just learn, you do the work"],
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
];
