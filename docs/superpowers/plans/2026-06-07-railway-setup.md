# TRA-6: Railway Project Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create Railway project with production and staging environments, two services (FastAPI + Prefect), committed `railway.toml` configs, and minimal stub Python modules so both services can build and deploy.

**Architecture:** Two services (`api`, `pipelines`) each with a `railway.toml` in their service directory. Railway sets Root Directory per service in the dashboard. Build commands navigate to repo root (`cd ../../` and `cd ../`) before running uv, because uv workspace operations require the workspace root. Stub modules make packages importable before real application code is written.

**Tech Stack:** Railway (nixpacks builder), uv workspace, FastAPI, Prefect Cloud (free tier)

---

## File Map

| File | Action | Purpose |
|---|---|---|
| `apps/api/pyproject.toml` | Modify | Add pytest + httpx dev dependency group |
| `apps/api/railway.toml` | Create | Build/deploy config for FastAPI service |
| `apps/api/tracktal_api/__init__.py` | Create | Makes `tracktal_api` importable |
| `apps/api/tracktal_api/main.py` | Create | FastAPI app with `/health` endpoint |
| `apps/api/tests/__init__.py` | Create | Makes tests directory a package |
| `apps/api/tests/test_health.py` | Create | Health endpoint test |
| `pipelines/pyproject.toml` | Modify | Add pytest dev dependency group |
| `pipelines/railway.toml` | Create | Build/deploy config for Prefect service |
| `pipelines/tracktal_pipelines/__init__.py` | Create | Makes `tracktal_pipelines` importable |
| `pipelines/tests/__init__.py` | Create | Makes tests directory a package |
| `pipelines/tests/test_import.py` | Create | Package importability test |
| `uv.lock` | Auto-updated | Updated when `uv sync` runs after adding dev deps |

---

### Task 1: FastAPI stub package

**Files:**
- Modify: `apps/api/pyproject.toml`
- Create: `apps/api/tracktal_api/__init__.py`
- Create: `apps/api/tracktal_api/main.py`
- Create: `apps/api/tests/__init__.py`
- Create: `apps/api/tests/test_health.py`

- [ ] **Step 1: Add dev dependencies to apps/api/pyproject.toml**

Replace the full file content with:

```toml
[project]
name = "tracktal-api"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.111.0",
    "uvicorn[standard]>=0.29.0",
    "supabase>=2.4.0",
    "alembic>=1.13.0",
    "anthropic>=0.26.0",
    "python-dotenv>=1.0.0",
    "sentry-sdk>=2.0.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "httpx>=0.27.0",
]
```

- [ ] **Step 2: Write the failing test**

Create `apps/api/tests/__init__.py` — empty file.

Create `apps/api/tests/test_health.py`:

```python
from fastapi.testclient import TestClient
from tracktal_api.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 3: Run test to verify it fails**

Run from repo root:

```bash
uv sync
uv run pytest apps/api/tests/test_health.py -v
```

Expected: `ModuleNotFoundError: No module named 'tracktal_api'`

- [ ] **Step 4: Create tracktal_api stub**

Create `apps/api/tracktal_api/__init__.py` — empty file.

Create `apps/api/tracktal_api/main.py`:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 5: Run test to verify it passes**

```bash
uv run pytest apps/api/tests/test_health.py -v
```

Expected output:
```
PASSED apps/api/tests/test_health.py::test_health_returns_ok
1 passed in Xs
```

- [ ] **Step 6: Commit**

```bash
git add apps/api/pyproject.toml apps/api/tracktal_api/ apps/api/tests/ uv.lock
git commit -m "feat(TRA-6): add FastAPI stub with health endpoint"
```

---

### Task 2: Prefect stub package

**Files:**
- Modify: `pipelines/pyproject.toml`
- Create: `pipelines/tracktal_pipelines/__init__.py`
- Create: `pipelines/tests/__init__.py`
- Create: `pipelines/tests/test_import.py`

- [ ] **Step 1: Add dev dependencies to pipelines/pyproject.toml**

Replace the full file content with:

```toml
[project]
name = "tracktal-pipelines"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "prefect>=3.0.0",
    "dbt-core>=1.8.0",
    "dbt-postgres>=1.8.0",
    "duckdb>=0.10.0",
    "anthropic>=0.26.0",
    "supabase>=2.4.0",
    "python-dotenv>=1.0.0",
    "httpx>=0.27.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0.0",
]
```

- [ ] **Step 2: Write the failing test**

Create `pipelines/tests/__init__.py` — empty file.

Create `pipelines/tests/test_import.py`:

```python
def test_tracktal_pipelines_importable():
    import tracktal_pipelines
    assert tracktal_pipelines is not None
