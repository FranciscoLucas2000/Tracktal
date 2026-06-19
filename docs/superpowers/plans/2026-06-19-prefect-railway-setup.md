# TRA-13: Prefect on Railway Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deploy a self-hosted Prefect server on Railway and verify a smoke-test flow runs end-to-end via a Railway process worker.

**Architecture:** Self-hosted Prefect server runs as a Railway service backed by Railway Postgres. Existing `tracktal-pipelines` Railway service runs a Prefect process worker pointing to the server via Railway private networking. Prefect Cloud not used.

**Tech Stack:** Prefect 3.x, Railway (nixpacks + two services + Postgres addon), uv, pytest, `prefect.testing.utilities`

---

## File Map

| Action | Path | Purpose |
|--------|------|---------|
| Modify | `pipelines/.env.example` | Document Prefect env vars (self-hosted Railway URL) |
| Delete | `pipelines/flows/.gitkeep` | Flows move into package, not top-level dir |
| Create | `pipelines/tracktal_pipelines/flows/__init__.py` | Make flows a Python subpackage |
| Create | `pipelines/tracktal_pipelines/flows/smoke_test.py` | Smoke test flow |
| Create | `pipelines/tests/test_smoke_test.py` | Unit test for smoke flow |
| Create | `pipelines/prefect.yaml` | Deployment config for self-hosted Prefect server |

---

### Task 1: Feature branch

**Files:** (git only)

- [ ] **Step 1: Create feature branch**

```bash
git checkout -b feature/TRA-13-prefect-railway-setup
```

- [ ] **Step 2: Verify clean state**

```bash
git status
```

Expected: `nothing to commit, working tree clean`

---

### Task 2: Update .env.example and scaffold flows package

**Files:**
- Modify: `pipelines/.env.example`
- Delete: `pipelines/flows/.gitkeep`
- Create: `pipelines/tracktal_pipelines/flows/__init__.py`

- [ ] **Step 1: Add Prefect vars to .env.example**

Append to `pipelines/.env.example`:

```
# Prefect Cloud
PREFECT_API_URL=https://api.prefect.cloud/api/accounts/<account-id>/workspaces/<workspace-id>
PREFECT_API_KEY=
```

(`<account-id>` and `<workspace-id>` are found in Prefect Cloud → Settings → Workspaces → API URL)

- [ ] **Step 2: Remove top-level flows placeholder**

```bash
rm pipelines/flows/.gitkeep && rmdir pipelines/flows
```

Flows live in `tracktal_pipelines/flows/` (Python package), not a top-level dir.

- [ ] **Step 3: Create flows subpackage**

Create `pipelines/tracktal_pipelines/flows/__init__.py` — empty file, no content needed.

- [ ] **Step 4: Commit**

```bash
git add pipelines/.env.example pipelines/tracktal_pipelines/flows/__init__.py
git rm pipelines/flows/.gitkeep
git commit -m "chore(TRA-13): scaffold flows package and document Prefect env vars"
```

---

### Task 3: Smoke test flow (TDD)

**Files:**
- Create: `pipelines/tracktal_pipelines/flows/smoke_test.py`
- Create: `pipelines/tests/test_smoke_test.py`

- [ ] **Step 1: Write the failing test**

Create `pipelines/tests/test_smoke_test.py`:

```python
import pytest
from prefect.testing.utilities import prefect_test_harness
from tracktal_pipelines.flows.smoke_test import smoke_test


@pytest.fixture(autouse=True)
def prefect_setup():
    with prefect_test_harness():
        yield


def test_smoke_test_returns_ok():
    result = smoke_test()
    assert result == "ok"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd pipelines && uv run pytest tests/test_smoke_test.py -v
```

Expected: `FAILED` — `ModuleNotFoundError: No module named 'tracktal_pipelines.flows.smoke_test'`

- [ ] **Step 3: Write minimal implementation**

Create `pipelines/tracktal_pipelines/flows/smoke_test.py`:

```python
from prefect import flow, get_run_logger


@flow(name="smoke-test")
def smoke_test():
    logger = get_run_logger()
    logger.info("Prefect on Railway: OK")
    return "ok"
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd pipelines && uv run pytest tests/test_smoke_test.py -v
```

Expected: `PASSED`

- [ ] **Step 5: Run full test suite to check no regressions**

```bash
cd pipelines && uv run pytest -v
```

Expected: all tests pass

- [ ] **Step 6: Commit**

```bash
git add pipelines/tracktal_pipelines/flows/smoke_test.py pipelines/tests/test_smoke_test.py
git commit -m "feat(TRA-13): add smoke-test flow and unit test"
```

---

### Task 4: Prefect deployment config

**Files:**
- Create: `pipelines/prefect.yaml`

- [ ] **Step 1: Create prefect.yaml**

