# Monorepo Scaffold Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold the Tracktal monorepo with Turborepo (JS workspace) and uv (Python workspace) so all future tickets have a correct directory structure and dependency management foundation.

**Architecture:** Root npm workspace managed by Turborepo covers `apps/web` and `packages/shared`. Root uv workspace covers `apps/api` and `pipelines` with a single shared lockfile. All directories contain placeholder files — no application code.

**Tech Stack:** Turborepo, npm workspaces, uv, Node.js 20+, Python 3.11+

---

### Task 1: Create feature branch

**Files:**
- No files changed

- [ ] **Step 1: Create and switch to feature branch**

```bash
git checkout -b feature/TRA-5-github-monorepo
```

Expected output: `Switched to a new branch 'feature/TRA-5-github-monorepo'`

---

### Task 2: Create directory skeleton

**Files:**
- Create: `apps/web/.gitkeep`
- Create: `apps/api/migrations/.gitkeep`
- Create: `packages/shared/src/.gitkeep`
- Create: `pipelines/flows/.gitkeep`
- Create: `dbt/.gitkeep`

- [ ] **Step 1: Create all directories with placeholder files**

```bash
mkdir -p apps/web apps/api/migrations packages/shared/src pipelines/flows dbt
```

```bash
touch apps/api/migrations/.gitkeep pipelines/flows/.gitkeep dbt/.gitkeep packages/shared/src/.gitkeep
```

- [ ] **Step 2: Verify structure exists**

```bash
find . -not -path './.git/*' -not -path './node_modules/*' -not -path './scripts/*' -not -path './docs/*' -not -path './.claude/*' | sort
```

Expected output includes:
```
./apps/api/migrations/.gitkeep
./apps/web
./dbt/.gitkeep
./packages/shared/src/.gitkeep
./pipelines/flows/.gitkeep
```

---

### Task 3: Root JS workspace config

**Files:**
- Create: `package.json`
- Create: `turbo.json`

- [ ] **Step 1: Create root `package.json`**

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

Save to: `package.json`

- [ ] **Step 2: Create `turbo.json`**

```json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**", "dist/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": {},
    "type-check": {}
  }
}
```

Save to: `turbo.json`

---

### Task 4: JS package stubs

**Files:**
- Create: `apps/web/package.json`
- Create: `packages/shared/package.json`
- Create: `packages/shared/src/index.ts`

- [ ] **Step 1: Create `apps/web/package.json`**

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

Save to: `apps/web/package.json`

- [ ] **Step 2: Create `packages/shared/package.json`**

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

Save to: `packages/shared/package.json`

- [ ] **Step 3: Create `packages/shared/src/index.ts`**

```typescript
// Shared types and utilities — populated in later tickets
export {};
```

Save to: `packages/shared/src/index.ts`

---

### Task 5: Python workspace root

**Files:**
- Create: `pyproject.toml`

- [ ] **Step 1: Create root `pyproject.toml`**

```toml
[tool.uv.workspace]
members = ["apps/api", "pipelines"]
```

Save to: `pyproject.toml`

---

### Task 6: FastAPI package config

**Files:**
- Create: `apps/api/pyproject.toml`

- [ ] **Step 1: Create `apps/api/pyproject.toml`**

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

Save to: `apps/api/pyproject.toml`

---

### Task 7: Pipelines package config

**Files:**
- Create: `pipelines/pyproject.toml`

- [ ] **Step 1: Create `pipelines/pyproject.toml`**

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

Save to: `pipelines/pyproject.toml`

---

### Task 8: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create `README.md`**

```markdown
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
```

Save to: `README.md`

---

### Task 9: Install JS dependencies

**Files:**
- Generate: `package-lock.json`
- Generate: `node_modules/`

- [ ] **Step 1: Install from root**

```bash
npm install
```

Expected: turbo installed, `node_modules/` created, `package-lock.json` generated.

- [ ] **Step 2: Verify turbo works**

```bash
npx turbo --version
```

Expected output: version string e.g. `2.x.x`

---

### Task 10: Generate Python lockfile

**Files:**
- Generate: `uv.lock`

- [ ] **Step 1: Check uv is installed**

```bash
uv --version
```

If not installed:
```bash
pip install uv
```

- [ ] **Step 2: Generate lockfile from root**

```bash
uv lock
```

Expected: `uv.lock` file created at root. This resolves deps for both `tracktal-api` and `tracktal-pipelines`.

- [ ] **Step 3: Verify lockfile exists**

```bash
ls uv.lock
```

Expected: file exists with content.

---

### Task 11: Update .gitignore

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: Verify `node_modules/` and `uv.lock` are handled correctly**

`node_modules/` must be gitignored (already in `.gitignore`).
`uv.lock` must be committed (it is NOT in `.gitignore` — correct).

```bash
git status --short
```

Confirm `node_modules/` does NOT appear as untracked. Confirm `uv.lock` appears as untracked (to be committed).

---

### Task 12: Commit, push, open PR

**Files:**
- All new files staged

- [ ] **Step 1: Stage all new files**

```bash
git add package.json turbo.json apps/ packages/ pipelines/ dbt/ pyproject.toml uv.lock README.md
```

- [ ] **Step 2: Verify staged files**

```bash
git status --short
```

Confirm only expected files are staged. No `.env` files, no `node_modules/`.

- [ ] **Step 3: Commit**

```bash
git commit -m "feat(TRA-5): initialize monorepo scaffold

Turborepo for JS workspace (apps/web, packages/shared).
uv workspace for Python (apps/api, pipelines) with shared lockfile.
Directory structure, all workspace configs, README.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

- [ ] **Step 4: Push branch**

```bash
git push -u origin feature/TRA-5-github-monorepo
```

- [ ] **Step 5: Open PR**

```bash
gh pr create \
  --title "feat(TRA-5): initialize monorepo scaffold" \
  --body "## Summary
- Turborepo root workspace managing \`apps/web\` and \`packages/shared\`
- uv workspace managing \`apps/api\` and \`pipelines\` with single \`uv.lock\`
- Full directory structure per CONTEXT.md spec
- Stub package configs — no application code

## Test plan
- [ ] \`npm install\` succeeds from root
- [ ] \`npx turbo --version\` returns version
- [ ] \`uv lock\` succeeds from root
- [ ] \`uv.lock\` committed and present
- [ ] Directory structure matches spec

Closes TRA-5" \
  --base main
```

- [ ] **Step 6: Mark TRA-5 as Done in Linear**

Open Linear → TRA-5 → set status to **Done**.
