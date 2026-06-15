# Core Database Schema Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create all 7 core Supabase tables via Supabase CLI migrations with RLS policies.

**Architecture:** 7 SQL migration files in `supabase/migrations/`, one per table, applied via `supabase db push` (remote) or `supabase db reset` (local). RLS policies inline in each migration. Tier gating (free/pro/team data limits) handled in FastAPI, not RLS. `updated_at` trigger function defined once in `job_postings` migration, reused in `subscriptions`.

**Tech Stack:** Supabase CLI, PostgreSQL, psycopg2-binary (schema tests), pytest

**Spec:** `docs/superpowers/specs/2026-06-15-core-database-schema-design.md`

---

## File Map

| File | Action | Purpose |
|---|---|---|
| `supabase/config.toml` | Create | Supabase CLI config (via `supabase init`) |
| `supabase/migrations/20260615000001_create_locations.sql` | Create | locations table + RLS |
| `supabase/migrations/20260615000002_create_companies.sql` | Create | companies table + RLS |
| `supabase/migrations/20260615000003_create_skills.sql` | Create | skills table + RLS |
| `supabase/migrations/20260615000004_create_job_postings.sql` | Create | job_postings table + updated_at trigger + RLS |
| `supabase/migrations/20260615000005_create_job_skills.sql` | Create | job_skills join table + RLS |
| `supabase/migrations/20260615000006_create_scrape_runs.sql` | Create | scrape_runs table (no RLS) |
| `supabase/migrations/20260615000007_create_subscriptions.sql` | Create | subscriptions table + RLS |
| `apps/api/pyproject.toml` | Modify | Add psycopg2-binary to dev deps |
| `apps/api/tests/conftest.py` | Create | DB connection fixture for schema tests |
| `apps/api/tests/test_schema.py` | Create | Schema verification tests (one per table) |
| `CONTEXT.md` → `CONTEXT.md` | Modify | Update migrations path to `supabase/migrations/` |

---

## Task 1: Create feature branch

- [ ] **Step 1: Create and checkout branch**

```bash
git checkout -b feature/TRA-12-core-database-schema
```

- [ ] **Step 2: Verify branch**

```bash
git branch --show-current
```

Expected output: `feature/TRA-12-core-database-schema`

---

## Task 2: Initialize Supabase CLI

Prerequisites: Supabase CLI installed (`supabase --version` should work). If not: `winget install Supabase.CLI` on Windows or follow https://supabase.com/docs/guides/cli/getting-started.

- [ ] **Step 1: Run supabase init from repo root**

```bash
supabase init
```

Expected: creates `supabase/config.toml` and `supabase/.gitignore`. If asked to generate VS Code settings, say yes.

- [ ] **Step 2: Start local Supabase (requires Docker running)**

```bash
supabase start
```

Expected: Docker pulls images on first run (~2 min). When done, output shows:

```
API URL: http://localhost:54321
DB URL: postgresql://postgres:postgres@localhost:54322/postgres
Studio URL: http://localhost:54323
```

Save the DB URL — used by tests.

- [ ] **Step 3: Verify local DB is accessible**

```bash
supabase status
```

Expected: shows running services including `DB URL: postgresql://postgres:postgres@localhost:54322/postgres`

- [ ] **Step 4: Commit supabase init files**

```bash
git add supabase/config.toml supabase/.gitignore
git commit -m "chore: initialize Supabase CLI"
```

---

## Task 3: Add psycopg2 + schema test fixture

- [ ] **Step 1: Add psycopg2-binary to dev deps**

Edit `apps/api/pyproject.toml` — add `psycopg2-binary` to the dev group:

```toml
[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "httpx>=0.27.0",
    "psycopg2-binary>=2.9.0",
]
```

- [ ] **Step 2: Install psycopg2-binary**

```bash
pip install psycopg2-binary
```

- [ ] **Step 3: Create test DB fixture**

Create `apps/api/tests/conftest.py`:

```python
import psycopg2
import pytest


LOCAL_DB_URL = "postgresql://postgres:postgres@localhost:54322/postgres"


@pytest.fixture(scope="session")
def db():
    conn = psycopg2.connect(LOCAL_DB_URL)
    conn.autocommit = True
    yield conn
    conn.close()
```

- [ ] **Step 4: Verify fixture works**

