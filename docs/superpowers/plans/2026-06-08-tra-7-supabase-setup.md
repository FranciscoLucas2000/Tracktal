# TRA-7: Supabase Project Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create Supabase project, enable email auth, set env vars in Railway, and commit `.env.example` files documenting required credentials.

**Architecture:** Pure infrastructure setup. Supabase project created via UI. Credentials stored in Railway (api + pipelines) and documented in `.env.example` files. Vercel env vars deferred to TRA-8 (Vercel setup). No SQL migrations — TRA-12 owns all DB schema and per-table RLS.

**Tech Stack:** Supabase (hosted Postgres + Auth), Railway env var dashboard, curl for connectivity verification.

**Spec:** `docs/superpowers/specs/2026-06-08-tra-7-supabase-setup-design.md`

> **Note on Vercel env vars:** The spec lists "set Vercel env vars" as a deliverable, but the Vercel project doesn't exist until TRA-8 (which is blocked by this ticket). Vercel vars are documented in `apps/web/.env.example` here; they get set in the Vercel dashboard as part of TRA-8.

---

## File Map

| Action | Path | Purpose |
|--------|------|---------|
| Create | `apps/api/.env.example` | Document Railway env vars for FastAPI |
| Create | `apps/web/.env.example` | Document Vercel env vars for Next.js |
| Create | `pipelines/.env.example` | Document Railway env vars for Prefect pipelines |

No existing files modified.

---

## Task 1: Create Supabase Project

**Files:** None (UI only)

- [ ] **Step 1: Open Supabase dashboard**

Go to https://supabase.com/dashboard and sign in (or create account).

- [ ] **Step 2: Create new project**

Click "New project". Fill in:
- Organization: your org
- Name: `tracktal`
- Database password: generate a strong password and save it in a password manager
- Region: `eu-west-1` (Europe West — Ireland, closest to PT/ES)
- Plan: Free tier

Click "Create new project". Wait ~2 minutes for provisioning.

- [ ] **Step 3: Copy project credentials**

In project dashboard: Settings > API. Copy and save these three values somewhere secure (you'll need them in Task 3):

```
SUPABASE_URL         = https://<project-ref>.supabase.co
SUPABASE_ANON_KEY    = eyJ...  (labeled "anon public")
SUPABASE_SERVICE_ROLE_KEY = eyJ...  (labeled "service_role secret")
```

> **Security:** `SERVICE_ROLE_KEY` bypasses RLS — never expose it to the browser or commit it anywhere.

---

## Task 2: Configure Email Auth

**Files:** None (UI only)

- [ ] **Step 1: Enable email provider**

In Supabase dashboard: Authentication > Providers > Email.

Verify "Enable Email provider" is toggled ON (it is by default).

- [ ] **Step 2: Disable email confirmation for development**

On the same Email provider page, toggle OFF "Confirm email".

> Re-enable this before launch. With confirmation off, users can sign up and immediately sign in without verifying their email — needed for local dev and testing.

- [ ] **Step 3: Note RLS posture**

No action needed. Supabase enables RLS per-table via `ALTER TABLE ... ENABLE ROW LEVEL SECURITY`. TRA-12 will run those migrations. For now, no tables exist yet.

---

## Task 3: Set Railway Environment Variables

**Files:** None (Railway dashboard)

Railway has two environments (set up in TRA-6): `production` and `staging`. Set vars in both.

The api service needs all three vars. The pipelines service needs `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` (it writes data as a service, not on behalf of users).

- [ ] **Step 1: Set vars on api service (production)**

In Railway: Tracktal project > production environment > api service > Variables.

Add:
```
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_ANON_KEY=<your-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>
```

- [ ] **Step 2: Set vars on api service (staging)**

Switch to staging environment. Repeat the same three vars for the staging environment.

> You can reuse the same Supabase project for both staging and production for now. When traffic warrants it, create a second Supabase project for staging isolation.

- [ ] **Step 3: Set vars on pipelines service (production)**

In Railway: production environment > pipelines service > Variables.

Add:
```
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>
```

(No `SUPABASE_ANON_KEY` — pipelines use the service role to write data.)

- [ ] **Step 4: Set vars on pipelines service (staging)**

Switch to staging environment. Repeat the two vars above.

---

## Task 4: Create `.env.example` Files

**Files:**
- Create: `apps/api/.env.example`
- Create: `apps/web/.env.example`
- Create: `pipelines/.env.example`

These files document required env vars with no real values. They are committed to the repo and safe to share — they contain only var names and placeholder hints, never secrets.

- [ ] **Step 1: Create `apps/api/.env.example`**

```bash
# apps/api/.env.example
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
```

- [ ] **Step 2: Create `apps/web/.env.example`**

```bash
# apps/web/.env.example
# Set these in Vercel dashboard (TRA-8) — not in Railway
NEXT_PUBLIC_SUPABASE_URL=https://<project-ref>.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=
```

> `NEXT_PUBLIC_` prefix is required by Next.js to expose vars to the browser bundle. These are safe to expose — they are the anon key, not the service role key.

- [ ] **Step 3: Create `pipelines/.env.example`**

```bash
# pipelines/.env.example
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=
```

- [ ] **Step 4: Commit**

```bash
git add apps/api/.env.example apps/web/.env.example pipelines/.env.example
git commit -m "feat(TRA-7): add .env.example files for Supabase credentials"
```

---

## Task 5: Verify Supabase Connectivity

**Files:** None (verification only)

Confirm the Supabase project is live and the credentials work before closing the ticket.

- [ ] **Step 1: Test the REST endpoint**

From your terminal (substituting real values):

```bash
curl "https://<project-ref>.supabase.co/rest/v1/" \
  -H "apikey: <your-anon-key>" \
  -H "Authorization: Bearer <your-anon-key>"
```

Expected: HTTP 200 with an OpenAPI/Swagger JSON response body. Any 2xx means the project is live and the anon key is valid.

If you get 401: the anon key is wrong or the project hasn't finished provisioning — wait 1 minute and retry.

- [ ] **Step 2: Test the Auth endpoint**

```bash
curl "https://<project-ref>.supabase.co/auth/v1/settings" \
  -H "apikey: <your-anon-key>"
```

Expected: HTTP 200 with JSON containing `"external": {"email": true, ...}`. Confirms email auth is enabled.

---

## Task 6: Open PR

- [ ] **Step 1: Push branch**

```bash
git push -u origin feature/TRA-7-railway-setup
```

- [ ] **Step 2: Open PR**

```bash
gh pr create \
  --title "feat(TRA-7): create Supabase project and configure auth" \
  --body "$(cat <<'EOF'
## Summary
- Supabase project created (eu-west-1), email auth enabled
- Railway env vars set for api + pipelines (prod + staging)
- `.env.example` files committed for all three services
- Vercel env vars deferred to TRA-8

## What's not in this PR
- No SQL migrations (TRA-12)
- No Supabase client code (TRA-30)
- No Vercel env vars (TRA-8)

## Test plan
- [ ] `curl /rest/v1/` returns 200
- [ ] `curl /auth/v1/settings` shows email provider enabled
- [ ] Railway api service can start with new env vars (no crash)
EOF
)"
```

- [ ] **Step 3: Mark TRA-7 as In Review in Linear**

Open https://linear.app/tracktal/issue/TRA-7 and move to "In Review".

- [ ] **Step 4: Post PR link as comment on TRA-7**

Add a comment to the Linear issue with the PR URL so it's visible from the issue.