```

- [ ] **Step 3: Run test to verify it fails**

```bash
uv sync
uv run pytest pipelines/tests/test_import.py -v
```

Expected: `ModuleNotFoundError: No module named 'tracktal_pipelines'`

- [ ] **Step 4: Create tracktal_pipelines stub**

Create `pipelines/tracktal_pipelines/__init__.py` — empty file.

- [ ] **Step 5: Run test to verify it passes**

```bash
uv run pytest pipelines/tests/test_import.py -v
```

Expected output:
```
PASSED pipelines/tests/test_import.py::test_tracktal_pipelines_importable
1 passed in Xs
```

- [ ] **Step 6: Commit**

```bash
git add pipelines/pyproject.toml pipelines/tracktal_pipelines/ pipelines/tests/ uv.lock
git commit -m "feat(TRA-6): add Prefect stub package"
```

---

### Task 3: Railway config files

**Files:**
- Create: `apps/api/railway.toml`
- Create: `pipelines/railway.toml`

> **Why `cd` in build/start commands:** Railway sets Root Directory per service (`apps/api` and `pipelines`). uv workspace operations (`uv sync --package X`) must run from the workspace root where `pyproject.toml` and `uv.lock` live. `../../` from `apps/api/` and `../` from `pipelines/` both reach the repo root. Railway clones the full repo — relative paths are reliable.

- [ ] **Step 1: Create apps/api/railway.toml**

```toml
[build]
builder = "nixpacks"
buildCommand = "cd ../../ && uv sync --package tracktal-api --no-dev"

[deploy]
startCommand = "cd ../../ && uv run --package tracktal-api uvicorn tracktal_api.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 30
restartPolicyType = "on_failure"
```

- [ ] **Step 2: Create pipelines/railway.toml**

```toml
[build]
builder = "nixpacks"
buildCommand = "cd ../ && uv sync --package tracktal-pipelines --no-dev"