```bash
cd apps/api && pytest tests/ -v
```

Expected: existing `test_health.py` tests still pass. No import errors.

- [ ] **Step 5: Commit**

```bash
git add apps/api/pyproject.toml apps/api/tests/conftest.py
git commit -m "test: add psycopg2 dev dep and DB connection fixture"
```

---

## Task 4: locations migration

- [ ] **Step 1: Write failing test for locations**

Create `apps/api/tests/test_schema.py`:

```python
import pytest


def _table_columns(db, table_name):
    with db.cursor() as cur:
        cur.execute(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position
            """,
            (table_name,),
        )
        return {row[0]: {"type": row[1], "nullable": row[2]} for row in cur.fetchall()}


def _rls_enabled(db, table_name):
    with db.cursor() as cur:
        cur.execute(
            "SELECT relrowsecurity FROM pg_class WHERE relname = %s AND relnamespace = 'public'::regnamespace",
            (table_name,),
        )
        row = cur.fetchone()
        return row is not None and row[0]


def _policy_exists(db, table_name, policy_name):
    with db.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM pg_policies WHERE tablename = %s AND policyname = %s",
            (table_name, policy_name),
        )
        return cur.fetchone() is not None


class TestLocations:
    def test_table_exists(self, db):
        cols = _table_columns(db, "locations")
        assert "id" in cols
        assert "city" in cols
        assert "region" in cols
        assert "country" in cols
        assert "lat" in cols
        assert "lng" in cols
        assert "created_at" in cols

    def test_country_not_nullable(self, db):
        cols = _table_columns(db, "locations")
        assert cols["country"]["nullable"] == "NO"

    def test_rls_enabled(self, db):
        assert _rls_enabled(db, "locations")

    def test_authenticated_read_policy(self, db):
        assert _policy_exists(db, "locations", "authenticated_read")
```

- [ ] **Step 2: Run test — verify it fails**

```bash
cd apps/api && pytest tests/test_schema.py::TestLocations -v
```

Expected: FAIL — `AssertionError` because table doesn't exist yet.

- [ ] **Step 3: Write locations migration**

Create `supabase/migrations/20260615000001_create_locations.sql`:

```sql
CREATE TABLE locations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  city TEXT,
  region TEXT,
  country TEXT NOT NULL CHECK (country IN ('PT', 'ES')),
  lat NUMERIC(9,6),
  lng NUMERIC(9,6),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (city, region, country)
);

ALTER TABLE locations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "authenticated_read" ON locations
  FOR SELECT USING (auth.role() = 'authenticated');
```

- [ ] **Step 4: Apply migration**

```bash
supabase db reset
```

Expected: `Resetting local database...` then `Local database is now up to date.`

- [ ] **Step 5: Run test — verify it passes**

```bash
cd apps/api && pytest tests/test_schema.py::TestLocations -v
```

Expected: all 4 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add supabase/migrations/20260615000001_create_locations.sql apps/api/tests/test_schema.py
git commit -m "feat(TRA-12): add locations table migration and schema test"
```

---

## Task 5: companies migration

- [ ] **Step 1: Add failing test — append to `apps/api/tests/test_schema.py`**

```python
class TestCompanies:
    def test_table_exists(self, db):
        cols = _table_columns(db, "companies")
        assert "id" in cols
        assert "name" in cols
        assert "slug" in cols
        assert "website" in cols
        assert "sector" in cols
        assert "country" in cols
        assert "created_at" in cols

    def test_name_not_nullable(self, db):
        cols = _table_columns(db, "companies")
        assert cols["name"]["nullable"] == "NO"

    def test_slug_not_nullable(self, db):
        cols = _table_columns(db, "companies")
        assert cols["slug"]["nullable"] == "NO"

    def test_rls_enabled(self, db):
        assert _rls_enabled(db, "companies")

    def test_authenticated_read_policy(self, db):
        assert _policy_exists(db, "companies", "authenticated_read")
