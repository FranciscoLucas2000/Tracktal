# TRA-13: Prefect on Railway — Design Spec

**Date:** 2026-06-19 (revised 2026-06-20)
**Ticket:** TRA-13 — T-009: Set up Prefect on Railway
**Status:** Approved

> **Revision note:** Original design used Prefect Cloud free tier. Prefect Cloud free tier does not support hybrid/process work pools. Design updated to self-hosted Prefect server on Railway.

---

## Architecture

Self-hosted Prefect server runs as a Railway service. A second Railway service runs a Prefect process worker polling a `railway-pool` work pool on that server. Worker communicates with the server via Railway private networking (no public internet hop, no bandwidth cost).

```
Railway Project
├── prefect-server service
│   ├── Source: pipelines/ (same repo, same nixpacks/uv build)
│   ├── Start: uv run prefect server start --host 0.0.0.0 --port 4200
│   ├── Env: PREFECT_SERVER_DATABASE_CONNECTION_URL=postgresql+asyncpg://...
│   └── Public domain: prefect-server-xxx.up.railway.app (UI + local CLI)
│
├── tracktal-pipelines service (existing — worker)
│   ├── Start: uv run prefect worker start --pool railway-pool --type process
│   └── Env: PREFECT_API_URL=http://prefect-server.railway.internal:4200/api
│
└── Postgres (Railway addon)
    └── Provides DATABASE_URL → used by prefect-server for state storage
```

No Prefect Cloud account needed. No API key. No auth (server is on private Railway network; UI is public but read-only risk is acceptable for solo project).

---

## Components

### Updated: `pipelines/.env.example`

```
# Prefect server (self-hosted on Railway)
# Railway internal URL for worker (set on tracktal-pipelines service):
PREFECT_API_URL=http://prefect-server.railway.internal:4200/api
# Public URL for local CLI commands (use Railway-assigned domain):
# PREFECT_API_URL=https://prefect-server-xxx.up.railway.app/api
```

Remove `PREFECT_API_KEY` — not needed for self-hosted server.

### Unchanged

- `pipelines/railway.toml` — worker start command already correct
- `pipelines/nixpacks.toml` — Python 3.12 + uv already correct
- `pipelines/pyproject.toml` — `prefect>=3.0.0` already declared
- `pipelines/tracktal_pipelines/flows/smoke_test.py` — flow unchanged
- `pipelines/prefect.yaml` — deployment config unchanged

---

## Manual Setup Steps (one-time, not in code)

### Railway setup

1. Add **Postgres** plugin to Railway project (Database → Add → PostgreSQL)
2. Create new Railway service `prefect-server`:
   - Source: same GitHub repo, root `pipelines/`
   - Override start command: `uv run prefect server start --host 0.0.0.0 --port 4200`
   - Set env var: `PREFECT_SERVER_DATABASE_CONNECTION_URL=postgresql+asyncpg://${{PGUSER}}:${{PGPASSWORD}}@${{PGHOST}}:${{PGPORT}}/${{PGDATABASE}}`
   - Expose public domain (Railway → Settings → Networking → Generate Domain)
3. On `tracktal-pipelines` service, set:
   - `PREFECT_API_URL=http://prefect-server.railway.internal:4200/api`

### Work pool + deployment

4. Once `prefect-server` is live, create work pool from local CLI:
   ```
   $env:PREFECT_API_URL="https://prefect-server-xxx.up.railway.app/api"
   uv run prefect work-pool create railway-pool --type process
   ```
5. Deploy smoke-test flow:
   ```
   uv run prefect deploy --all
   ```

---

## Error Handling

- `restartPolicyType = "on_failure"` in `railway.toml` auto-restarts worker on crash
- Wrong `PREFECT_API_URL` on worker → connection refused at startup → visible in Railway logs
- Prefect server fails to start → check `PREFECT_SERVER_DATABASE_CONNECTION_URL` in Railway logs
- Railway private networking uses `.railway.internal` hostname — only works between services in same Railway project

---

## Success Criteria

1. `prefect-server` Railway service deploys and UI accessible at public domain
2. `tracktal-pipelines` worker logs: `Worker 'ProcessWorker ...' started!`
3. Prefect server UI shows `railway-pool` worker as **online**
4. Smoke test flow triggered from UI → status **Completed**
5. Log line `"Prefect on Railway: OK"` visible in Prefect server run logs