Create `pipelines/prefect.yaml`:

```yaml
name: tracktal-pipelines
prefect-version: "3.0.0"

deployments:
  - name: smoke-test
    entrypoint: tracktal_pipelines/flows/smoke_test.py:smoke_test
    work_pool:
      name: railway-pool
    schedules: []
```

Entrypoint path is relative to `pipelines/` (the Railway working directory). Matches the editable install location.

- [ ] **Step 2: Commit**

```bash
git add pipelines/prefect.yaml
git commit -m "feat(TRA-13): add prefect.yaml with smoke-test deployment"
```

---

### Task 5: Update .env.example for self-hosted server

**Files:**
- Modify: `pipelines/.env.example`

> **Revision:** Prefect Cloud free tier blocks process work pools. Switching to self-hosted Prefect server on Railway.

- [ ] **Step 1: Update Prefect vars in .env.example**

Replace the `# Prefect Cloud` block with:

```
# Prefect (self-hosted server on Railway)
# Worker env var — Railway internal networking (set on tracktal-pipelines service in Railway):
PREFECT_API_URL=http://prefect-server.railway.internal:4200/api
# For local CLI commands, use the public Railway domain instead:
# PREFECT_API_URL=https://prefect-server-xxx.up.railway.app/api
```

Remove `PREFECT_API_KEY` — not needed for self-hosted server.

- [ ] **Step 2: Run tests to confirm no regressions**

```bash
cd pipelines && uv run pytest -v
```

Expected: all tests pass

- [ ] **Step 3: Commit**

```bash
git add pipelines/.env.example
git commit -m "chore(TRA-13): update env example for self-hosted Prefect server on Railway"
```

---

### Task 6: Railway infrastructure setup (manual — Railway dashboard)

No code changes. Steps in [railway.app](https://railway.app) dashboard.

- [ ] **Step 1: Add Postgres addon**

Railway project → **+ New** → **Database** → **Add PostgreSQL**. Wait for it to provision.

- [ ] **Step 2: Create prefect-server service**

Railway project → **+ New** → **GitHub Repo** → same repo → set **Root Directory** to `pipelines`

- [ ] **Step 3: Configure prefect-server service**

In the new service → **Settings**:
- Name: `prefect-server`
- Start command: `uv run prefect server start --host 0.0.0.0 --port 4200`

In **Variables** tab, add:
```
PREFECT_SERVER_DATABASE_CONNECTION_URL=postgresql+asyncpg://${{PGUSER}}:${{PGPASSWORD}}@${{PGHOST}}:${{PGPORT}}/${{PGDATABASE}}
```

Railway resolves `${{PGUSER}}` etc. from the Postgres addon automatically.

- [ ] **Step 4: Expose public domain**

`prefect-server` service → **Settings** → **Networking** → **Generate Domain**

Copy the domain (e.g. `prefect-server-production-xxxx.up.railway.app`).

- [ ] **Step 5: Wait for prefect-server to deploy**

Watch deployment logs. Expected:

```
Starting Prefect server on http://0.0.0.0:4200
```

- [ ] **Step 6: Configure tracktal-pipelines worker env var**

`tracktal-pipelines` service → **Variables** → add:

```
PREFECT_API_URL=http://prefect-server.railway.internal:4200/api
```

Remove `PREFECT_API_KEY` if previously set. Watch redeploy logs for:

```
Worker 'ProcessWorker ...' started!
```

---

### Task 7: Create work pool, deploy flow, verify end-to-end

- [ ] **Step 1: Set local PREFECT_API_URL to public domain**

```powershell
$env:PREFECT_API_URL="https://prefect-server-production-xxxx.up.railway.app/api"
```

Replace with real domain from Task 6 Step 4.

- [ ] **Step 2: Create work pool via CLI**

```bash
cd pipelines && uv run prefect work-pool create railway-pool --type process
```

Expected: `Created work pool 'railway-pool'!`

- [ ] **Step 3: Deploy smoke-test flow**

```bash
uv run prefect deploy --all
```

Expected: `Successfully created/updated all deployments!`

- [ ] **Step 4: Verify worker online in Prefect UI**

Navigate to `https://prefect-server-production-xxxx.up.railway.app` → **Work Pools** → `railway-pool` → **Workers** tab.

Expected: worker with status **Online**.

- [ ] **Step 5: Trigger smoke test run**

Prefect UI → **Deployments** → `smoke-test` → **Run** → **Quick Run** → **Submit**.

- [ ] **Step 6: Verify run completes**

Prefect UI → **Flow Runs** → find the run.

Expected:
- Status: **Completed**
- **Logs** tab contains: `Prefect on Railway: OK`

- [ ] **Step 7: Push updated branch**

```bash
git push
```

PR #12 already open — architecture change is self-contained in commits.
