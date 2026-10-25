/*
  Crea8it — shared content data
  ------------------------------
  Add a program, resource, or testimonial ONCE here and it will show up
  everywhere it's supposed to: the homepage teaser sections AND the
  dedicated full pages (programs.html / resources.html / impact.html).

  Nothing here needs a build step — it's plain JS read directly by
  assets/js/render.js in each page.
*/

// ctaLink opens register.html (form). whatsappLink is shown AFTER someone registers.
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
        ctaLink: "register.html?program=career-acceleration",
        whatsappLink: "https://wa.me/2348096506034?text=Hi%20Abdul%2C%20I%27m%20interested%20in%20the%20AI%20Career%20Acceleration%20program%20-%20saw%20it%20on%20Crea8it.%20Can%20you%20tell%20me%20more%3F"
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
        ctaLink: "register.html?program=data-analysis",
        whatsappLink: "https://wa.me/2348096506034?text=Hi%20Abdul%2C%20I%27m%20interested%20in%20the%20Data%20Analysis%20program%20-%20saw%20it%20on%20Crea8it.%20Can%20you%20tell%20me%20more%3F"
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
        ctaLink: "register.html?program=research-data-analysis",
        whatsappLink: "https://wa.me/2348096506034?text=Hi%20Abdul%2C%20I%27m%20interested%20in%20the%20Research%20and%20Data%20Analysis%20program%20-%20saw%20it%20on%20Crea8it.%20Can%20you%20tell%20me%20more%3F"
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
        ctaLink: "register.html?program=research-technical-writing",
        whatsappLink: "https://wa.me/2348096506034?text=Hi%20Abdul%2C%20I%27m%20interested%20in%20the%20Research%20and%20Technical%20Writing%20program%20-%20saw%20it%20on%20Crea8it.%20Can%20you%20tell%20me%20more%3F"
    },
     {
        id: "natural-language-processing",
        title: "Natural Language Processing",
        icon: "icon-adapt",
        tag: "Active",
        tagClass: "open",
        img: "assets/prog-nlp.jpg",
        rot: "rot--1",
        description: "A hands-on program for teaching machines to understand human language — from text preprocessing and classical techniques to transformers and building real LLM-powered applications.",
        audience: "Eight(8) Weeks, 24 Live Sessions, 8 Tasks & 1 Capstone Project.", // DRAFT: edit to match the real program
        covers: ["Text & Language Fundamentals", "Classical NLP Techniques & Pipelines", "Transformers & LLM-Powered Applications", "NLP Portfolio Project & Skill Monetisation"],
        priceLabel: "--", // TODO: add price
        ctaText: "Register →",
        ctaLink: "register.html?program=natural-language-processing",
        whatsappLink: "https://wa.me/2348096506034?text=Hi%20Abdul%2C%20I%27m%20interested%20in%20the%20Natural%20Language%20Processing%20program%20-%20saw%20it%20on%20Crea8it.%20Can%20you%20tell%20me%20more%3F"
    },
    {
        id: "applied-machine-learning",
        title: "Applied Machine Learning",
        icon: "icon-gear",
        tag: "Active",
        tagClass: "open",
        img: "assets/prog-aml.jpg",
        rot: "rot--4",
        description: "A practical program for building machine learning models that solve real problems — preparing data, training and evaluating models, and deploying them so they actually get used.",
        audience: "Eight(8) Weeks, 24 Live Sessions, 8 Tasks & 1 Capstone Project.", // DRAFT: edit to match the real program
        covers: ["Core Machine Learning Algorithms", "Feature Engineering & Data Preparation", "Model Evaluation, Tuning & Interpretation", "Model Deployment & Skill Monetisation"],
        priceLabel: "--", // TODO: add price
        ctaText: "Register →",
        ctaLink: "register.html?program=applied-machine-learning",
        whatsappLink: "https://wa.me/2348096506034?text=Hi%20Abdul%2C%20I%27m%20interested%20in%20the%20Applied%20Machine%20Learning%20program%20-%20saw%20it%20on%20Crea8it.%20Can%20you%20tell%20me%20more%3F"
    },
    {
        id: "data-science",
        title: "Data Science",
        icon: "icon-toolbox",
        tag: "Active",
        tagClass: "open",
        img: "assets/prog-ds.jpeg",
        rot: "rot--2",
        description: "An end-to-end data science program — from wrangling and exploring data to statistical modelling, visualisation and communicating insights that drive decisions.",
        audience: "Eight(8) Weeks, 24 Live Sessions, 8 Tasks & 1 Capstone Project.", // DRAFT: edit to match the real program
        covers: ["Python & SQL for Data Work", "Statistics, Modelling & Prediction", "Data Visualisation & Storytelling", "Data Science Portfolio & Skill Monetisation"],
        priceLabel: "--", // TODO: add price
        ctaText: "Register →",
        ctaLink: "register.html?program=data-science",
        whatsappLink: "https://wa.me/2348096506034?text=Hi%20Abdul%2C%20I%27m%20interested%20in%20the%20Data%20Science%20program%20-%20saw%20it%20on%20Crea8it.%20Can%20you%20tell%20me%20more%3F"
    },
    {
        id: "business-intelligence",
        title: "Business Intelligence",
        icon: "icon-toolbox",
        tag: "Active",
        tagClass: "open",
        img: "assets/prog-bi.jpeg",
        rot: "rot--3",
        description: "A hands-on program for turning business data into dashboards, KPIs and reports that leaders actually use — from defining the right metrics to building decision-ready BI solutions.",
        audience: "Six(6) Weeks, 18 Live Sessions, 6 Tasks & 1 Capstone Project.", // DRAFT: edit to match the real program
        covers: ["Business Data Foundations & KPI Design", "Data Modelling, SQL & Spreadsheet Analytics", "Dashboard Design & Data Visualisation", "BI Portfolio & Skill Monetisation"],
        priceLabel: "--", // TODO: add price
        ctaText: "Register →",
        ctaLink: "register.html?program=business-intelligence",
        whatsappLink: "https://wa.me/2348096506034?text=Hi%20Abdul%2C%20I%27m%20interested%20in%20the%20Business%20Intelligence%20program%20-%20saw%20it%20on%20Crea8it.%20Can%20you%20tell%20me%20more%3F"
    },
    {
        id: "software-design-development",
        title: "Software Design and Development",
        icon: "icon-terminal",
        tag: "Active",
        tagClass: "open",
        img: "assets/prog-sdd.jpg",
        rot: "rot--5",
        description: "A full program for learning how to design, build and ship real software — from programming foundations and architecture to full-stack development, deployment and maintenance.",
        audience: "Twelve(12) Weeks, 36 Live Sessions, 12 Tasks & 1 Capstone Project.", // DRAFT: edit to match the real program
        covers: ["Programming Foundations & Problem Solving", "Software Architecture & System Design", "Full-Stack Application Development", "Deployment, Testing & Software Career Launch"],
        priceLabel: "--", // TODO: add price
        ctaText: "Register →",
        ctaLink: "register.html?program=software-design-development",
        whatsappLink: "https://wa.me/2348096506034?text=Hi%20Abdul%2C%20I%27m%20interested%20in%20the%20Software%20Design%20and%20Development%20program%20-%20saw%20it%20on%20Crea8it.%20Can%20you%20tell%20me%20more%3F"
    },
    {
        id: "build-in-public",
        title: "Applied AI and Productivity",
        icon: null,
        tag: "Active",
        tagClass: "open",
        img: "assets/AppliedAI.jpeg",
        rot: "rot--2",
        description: "A hands-on program for learning how to use AI tools, build AI-powered workflows, automate tasks and apply AI to real-world professional and business problems..",
        audience: "Four(4) Weeks, 12 Live Sessions, 4 Tasks and 1 Capstone Project.", // DRAFT: edit to match the real program
        covers: ["AI Foundation & Prompt Mastery", "AI Tools Mastery & Application", "AI Workflow & Integration", "AI Skills Monetisation & Distribution"],
        priceLabel: "--",
        ctaText: "Join Challenge →",
        ctaLink: "register.html?program=build-in-public",
        whatsappLink: "https://wa.me/2348096506034?text=Hi%20Abdul%2C%20I%27d%20like%20to%20join%20the%20Build%20in%20Public%20Challenge%20-%20saw%20it%20on%20Crea8it."
    },
    {
        id: "zero-to-one",
        title: "Zero to 1",
        icon: "icon-flask",
        tag: "Active",
        tagClass: "open",
        img: "assets/zerops.jpeg",
        rot: "rot--3",
        description: "An idea validation and startup launch program for founders and indie hackers building real businesses from scratch. You don't just learn here — you EXECUTE.",
        audience: "8 Weeks, 16 Live Sessions, 4 Tasks & 1 Product.", // DRAFT: edit to match the real program
        covers: ["Idea Validation", "Business Model Development & Market Discovery", "MVP Design & Building", "Launch, Distribution & Monetization"],
        priceLabel: "--",
        ctaText: "Register →",
        ctaLink: "register.html?program=zero-to-one",
        whatsappLink: "https://wa.me/2348096506034?text=Hi%20Abdul%2C%20I%27d%20like%20to%20join%20the%20Zero%20to%201%20lab%20program-%20saw%20it%20on%20Crea8it."
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