[deploy]
startCommand = "cd ../ && uv run --package tracktal-pipelines prefect worker start --pool railway-pool --type process"
restartPolicyType = "on_failure"
```

- [ ] **Step 3: Commit**

```bash
git add apps/api/railway.toml pipelines/railway.toml
git commit -m "feat(TRA-6): add railway.toml configs for api and pipelines"
```

---

### Task 4: Railway dashboard setup

**This task is manual dashboard configuration. No code changes.**

**Prerequisites before starting:**
- Railway account at railway.app
- Feature branch `feature/TRA-6-railway-setup` pushed to GitHub remote
- Prefect Cloud account at prefect.io (free tier — create if needed)
- Supabase project URL + service role key available (set up in TRA-7/TRA-8 — if not ready yet, use placeholder values and update later)
- Anthropic, ScraperAPI, Sentry credentials available

- [ ] **Step 1: Push branch to remote**

```bash
git push -u origin feature/TRA-6-railway-setup
```

- [ ] **Step 2: Create Railway project**

1. Go to railway.app → Dashboard → New Project
2. Select "Deploy from GitHub repo"
3. Authorize Railway to access your GitHub account if prompted
4. Select the Tracktal repository
5. When Railway asks to configure a service, click **Skip** — you'll add services manually
6. Name the project `tracktal` (Settings → General → Project Name)

- [ ] **Step 3: Add staging environment**

Railway creates `production` by default.

1. Click the environment dropdown (top of project canvas)
2. Click "New Environment"
3. Name: `staging`
4. Environment type: **Permanent**
5. Click Create

- [ ] **Step 4: Create services in production environment**

Switch to **production** environment.

Create API service:
1. Click "+ New" → "GitHub Repo"
2. Select Tracktal repo
3. After service is created, click the service → Settings tab
4. Service name: `api`
5. Root Directory: `apps/api`
6. Click Save → service will attempt a deploy (may fail until env vars are set — that's expected)

Create Pipelines service:
1. Click "+ New" → "GitHub Repo"
2. Select Tracktal repo
3. Service name: `pipelines`
4. Root Directory: `pipelines`
5. Click Save

- [ ] **Step 5: Create services in staging environment**

Switch to **staging** environment. Repeat Step 4 exactly — create `api` and `pipelines` services with the same Root Directory settings.

- [ ] **Step 6: Set production environment variables**

Switch to **production** environment.

For the `api` service → Variables tab → add raw variables:

| Variable | Value |
|---|---|
| `DATABASE_URL` | Supabase Postgres connection string (from Supabase dashboard → Settings → Database → Connection string → URI) |
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `SENTRY_DSN` | Sentry DSN for this project |
| `ENVIRONMENT` | `production` |

For the `pipelines` service → Variables tab → add:

| Variable | Value |
|---|---|
| `DATABASE_URL` | Same Supabase Postgres connection string |
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `SCRAPERAPI_API_KEY` | Your ScraperAPI key |
| `PREFECT_API_URL` | Prefect Cloud workspace URL (prefect.io → Settings → Workspaces → copy API URL) |
| `PREFECT_API_KEY` | Prefect Cloud API key (prefect.io → Settings → API Keys → New key) |
| `SENTRY_DSN` | Same Sentry DSN |
| `ENVIRONMENT` | `production` |

- [ ] **Step 7: Set staging environment variables**

Switch to **staging** environment. Repeat Step 6 with these differences:

- `DATABASE_URL` for both services: same Supabase connection string but append `?options=-c%20search_path%3Dstaging` to isolate staging data in its own schema
- `ENVIRONMENT`: `staging`
- All other variables: same values as production

- [ ] **Step 8: Create Prefect work pool**

1. Go to prefect.io → Work Pools
2. Click "+" → New work pool
3. Name: `railway-pool`
4. Infrastructure type: **Process**
5. Click Create

- [ ] **Step 9: Trigger deployments and verify**

For each service in both environments, trigger a manual deploy:
1. Railway dashboard → service → Deployments tab → "Deploy" button (or redeploy latest)
2. Watch build logs — look for `uv sync` completing successfully

Verify `api` service:
1. Railway dashboard → `api` service → Settings → click the generated Railway URL
2. Append `/health` to the URL
3. Expected response: `{"status": "ok"}`

Verify `pipelines` service:
1. Go to prefect.io → Work Pools → `railway-pool`
2. Expected: at least one worker showing as **Online**

---

## Self-Review Notes

**Spec correction applied in this plan:** The spec listed `uv sync --package tracktal-api` as the build command without addressing that Railway's Root Directory changes the working directory. This plan uses `cd ../../ && uv sync --package tracktal-api` to navigate to the workspace root before running uv — a required step for uv workspace operations.

**Staging schema isolation:** The `?options=-c%20search_path%3Dstaging` suffix on staging `DATABASE_URL` requires the `staging` schema to exist in Supabase before pipelines run. Create it manually in the Supabase SQL editor: `CREATE SCHEMA IF NOT EXISTS staging;`