```

- [ ] **Step 2: Run test — verify it fails**

```bash
cd apps/api && pytest tests/test_schema.py::TestCompanies -v
```

Expected: FAIL.

- [ ] **Step 3: Write companies migration**

Create `supabase/migrations/20260615000002_create_companies.sql`:

```sql
CREATE TABLE companies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  website TEXT,
  sector TEXT,
  country TEXT CHECK (country IN ('PT', 'ES')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE companies ENABLE ROW LEVEL SECURITY;

CREATE POLICY "authenticated_read" ON companies
  FOR SELECT USING (auth.role() = 'authenticated');
```

- [ ] **Step 4: Apply migration**

```bash
supabase migration up
```

Expected: `Applying migration 20260615000002_create_companies.sql...` then `Local database is now up to date.`

- [ ] **Step 5: Run test — verify it passes**

```bash
cd apps/api && pytest tests/test_schema.py::TestCompanies -v
```

Expected: all 5 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add supabase/migrations/20260615000002_create_companies.sql apps/api/tests/test_schema.py
git commit -m "feat(TRA-12): add companies table migration and schema test"
```

---

## Task 6: skills migration

- [ ] **Step 1: Add failing test — append to `apps/api/tests/test_schema.py`**

```python
class TestSkills:
    def test_table_exists(self, db):
        cols = _table_columns(db, "skills")
        assert "id" in cols
        assert "name" in cols
        assert "category" in cols
        assert "created_at" in cols

    def test_name_not_nullable(self, db):
        cols = _table_columns(db, "skills")
        assert cols["name"]["nullable"] == "NO"

    def test_rls_enabled(self, db):
        assert _rls_enabled(db, "skills")

    def test_authenticated_read_policy(self, db):
        assert _policy_exists(db, "skills", "authenticated_read")
```

- [ ] **Step 2: Run test — verify it fails**

```bash
cd apps/api && pytest tests/test_schema.py::TestSkills -v
```

Expected: FAIL.

- [ ] **Step 3: Write skills migration**

Create `supabase/migrations/20260615000003_create_skills.sql`:

```sql
CREATE TABLE skills (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT UNIQUE NOT NULL,
  category TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE skills ENABLE ROW LEVEL SECURITY;

CREATE POLICY "authenticated_read" ON skills
  FOR SELECT USING (auth.role() = 'authenticated');
```

- [ ] **Step 4: Apply migration**

```bash
supabase migration up
```

Expected: `Applying migration 20260615000003_create_skills.sql...` then `Local database is now up to date.`

- [ ] **Step 5: Run test — verify it passes**

```bash
cd apps/api && pytest tests/test_schema.py::TestSkills -v
```

Expected: all 4 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add supabase/migrations/20260615000003_create_skills.sql apps/api/tests/test_schema.py
git commit -m "feat(TRA-12): add skills table migration and schema test"
```

---

## Task 7: job_postings migration

This migration also creates the `trigger_set_updated_at` function used by `subscriptions` later.

- [ ] **Step 1: Add failing test — append to `apps/api/tests/test_schema.py`**

```python
class TestJobPostings:
    def test_table_exists(self, db):
        cols = _table_columns(db, "job_postings")
        expected = [
            "id", "source", "external_id",
            "raw_title", "raw_description", "raw_location",
            "raw_salary_min", "raw_salary_max", "raw_company_name", "raw_posted_at",
            "normalised_title", "title_category", "company_id", "location_id",
            "salary_min_eur", "salary_max_eur", "salary_period",
            "employment_type", "remote_type", "experience_level",
            "is_normalised", "scraped_at", "created_at", "updated_at",
        ]
        cols_found = list(cols.keys())
        for col in expected:
            assert col in cols_found, f"Missing column: {col}"

    def test_source_not_nullable(self, db):
        cols = _table_columns(db, "job_postings")
        assert cols["source"]["nullable"] == "NO"

    def test_is_normalised_not_nullable(self, db):
        cols = _table_columns(db, "job_postings")
        assert cols["is_normalised"]["nullable"] == "NO"

    def test_updated_at_trigger_exists(self, db):
        with db.cursor() as cur:
            cur.execute(
                """
                SELECT 1 FROM information_schema.triggers
                WHERE event_object_table = 'job_postings'
                  AND trigger_name = 'set_updated_at'
                """
            )
            assert cur.fetchone() is not None

    def test_rls_enabled(self, db):
        assert _rls_enabled(db, "job_postings")

    def test_authenticated_read_policy(self, db):
        assert _policy_exists(db, "job_postings", "authenticated_read")

    def test_unique_source_external_id(self, db):
        with db.cursor() as cur:
            cur.execute(
                """
                SELECT 1 FROM information_schema.table_constraints
                WHERE table_name = 'job_postings'
                  AND constraint_type = 'UNIQUE'
                """
            )
            assert cur.fetchone() is not None
```

- [ ] **Step 2: Run test — verify it fails**

```bash
cd apps/api && pytest tests/test_schema.py::TestJobPostings -v
```

Expected: FAIL.

- [ ] **Step 3: Write job_postings migration**

Create `supabase/migrations/20260615000004_create_job_postings.sql`:

```sql
CREATE OR REPLACE FUNCTION trigger_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TABLE job_postings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source TEXT NOT NULL CHECK (source IN ('adzuna', 'indeed', 'linkedin', 'eures')),
  external_id TEXT NOT NULL,

  raw_title TEXT,
  raw_description TEXT,
  raw_location TEXT,
  raw_salary_min NUMERIC,
  raw_salary_max NUMERIC,
  raw_company_name TEXT,
  raw_posted_at TIMESTAMPTZ,

  normalised_title TEXT,
  title_category TEXT,
  company_id UUID REFERENCES companies(id),
  location_id UUID REFERENCES locations(id),
  salary_min_eur NUMERIC,
  salary_max_eur NUMERIC,
  salary_period TEXT CHECK (salary_period IN ('hourly', 'monthly', 'annual')),
  employment_type TEXT CHECK (employment_type IN ('full_time', 'part_time', 'contract', 'internship')),
  remote_type TEXT CHECK (remote_type IN ('on_site', 'hybrid', 'remote')),
  experience_level TEXT CHECK (experience_level IN ('junior', 'mid', 'senior', 'unspecified')),

  is_normalised BOOLEAN NOT NULL DEFAULT FALSE,
  scraped_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

  UNIQUE (source, external_id)
);

