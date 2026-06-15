# TRA-12: Core Database Schema & Migrations

**Date:** 2026-06-15
**Linear:** TRA-12
**Status:** Approved

---

## Overview

Create all core Supabase tables via Supabase CLI migrations. 7 SQL files in `supabase/migrations/`, one per table, applied with `supabase db push`. Tier gating (free/pro/team data limits) handled in FastAPI query layer, not RLS.

**Blocked by:** TRA-7 (Supabase project setup)
**Blocks:** TRA-17, TRA-18, TRA-19, TRA-20 (scrapers), TRA-40 (subscription webhook)

---

## Migration File Structure

```
supabase/
  migrations/
    20260615000001_create_locations.sql
    20260615000002_create_companies.sql
    20260615000003_create_skills.sql
    20260615000004_create_job_postings.sql
    20260615000005_create_job_skills.sql
    20260615000006_create_scrape_runs.sql
    20260615000007_create_subscriptions.sql
```

Order is dependency-driven: `locations` and `companies` before `job_postings` (FK deps). `job_skills` after both `job_postings` and `skills`.

> **Note:** CONTEXT.md references `/apps/api/migrations/` — this is superseded by Supabase CLI convention. `apps/api/migrations/` is kept but unused for DB schema. CONTEXT.md should be updated.

---

## Schema

### `locations`

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
```

### `companies`

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
```

### `skills`

```sql
CREATE TABLE skills (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT UNIQUE NOT NULL,  -- lowercase, normalised e.g. "python", "react"
  category TEXT,              -- "programming_language" | "framework" | "soft_skill" | etc.
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### `job_postings`

```sql
CREATE TABLE job_postings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source TEXT NOT NULL CHECK (source IN ('adzuna', 'indeed', 'linkedin', 'eures')),
  external_id TEXT NOT NULL,

  -- Raw fields (as scraped)
  raw_title TEXT,
  raw_description TEXT,
  raw_location TEXT,
  raw_salary_min NUMERIC,
  raw_salary_max NUMERIC,
  raw_company_name TEXT,
  raw_posted_at TIMESTAMPTZ,

  -- Normalised fields (Claude AI output)
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
```

### `job_skills`

```sql
CREATE TABLE job_skills (
  job_id UUID NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
  skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
  PRIMARY KEY (job_id, skill_id)
);

CREATE INDEX ON job_skills (skill_id);
```

### `scrape_runs`

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

No RLS — pipeline-only table, accessed exclusively via service role.

### `subscriptions`

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
```

---

## RLS Policies

### Dashboard tables (job_postings, companies, skills, job_skills, locations)

Authenticated read-only. No user writes — all inserts/updates come from pipeline via service role (bypasses RLS).

```sql
ALTER TABLE <table> ENABLE ROW LEVEL SECURITY;

CREATE POLICY "authenticated_read" ON <table>
  FOR SELECT USING (auth.role() = 'authenticated');
```

### subscriptions

Users see only their own row. Webhook handler (service role) bypasses RLS.

```sql
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users_own_subscription" ON subscriptions
  FOR ALL USING (auth.uid() = user_id);
```

### scrape_runs

No RLS. Pipeline-internal table only.

---

## Tier Gating

Free/Pro/Team data limits (sector count, date range) are **not** implemented in RLS. FastAPI query layer applies filters based on subscription plan from JWT claims. This keeps RLS simple and business rules easy to change.

---

## Trigger: updated_at

`job_postings` and `subscriptions` both have `updated_at`. Postgres `DEFAULT now()` only fires on INSERT — a trigger is required for UPDATE.

Add once, reuse across tables:

```sql
CREATE OR REPLACE FUNCTION trigger_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at
  BEFORE UPDATE ON job_postings
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();

CREATE TRIGGER set_updated_at
  BEFORE UPDATE ON subscriptions
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
```

The function is created in the `job_postings` migration (first table that needs it) and referenced again in `subscriptions`.

---

## Out of Scope

- `profiles` table (not in TRA-12 scope — Supabase Auth handles `auth.users`)
- Seed data for `skills` vocabulary (separate task or initial migration)
- dbt models (separate epic)
- FastAPI endpoints (separate tickets)
