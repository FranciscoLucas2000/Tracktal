# TRA-13: Prefect on Railway Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Connect a Railway process worker to Prefect Cloud and verify a smoke-test flow runs end-to-end.

**Architecture:** Prefect Cloud (free tier, existing account) acts as orchestration server and UI. A single Railway service runs a Prefect process worker polling work pool `railway-pool`. Flows live in `tracktal_pipelines/flows/` (installed Python package, available on Railway worker via editable install).

**Tech Stack:** Prefect 3.x, Railway (nixpacks + process worker), uv, pytest, `prefect.testing.utilities`

---

## File Map

| Action | Path | Purpose |
|--------|------|---------|
| Modify | `pipelines/.env.example` | Document Prefect env vars |
| Delete | `pipelines/flows/.gitkeep` | Flows move into package, not top-level dir |
| Create | `pipelines/tracktal_pipelines/flows/__init__.py` | Make flows a Python subpackage |
| Create | `pipelines/tracktal_pipelines/flows/smoke_test.py` | Smoke test flow |
| Create | `pipelines/tests/test_smoke_test.py` | Unit test for smoke flow |
| Create | `pipelines/prefect.yaml` | Deployment config for Prefect Cloud |

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

### Task 5: Prefect Cloud work pool setup (manual — browser)

No code changes. Steps in browser at [app.prefect.cloud](https://app.prefect.cloud).

- [ ] **Step 1: Create work pool**

Navigate to **Work Pools** → **+ Create work pool**
- Name: `railway-pool`
- Type: **Process**
- Click **Next** → **Create**

- [ ] **Step 2: Create API key**

Navigate to **Settings** → **API Keys** → **+ Create API Key**
- Name: `railway-worker`
- Copy the key — it is shown only once

- [ ] **Step 3: Copy workspace API URL**

Navigate to **Settings** → **Workspaces** → copy the **API URL**

Format: `https://api.prefect.cloud/api/accounts/<uuid>/workspaces/<uuid>`

Keep both values for Task 6.

---

### Task 6: Configure Railway env vars (manual — Railway dashboard)

No code changes. Steps in [railway.app](https://railway.app) dashboard.

- [ ] **Step 1: Open service variables**

Railway project → `tracktal-pipelines` service → **Variables** tab

- [ ] **Step 2: Add both variables**

| Variable | Value |
|----------|-------|
| `PREFECT_API_URL` | URL from Task 5 Step 3 |
| `PREFECT_API_KEY` | Key from Task 5 Step 2 |

- [ ] **Step 3: Watch redeploy logs**

Railway redeploys automatically. In **Deployments** tab, watch logs for:

```
Worker 'ProcessWorker ...' started!
```

If you see a connection error instead, verify `PREFECT_API_URL` has no trailing slash and the key is correct.

---

### Task 7: Push branch, deploy flow, verify end-to-end

- [ ] **Step 1: Push branch to remote**

```bash
git push -u origin feature/TRA-13-prefect-railway-setup
```

This triggers a Railway redeploy from the feature branch (if Railway is watching this branch). If Railway only watches `main`, the Railway service is already running from the previous tasks — proceed to Step 2.

- [ ] **Step 2: Set local env vars for deploy command**

Copy `pipelines/.env.example` to `pipelines/.env` and fill in `PREFECT_API_URL` and `PREFECT_API_KEY` with real values. The `.env` file is gitignored.

- [ ] **Step 3: Deploy flow to Prefect Cloud**

```bash
cd pipelines && uv run prefect deploy --all
```

Expected output:

```
Successfully created/updated all deployments!

                          Deployments
┏━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Name                   ┃ Status        ┃ Details            ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ smoke-test/smoke-test  │ ✅ Applied    │ railway-pool       │
└────────────────────────┴───────────────┴────────────────────┘
```

- [ ] **Step 4: Verify worker is online in Prefect Cloud**

Navigate to **Work Pools** → `railway-pool` → **Workers** tab.

Expected: worker listed with status **Online**. If **Offline**, check Railway logs for connection errors.

- [ ] **Step 5: Trigger smoke test run from UI**

Navigate to **Deployments** → `smoke-test` → **Run** → **Quick Run** → **Submit**.

- [ ] **Step 6: Verify run completes**

Navigate to **Flow Runs** → find the new run.

Expected:
- Status: **Completed**
- **Logs** tab contains: `Prefect on Railway: OK`

- [ ] **Step 7: Open PR and update Linear**

Open PR on GitHub from `feature/TRA-13-prefect-railway-setup` → link to TRA-13 in description.
Set Linear ticket TRA-13 to **In Review**.