CREATE INDEX ON job_postings (source, scraped_at);
CREATE INDEX ON job_postings (is_normalised);
CREATE INDEX ON job_postings (company_id);
CREATE INDEX ON job_postings (location_id);

CREATE TRIGGER set_updated_at
  BEFORE UPDATE ON job_postings
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

ALTER TABLE job_postings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "authenticated_read" ON job_postings
  FOR SELECT USING (auth.role() = 'authenticated');
```

- [ ] **Step 4: Apply migration**

```bash
supabase migration up
```

Expected: `Applying migration 20260615000004_create_job_postings.sql...` then `Local database is now up to date.`

- [ ] **Step 5: Run test — verify it passes**

```bash
cd apps/api && pytest tests/test_schema.py::TestJobPostings -v
```

Expected: all 7 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add supabase/migrations/20260615000004_create_job_postings.sql apps/api/tests/test_schema.py
git commit -m "feat(TRA-12): add job_postings migration with updated_at trigger and schema test"
```

---

## Task 8: job_skills migration

- [ ] **Step 1: Add failing test — append to `apps/api/tests/test_schema.py`**

```python
class TestJobSkills:
    def test_table_exists(self, db):
        cols = _table_columns(db, "job_skills")
        assert "job_id" in cols
        assert "skill_id" in cols

    def test_job_id_not_nullable(self, db):
        cols = _table_columns(db, "job_skills")
        assert cols["job_id"]["nullable"] == "NO"

    def test_skill_id_not_nullable(self, db):
        cols = _table_columns(db, "job_skills")
        assert cols["skill_id"]["nullable"] == "NO"

    def test_primary_key_exists(self, db):
        with db.cursor() as cur:
            cur.execute(
                """
                SELECT 1 FROM information_schema.table_constraints
                WHERE table_name = 'job_skills' AND constraint_type = 'PRIMARY KEY'
                """
            )
            assert cur.fetchone() is not None

    def test_rls_enabled(self, db):
        assert _rls_enabled(db, "job_skills")

    def test_authenticated_read_policy(self, db):
        assert _policy_exists(db, "job_skills", "authenticated_read")
```

- [ ] **Step 2: Run test — verify it fails**

```bash
cd apps/api && pytest tests/test_schema.py::TestJobSkills -v
```

Expected: FAIL.

- [ ] **Step 3: Write job_skills migration**

Create `supabase/migrations/20260615000005_create_job_skills.sql`:

```sql
CREATE TABLE job_skills (
  job_id UUID NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
  skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
  PRIMARY KEY (job_id, skill_id)
);

CREATE INDEX ON job_skills (skill_id);

ALTER TABLE job_skills ENABLE ROW LEVEL SECURITY;

CREATE POLICY "authenticated_read" ON job_skills
  FOR SELECT USING (auth.role() = 'authenticated');
```

- [ ] **Step 4: Apply migration**

```bash
supabase migration up
```

Expected: `Applying migration 20260615000005_create_job_skills.sql...` then `Local database is now up to date.`

- [ ] **Step 5: Run test — verify it passes**

```bash
cd apps/api && pytest tests/test_schema.py::TestJobSkills -v
```

Expected: all 6 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add supabase/migrations/20260615000005_create_job_skills.sql apps/api/tests/test_schema.py
git commit -m "feat(TRA-12): add job_skills migration and schema test"
```

---

## Task 9: scrape_runs migration

- [ ] **Step 1: Add failing test — append to `apps/api/tests/test_schema.py`**

```python
class TestScrapeRuns:
    def test_table_exists(self, db):
        cols = _table_columns(db, "scrape_runs")
        expected = [
            "id", "source", "status", "started_at", "completed_at",
            "postings_found", "postings_new", "error_message", "created_at",
        ]
        for col in expected:
            assert col in cols, f"Missing column: {col}"

    def test_source_not_nullable(self, db):
        cols = _table_columns(db, "scrape_runs")
        assert cols["source"]["nullable"] == "NO"

    def test_status_not_nullable(self, db):
        cols = _table_columns(db, "scrape_runs")
        assert cols["status"]["nullable"] == "NO"

    def test_rls_not_enabled(self, db):
        # scrape_runs is pipeline-only, no RLS needed
        assert not _rls_enabled(db, "scrape_runs")
```

- [ ] **Step 2: Run test — verify it fails**

```bash
cd apps/api && pytest tests/test_schema.py::TestScrapeRuns -v
```

Expected: FAIL.

- [ ] **Step 3: Write scrape_runs migration**

Create `supabase/migrations/20260615000006_create_scrape_runs.sql`:

```sql
CREATE TABLE scrape_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source TEXT NOT NULL CHECK (source IN ('adzuna', 'indeed', 'linkedin', 'eures')),
  status TEXT NOT NULL DEFAULT 'running' CHECK (status IN ('running', 'success', 'failed')),
  started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at TIMESTAMPTZ,
  postings_found INT NOT NULL DEFAULT 0,
  postings_new INT NOT NULL DEFAULT 0,
  error_message TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

- [ ] **Step 4: Apply migration**

```bash
supabase migration up
```

Expected: `Applying migration 20260615000006_create_scrape_runs.sql...` then `Local database is now up to date.`

- [ ] **Step 5: Run test — verify it passes**

```bash
cd apps/api && pytest tests/test_schema.py::TestScrapeRuns -v
```

Expected: all 4 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add supabase/migrations/20260615000006_create_scrape_runs.sql apps/api/tests/test_schema.py
git commit -m "feat(TRA-12): add scrape_runs migration and schema test"
```

---

## Task 10: subscriptions migration

- [ ] **Step 1: Add failing test — append to `apps/api/tests/test_schema.py`**

```python
class TestSubscriptions:
    def test_table_exists(self, db):
        cols = _table_columns(db, "subscriptions")
        expected = [
            "id", "user_id", "lemon_squeezy_subscription_id",
            "plan", "status", "current_period_start", "current_period_end",
            "created_at", "updated_at",
        ]
        for col in expected:
            assert col in cols, f"Missing column: {col}"

    def test_user_id_not_nullable(self, db):
        cols = _table_columns(db, "subscriptions")
        assert cols["user_id"]["nullable"] == "NO"

    def test_plan_not_nullable(self, db):
        cols = _table_columns(db, "subscriptions")
        assert cols["plan"]["nullable"] == "NO"

    def test_status_not_nullable(self, db):
        cols = _table_columns(db, "subscriptions")
        assert cols["status"]["nullable"] == "NO"

    def test_updated_at_trigger_exists(self, db):
        with db.cursor() as cur:
            cur.execute(
                """
                SELECT 1 FROM information_schema.triggers
                WHERE event_object_table = 'subscriptions'
                  AND trigger_name = 'set_updated_at'
                """
            )
            assert cur.fetchone() is not None

    def test_rls_enabled(self, db):
        assert _rls_enabled(db, "subscriptions")

    def test_users_own_subscription_policy(self, db):
        assert _policy_exists(db, "subscriptions", "users_own_subscription")
