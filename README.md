# Tracktal

Job market intelligence SaaS for Portugal and Spain. Scrapes job postings, normalises with AI, surfaces skill demand, salary benchmarks, and hiring trends.

## Stack

- **Frontend:** Next.js 14, Tailwind CSS, Shadcn/ui, Vercel
- **Backend:** FastAPI (Python), Railway
- **Database:** Supabase (Postgres + Auth)
- **Pipeline:** Prefect, dbt, DuckDB, ScraperAPI
- **AI:** Anthropic Claude API

## Structure

```
apps/web/        Next.js frontend
apps/api/        FastAPI backend
packages/shared/ Shared TypeScript types
pipelines/       Prefect flows and scrapers
dbt/             dbt transformation models
```

## Setup

See `CONTEXT.md` for full project context, architecture decisions, and development instructions.

### JS

```bash
npm install        # install all JS deps
npm run dev        # run all apps in dev mode
```

### Python

```bash
uv sync            # install all Python deps
```
