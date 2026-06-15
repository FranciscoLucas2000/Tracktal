# Tracktal — Project Context

> This file is the single source of truth for the Tracktal project.
> Reference it in every Cursor session with @CONTEXT.md before giving instructions.
> Keep it updated as decisions change.

---

## What It Is

**Tracktal** is a job market intelligence SaaS platform targeting Portugal and Spain.
It scrapes job postings at scale, normalises the data using AI, and surfaces actionable
trends — skill demand, salary benchmarks, hiring velocity — sold as a subscription
dashboard and weekly email digest.

**Domain:** tracktal.com
**Founder:** Solo — software engineer and data engineer, building with Claude AI assistance.
**Goal:** Replace a full-time salary within 18 months. Target 2–4 hours/day maintenance once stable.

---

## Problem It Solves

HR managers, recruiters, career coaches, and universities in Portugal and Spain have no
reliable, affordable source of real-time job market intelligence. They make decisions
about hiring, training, and career guidance based on intuition. Tracktal gives them
data — which skills are growing, what roles pay, which companies are hiring.

---

## Target Customers

- Recruitment agencies in Portugal and Spain
- HR managers at mid-size companies
- Career coaches and career centres
- University career services departments
- Government workforce planning teams (IEFP Portugal, SEPE Spain)
- HR consultancies that serve multiple clients

**Not targeting:** Enterprise (too slow), individual job seekers (too low willingness to pay).

---

## Business Model

Subscription SaaS with three tiers:

| Plan | Price | Features |
|---|---|---|
| Free | €0 | 2 sectors, last 4 weeks data, limited charts |
| Pro | €29/month | All sectors, 12 months history, CSV export, email alerts |
| Team | €79/month | Everything + public API access, white-label reports |

**Payment processor:** Lemon Squeezy (handles EU VAT automatically)
**Target MRR at quit-job point:** €6,000–€8,000 (roughly 15–20 Pro clients or equivalent mix)

---

## Tech Stack

### Frontend
- **Next.js 14** (app router) — main web framework
- **Tailwind CSS** — styling
- **Shadcn/ui** — component library
- **Tremor** — data dashboard components
- **Recharts** — charts
- **Vercel** — deployment

### Backend & API
- **Railway** — backend and pipeline deployment
- **Supabase** — primary database (Postgres), auth, row-level security
- **FastAPI** (Python) — API layer

### Data Pipeline
- **Prefect** — pipeline orchestration and scheduling
- **dbt** — data transformation and modelling
- **DuckDB** — local intermediate processing
- **ScraperAPI** — managed proxy infrastructure for scrapers

### AI
- **Anthropic Claude API** — job title normalisation, skills extraction, data parsing
- Model: claude-sonnet-4-20250514

### Integrations & Services
- **Lemon Squeezy** — payments and subscriptions
- **Resend** — transactional and digest emails
- **Loops** — marketing email and onboarding sequences
- **Posthog** — product analytics and session recording
- **Sentry** — error monitoring
- **Uptime Robot** — uptime monitoring
- **Cloudflare** — DNS, CDN, DDoS protection
- **GitHub Actions** — CI/CD

### Dev Tools
- **Cursor** — IDE with AI assistance
- **Linear** — project management and tickets (MCP connected)
- **Notion** — research, decisions, customer notes

---

## Repository Structure

```
tracktal/
├── apps/
│   ├── web/          # Next.js frontend
│   └── api/          # FastAPI backend
├── packages/
│   └── shared/       # Shared types and utilities
├── pipelines/        # Prefect flows and scraping logic
├── dbt/              # dbt models and transformations
├── CONTEXT.md        # This file
└── README.md
```

---

## Database Schema (Core Tables)

```
job_postings       — raw and normalised job postings
companies          — company entities (deduplicated)
skills             — controlled skills vocabulary
job_skills         — many-to-many: job_postings <> skills
locations          — normalised location entities
scrape_runs        — pipeline run logs and metadata
users              — auth users (managed by Supabase Auth)
subscriptions      — plan status synced from Lemon Squeezy
```

---

## Data Sources

| Source | Type | Geography | Cadence |
|---|---|---|---|
| Adzuna API | Official API (free) | PT + ES | Weekly |
| Indeed | Scraper (ScraperAPI) | PT + ES | Weekly |
| LinkedIn Jobs | Scraper (ScraperAPI) | PT + ES | Weekly |
| EURES | Official API (EU) | EU-wide | Weekly |

All pipelines run on Sunday night. Dashboard updates Monday morning.
Reports sent to subscribers every Monday at 8am.

---

## dbt Model Layers

```
staging/           — raw source cleaning, one model per source
  stg_adzuna
  stg_indeed
  stg_linkedin
  stg_eures

intermediate/      — business logic, deduplication, normalisation
  int_job_postings_deduped
  int_skills_extracted
  int_salaries_normalised

marts/             — final analytics-ready models
  mart_skill_trends          — weekly skill demand + WoW/MoM growth
  mart_salary_benchmarks     — median/p25/p75 by role + location
  mart_company_hiring        — hiring velocity per company
  mart_location_demand       — job demand by city and region
```