```

- [ ] **Step 2: Run test — verify it fails**

```bash
cd apps/api && pytest tests/test_schema.py::TestSubscriptions -v
```

Expected: FAIL.

- [ ] **Step 3: Write subscriptions migration**

Create `supabase/migrations/20260615000007_create_subscriptions.sql`:

```sql
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  lemon_squeezy_subscription_id TEXT UNIQUE,
  plan TEXT NOT NULL DEFAULT 'free' CHECK (plan IN ('free', 'pro', 'team')),
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'past_due', 'paused')),
  current_period_start TIMESTAMPTZ,
  current_period_end TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (user_id)
);

CREATE INDEX ON subscriptions (user_id);

CREATE TRIGGER set_updated_at
  BEFORE UPDATE ON subscriptions
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users_own_subscription" ON subscriptions
  FOR ALL USING (auth.uid() = user_id);
```

- [ ] **Step 4: Apply migration**

```bash
supabase migration up
```

Expected: `Applying migration 20260615000007_create_subscriptions.sql...` then `Local database is now up to date.`

- [ ] **Step 5: Run test — verify it passes**

```bash
cd apps/api && pytest tests/test_schema.py::TestSubscriptions -v
```

Expected: all 7 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add supabase/migrations/20260615000007_create_subscriptions.sql apps/api/tests/test_schema.py
git commit -m "feat(TRA-12): add subscriptions migration and schema test"
```

---

## Task 11: Full reset verify

- [ ] **Step 1: Full reset from scratch**

```bash
supabase db reset
```

Expected: all 7 migrations applied cleanly. `Local database is now up to date.`

- [ ] **Step 2: Run full test suite**

```bash
cd apps/api && pytest tests/ -v
```

Expected: ALL tests pass (health + all schema tests).

If any fail, `supabase db reset` may have a migration ordering issue. Fix by checking FK dependencies (locations/companies must precede job_postings).

---

## Task 12: Update CONTEXT.md

- [ ] **Step 1: Update migrations path in CONTEXT.md**

In `CONTEXT.md`, find:

```
3. All database changes must have a corresponding migration file in `/apps/api/migrations/`.
```

Replace with:

```
3. All database changes must have a corresponding migration file in `supabase/migrations/`. Files use timestamp prefix format: `YYYYMMDDHHmmss_description.sql`. Apply with `supabase migration up` (incremental) or `supabase db reset` (full local reset). The `/apps/api/migrations/` folder is unused for DB schema.
```

- [ ] **Step 2: Commit**

```bash
git add CONTEXT.md
git commit -m "docs: update migrations path from apps/api to supabase/migrations"
```

---

## Task 13: Open PR

- [ ] **Step 1: Push branch**

```bash
git push -u origin feature/TRA-12-core-database-schema
```

- [ ] **Step 2: Open PR**

```bash
gh pr create \
  --title "feat(TRA-12): implement core database schema and migrations" \
  --body "$(cat <<'EOF'
## Summary

- Initializes Supabase CLI (`supabase/config.toml`)
- Adds 7 migration files in `supabase/migrations/` (locations, companies, skills, job_postings, job_skills, scrape_runs, subscriptions)
- RLS enabled on all user-facing tables; authenticated-read policy on dashboard tables; user-scoped policy on subscriptions; no RLS on scrape_runs
- `updated_at` trigger function created in job_postings migration, reused by subscriptions
- Schema tests via psycopg2 + pytest verify each table's columns, nullability, RLS, and triggers
- Updates CONTEXT.md to reflect `supabase/migrations/` as the canonical migrations path

Closes TRA-12

## Test plan

- [ ] `supabase db reset` completes without errors
- [ ] `pytest tests/` — all tests pass
- [ ] Supabase Studio (http://localhost:54323) shows all 7 tables with correct columns

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- [ ] **Step 3: Post PR link to Linear TRA-12 and mark In Review**

In Linear, open TRA-12, add the PR URL as an attachment, set status to **In Review**.
