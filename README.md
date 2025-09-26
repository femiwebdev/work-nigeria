Project Overview

This workspace captures my recent learning and build journey across three tracks: a skills sandbox (Power Learn Project), a practical Python utility (Website Downloader), and a full‑stack Django product (Work Nigeria).
Power Learn Project (power_learn_project)

    Purpose: Hands‑on practice across web fundamentals, Python, and basic data workflows.
    Highlights:
        Apps scaffolding for typical product domains: accounts, gigs, messaging, payments, projects, reviews.
        SQL exercises in database/ (schema creation and query tasks).
        Frontend practice in html_css_js/ (forms, responsive layout, basic interactivity).
        Python practice in python_tutorial/ (functions, OOP, file handling, list comprehensions, pandas intro).
    Outcome: Stronger fundamentals across backend, frontend, and data basics through small, focused exercises.

Website Downloader (website-downloader)

    Purpose: A Python tool to crawl a URL and archive pages/media into a structured public_html directory.
    Tech: Python, requests, beautifulsoup4, lxml, tqdm (packaged with Poetry).
    Capabilities:
        Fetch HTML and discover linked assets.
        Download pages, images, and other media to a local folder structure.
        Basic configuration and logging support (per project README).
    Status: Core scaffolding and docs in place; next steps include robustness (URL normalization, deduping, retries) and CLI UX.

Work Nigeria (work-nigeria)

    Purpose: A Django web app connecting clients and freelancers (similar to Upwork/Fiverr concepts).
    Tech: Django 4.x, Django REST Framework, Channels (+ Redis), CORS headers, Allauth, Crispy Forms, Pillow.
    Features (scoped in README/requirements):
        Accounts/auth, profiles, project listings and applications.
        Messaging, real‑time capabilities via Channels.
        Payment flow scaffolding and responsive UI foundations.
    Status: Project structure and dependencies defined with setup docs; next steps include domain models, APIs, and end‑to‑end user flows.

What this adds up to

    Foundation: Practiced core web/Python/SQL skills via targeted exercises.
    Utility: Built a practical scraping/downloading tool from scratch.
    Product: Evolving a full‑stack marketplace app with modern Django tooling.

Near‑term next steps

    Power Learn Project: Add tests and small capstone linking the mini‑apps.
    Website Downloader: Ship a Windows‑friendly CLI, caching, and robust asset handling.
    Work Nigeria: Implement core models (users/projects/contracts), DRF endpoints, Channels‑based messaging, and payment integration.
