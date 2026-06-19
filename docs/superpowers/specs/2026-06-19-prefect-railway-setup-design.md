# TRA-13: Prefect on Railway — Design Spec

**Date:** 2026-06-19
**Ticket:** TRA-13 — T-009: Set up Prefect on Railway
**Status:** Approved

---

## Architecture

Prefect Cloud (free tier, existing account) acts as orchestration server and UI. A single Railway service runs a Prefect process worker that polls Cloud for work.

```
Prefect Cloud (app.prefect.cloud)
  └── work pool: railway-pool (process type)
        └── Railway service: tracktal-pipelines
              └── Prefect worker (uv run prefect worker start --pool railway-pool --type process)
                    └── Flow runs as subprocess on same container
```

No self-hosted Prefect server. No Docker-in-Docker. No additional Railway services.

---

## Components

### New file: `pipelines/flows/smoke_test.py`

Minimal flow to verify end-to-end plumbing:

```python
from prefect import flow, get_run_logger

@flow(name="smoke-test")
def smoke_test():
    logger = get_run_logger()
    logger.info("Prefect on Railway: OK")
    return "ok"
```

### Updated: `pipelines/.env.example`

Add two new env vars:

```
PREFECT_API_URL=https://api.prefect.cloud/api/accounts/<account-id>/workspaces/<workspace-id>
PREFECT_API_KEY=
```

### Unchanged

- `pipelines/railway.toml` — deploy command already correct
- `pipelines/nixpacks.toml` — Python 3.12 + uv already correct
- `pipelines/pyproject.toml` — `prefect>=3.0.0` already declared

---

## Manual Setup Steps (one-time, not in code)

1. Create work pool `railway-pool` with type **process** in Prefect Cloud UI
2. Set `PREFECT_API_URL` and `PREFECT_API_KEY` as Railway service env vars
3. Deploy smoke test flow:
   ```
   uv run prefect deploy pipelines/flows/smoke_test.py:smoke_test --name smoke-test --pool railway-pool
   ```
4. Trigger run from Prefect Cloud UI and verify success

---

## Error Handling

- `restartPolicyType = "on_failure"` in `railway.toml` auto-restarts worker on crash
- Missing `PREFECT_API_KEY` → worker fails at startup with clear connection error in Railway logs
- Wrong `PREFECT_API_URL` → same — connection refused at startup, not silent

---

## Success Criteria

1. Railway service deploys without error
2. Prefect Cloud UI shows `railway-pool` worker as **online**
3. Smoke test flow triggered from UI → status **Completed**
4. Log line `"Prefect on Railway: OK"` visible in Prefect Cloud run logs