---

## Key Technical Decisions

- **Weekly batch processing only** — not real-time. Keeps infrastructure simple and maintenance low.
- **ScraperAPI for all scraping** — no self-managed proxies. Worth the cost to avoid rabbit holes.
- **Claude API for normalisation** — job titles and skills are too chaotic for regex. AI handles it.
- **Lemon Squeezy over Stripe** — simpler EU VAT handling for a solo PT-based founder.
- **Supabase over raw Postgres** — built-in auth, dashboard, and REST API saves weeks of work.
- **DuckDB for intermediate processing** — process locally before loading to Supabase. Fast and free.
- **No real-time features in v1** — simplifies architecture massively. Add later if customers demand it.

---

## Roadmap Phases

### Phase 1 — Foundation (Months 1–2)
Infrastructure setup, database schema, pipeline foundation.
Epics: Project setup, Data pipeline foundation.

### Phase 2 — MVP Build (Months 2–4)
Build scrapers, analytics models, dashboard, and billing.
Epics: Job posting scrapers, Analytics & trend models, Dashboard & frontend, Payments.

### Phase 3 — Launch & First Revenue (Months 4–9)
Go-to-market, first customers, product improvements from feedback.
Epics: GTM & first customers, Product improvements.
Target: €2,000–€3,000 MRR by end of phase.

### Phase 4 — Scale (Months 9–18)
Public API, geographic expansion (FR, DE), infrastructure scaling, revenue expansion.
Target: €6,000–€8,000 MRR → quit job.

Full ticket list in Linear (58 tickets, 12 epics, T-001 to T-058).

---

## Current Status

- [x] Domain registered: tracktal.com
- [x] Linear workspace created
- [ ] GitHub repo initialised
- [ ] Railway project set up
- [ ] Supabase project created
- [ ] First scraper running

---

## Pricing Research Notes

- Competitors like Lightcast and Burning Glass charge €500–€2,000/month (enterprise only)
- No good affordable option exists for PT/ES market specifically
- Recruiters in PT typically spend €50–€200/month on tools
- €29/month Pro tier is intentionally low to reduce friction for first 50 customers
- Can increase pricing after establishing market presence

---

## Go-To-Market Strategy

**Phase 1 (pre-launch):** Interview 20 potential customers before writing product code.
**Phase 2 (launch):** Direct outreach to 50 recruitment agencies in PT + ES.
**Phase 3 (content):** Monthly free job market reports as lead magnet. SEO blog targeting
keywords like "tech salaries portugal", "fastest growing skills spain".
**Phase 4 (partnerships):** University career centres, HR consultancies, white-label deals.

**Never do:** Cold calls, enterprise sales cycles, paid ads before €3k MRR.

---

## Git Workflow

**These rules are mandatory. No exceptions.**

1. **Never commit directly to `main`.** All work goes on a feature branch.
2. **One branch per Linear ticket.** Name format: `feature/TRA-XXX-short-description`.
3. **One PR per ticket.** Open a PR when the ticket is complete. Link it to the Linear issue.
4. **PR checklist before opening:**
   - Code works locally
   - No hardcoded credentials
   - Migration file exists for any DB change
   - Tests pass (if applicable)
5. **Merge strategy:** Squash and merge into `main`. Delete branch after merge.

**Branch naming examples:**
```
feature/TRA-5-github-monorepo
feature/TRA-8-database-schema
feature/TRA-17-claude-normalisation
```

---

## Claude Code Instructions

When working on this project:
1. Always use the stack defined above. Do not suggest alternatives unless there is a critical reason.
2. Python code goes in `/pipelines/` or `/apps/api/`. TypeScript goes in `/apps/web/`.
3. All database changes must have a corresponding migration file in `supabase/migrations/`. Files use timestamp prefix format: `YYYYMMDDHHmmss_description.sql`. Apply with `supabase migration up` (incremental) or `supabase db reset` (full local reset). Push to remote Supabase with `supabase db push`. The `/apps/api/migrations/` folder is unused for DB schema.
4. All new Prefect flows go in `/pipelines/flows/`. Schedule in `/pipelines/schedules.py`.
5. All dbt models follow the staging → intermediate → marts layer structure above.
6. When creating Linear tickets via MCP, link to the correct epic and set priority as specified.
7. Environment variables are never hardcoded. Always use Railway env vars for backend, Vercel env vars for frontend.
8. All API endpoints require auth middleware unless explicitly marked public.
9. Default to batch/async processing. Never block the API on heavy computation.
10. When in doubt, keep it simple. This is a solo project — complexity is the enemy.
11. **Always create a feature branch before starting any ticket.** Use format `feature/TRA-XXX-short-description`.
12. **Always open a PR when a ticket is complete.** Never push directly to `main`.
13. **Mark the Linear ticket as In Progress when starting, Done when PR is opened.**
