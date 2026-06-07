# TRA-5: Monorepo Scaffold Design

**Date:** 2026-06-07
**Ticket:** TRA-5 — Initialize GitHub monorepo
**Status:** Approved

---

## Summary

Scaffold the Tracktal monorepo with Turborepo for JS workspace management and `uv` for Python workspace management. Creates directory structure and all workspace config files. No application code — only the skeleton that all future tickets build on.

---

## Directory Structure

```
tracktal/
├── apps/
│   ├── web/                    # Next.js 14 — @tracktal/web
│   │   └── package.json        # stub (full scaffold: TRA-26)
│   └── api/                    # FastAPI — tracktal-api
│       ├── pyproject.toml
│       └── migrations/         # Alembic migrations (TRA-8)
├── packages/
│   └── shared/                 # Shared TS types — @tracktal/shared
│       └── package.json
├── pipelines/                  # Prefect flows — tracktal-pipelines
│   ├── pyproject.toml
│   └── flows/
├── dbt/                        # dbt models (TRA-14)
├── scripts/                    # Tooling scripts (exists)
├── docs/                       # Specs and design docs (this file)
├── turbo.json                  # Turborepo task config
├── package.json                # Root npm workspace + turbo scripts
├── pyproject.toml              # uv workspace root
├── uv.lock                     # Generated lockfile (committed)
└── README.md
```

---

## JS Workspace (Turborepo)

**Root `package.json`:**
```json
{
  "name": "tracktal",
  "private": true,
  "workspaces": ["apps/web", "packages/shared"],
  "scripts": {
    "build": "turbo build",
    "dev": "turbo dev",
    "lint": "turbo lint",
    "type-check": "turbo type-check"
  },
  "devDependencies": {
    "turbo": "latest"
  }
}
```

**`turbo.json`:**
```json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**", "dist/**"]
    },
    "dev": { "cache": false, "persistent": true },
    "lint": {},
    "type-check": {}
  }
}
```

**`apps/web/package.json`** (stub — Next.js scaffold deferred to TRA-26):
```json
{
  "name": "@tracktal/web",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "lint": "next lint",
    "type-check": "tsc --noEmit"
  }
}
```

**`packages/shared/package.json`:**
```json
{
  "name": "@tracktal/shared",
  "version": "0.1.0",
  "private": true,
  "main": "./src/index.ts",
  "scripts": {
    "lint": "eslint .",
    "type-check": "tsc --noEmit"
  }
}
```

---

## Python Workspace (uv)

Single `uv.lock` at root covers both Python packages. Railway deploys per-service using `uv sync --package <name>`.

**Root `pyproject.toml`:**
```toml
[tool.uv.workspace]
members = ["apps/api", "pipelines"]
```

**`apps/api/pyproject.toml`:**
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
```

**`pipelines/pyproject.toml`:**
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
```

---

## Scope Boundary

**Included in TRA-5:**
- All directories and placeholder files
- All workspace config files (package.json, turbo.json, pyproject.toml)
- `uv lock` to generate lockfile
- `npm install` at root to install turbo
- `README.md`

**Explicitly excluded (deferred to later tickets):**
| What | Ticket |
|---|---|
| Next.js scaffold (`create-next-app`) | TRA-26 |
| FastAPI app code | Later API tickets |
| dbt project init | TRA-14 |
| Prefect flows | TRA-13+ |
| Alembic migrations | TRA-8 |
| `.env.example` files | TRA-7 |
| GitHub Actions CI/CD | TRA-9 |
| Railway + Vercel setup | TRA-2, TRA-4 |

---

## Success Criteria

- `npm install` at root succeeds (installs turbo)
- `turbo --version` works
- `uv lock` at root succeeds (generates `uv.lock`)
- All directories exist with correct structure
- Feature branch `feature/TRA-5-github-monorepo` → PR to main
