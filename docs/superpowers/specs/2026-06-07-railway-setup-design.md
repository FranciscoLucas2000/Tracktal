# TRA-6: Railway Project and Environments Design

**Date:** 2026-06-07
**Ticket:** TRA-6 — Set up Railway project and environments
**Status:** Approved

---

## Summary

Create Railway project `tracktal` with two environments (`production`, `staging`) and two services (`api`, `pipelines`). Add `railway.toml` config files to repo for each service. Set required environment variables in Railway dashboard.

---

## Railway Project Structure

```
Railway project: tracktal
├── environment: production
│   ├── service: api        (FastAPI)
│   └── service: pipelines  (Prefect worker)
└── environment: staging
    ├── service: api
    └── service: pipelines
```

Both environments deploy from the `main` branch. Staging differs from production only via environment variables — same Supabase database, staging uses `search_path=staging` in the connection string to isolate data.

---

## Service Configuration Files

### `apps/api/railway.toml`

```toml
[build]
builder = "nixpacks"
buildCommand = "uv sync --package tracktal-api"

[deploy]
startCommand = "uv run uvicorn tracktal_api.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 30
restartPolicyType = "on_failure"
```

### `pipelines/railway.toml`

```toml
[build]
builder = "nixpacks"
buildCommand = "uv sync --package tracktal-pipelines"

[deploy]
startCommand = "uv run prefect worker start --pool railway-pool --type process"
restartPolicyType = "on_failure"
```

**Railway dashboard config (per service):**
- `api` service → Root Directory: `apps/api`
- `pipelines` service → Root Directory: `pipelines`

Prefect orchestration uses Prefect Cloud (free tier). The worker on Railway polls Prefect Cloud for flow runs.

---

## Environment Variables

Set in Railway dashboard per environment. Never committed to the repository. TRA-7 will document these in `.env.example`.

| Variable | `api` | `pipelines` | Notes |
|---|---|---|---|
| `DATABASE_URL` | ✓ | ✓ | Staging: append `?options=-c%20search_path%3Dstaging` |
| `ANTHROPIC_API_KEY` | ✓ | ✓ | Same key for both environments |
| `SCRAPERAPI_API_KEY` | — | ✓ | |
| `PREFECT_API_URL` | — | ✓ | Prefect Cloud workspace URL |
| `PREFECT_API_KEY` | — | ✓ | Prefect Cloud API key |
| `SENTRY_DSN` | ✓ | ✓ | Same DSN; `ENVIRONMENT` tag differentiates in Sentry |
| `ENVIRONMENT` | ✓ | ✓ | `production` or `staging` |
| `PORT` | ✓ | — | Injected automatically by Railway |

---

## Staging Strategy

**Lightweight staging** — single Supabase database, separate schema:
- Staging services connect to same Supabase instance as production
- `DATABASE_URL` for staging appends `?options=-c%20search_path%3Dstaging`
- Prefect runs with schedules active in staging
- Upgrade path: swap staging `DATABASE_URL` to a dedicated Supabase instance at any time — zero code changes required

---

## Stub Modules (Required for Deployment)

No Python source code exists yet. Railway will fail to build/start without importable packages. TRA-6 must include minimal stubs so both services deploy.

### `apps/api/tracktal_api/__init__.py`
Empty file — makes package importable.

### `apps/api/tracktal_api/main.py`
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}
```

### `pipelines/tracktal_pipelines/__init__.py`
Empty file — makes package importable so `uv sync --package tracktal-pipelines` succeeds.

These stubs will be expanded in later tickets. They are not application code — they are the minimum required for Railway to build and start the services.

---

## Scope Boundary

**Included in TRA-6:**
- Railway project creation (dashboard)
- Two environments: `production`, `staging`
- Two services per environment: `api`, `pipelines`
- `railway.toml` files committed to repo
- Minimal stub modules (`tracktal_api`, `tracktal_pipelines`) so services deploy
- All env vars set in Railway dashboard for both environments
- GitHub repo connected, auto-deploy from `main` enabled

**Excluded (other tickets):**
| What | Ticket |
|---|---|
| `.env.example` files | TRA-7 |
| FastAPI application code | Later API tickets |
| Prefect flows | TRA-13+ |
| GitHub Actions CI/CD | TRA-9 |
| Supabase project setup | TRA-7/TRA-8 |

---

## Success Criteria

- Railway project `tracktal` exists with `production` and `staging` environments
- Both services deploy successfully from `main` with no build errors
- FastAPI `/health` endpoint returns 200 in both environments
- Prefect worker connects to Prefect Cloud and shows as online in `railway-pool`
- All env vars populated in Railway dashboard for both environments
- `railway.toml` files committed on feature branch `feature/TRA-6-railway-setup`
