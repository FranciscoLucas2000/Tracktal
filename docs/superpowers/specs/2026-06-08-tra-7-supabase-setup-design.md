# TRA-7: Create Supabase Project and Configure Auth

**Date:** 2026-06-08
**Linear:** https://linear.app/tracktal/issue/TRA-7
**Status:** Approved

## Scope

Pure infrastructure setup + `.env.example` code artifacts. No FastAPI code, no SQL migrations, no Supabase client integration.

**Boundary:**
- TRA-12 owns all table creation and per-table RLS policies
- TRA-30 owns Supabase client setup in Next.js (`@supabase/ssr`)
- TRA-31 owns auth pages and Next.js middleware

## Manual Setup Steps (Supabase UI)

1. Create Supabase project
   - Region: `eu-west-1` (Ireland — closest to PT/ES)
   - Project name: `tracktal`
2. Authentication > Providers > Email: enable email + password
   - Disable "Confirm email" for development; re-enable before launch
   - No OAuth providers in v1
3. Note: Supabase has no project-wide RLS toggle — RLS is enabled per table via `ALTER TABLE ... ENABLE ROW LEVEL SECURITY`. TRA-12 owns this. No RLS action needed in TRA-7.
4. Copy credentials: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`

## Env Var Distribution

| Var | Railway (api) | Railway (pipelines) | Vercel (web) |
|-----|:---:|:---:|:---:|
| `SUPABASE_URL` | ✓ | ✓ | — |
| `SUPABASE_ANON_KEY` | ✓ | — | — |
| `SUPABASE_SERVICE_ROLE_KEY` | ✓ | ✓ | — |
| `NEXT_PUBLIC_SUPABASE_URL` | — | — | ✓ |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | — | — | ✓ |

Set vars in both `production` and `staging` Railway environments.

## Code Artifacts

Three `.env.example` files committed to the repo — document required var names, no values.

### `apps/api/.env.example`
```
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
```

### `apps/web/.env.example`
```
NEXT_PUBLIC_SUPABASE_URL=https://<project-ref>.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=
```

### `pipelines/.env.example`
```
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=
```

## Out of Scope

- Supabase client library installation (TRA-30)
- Table creation, RLS policies (TRA-12)
- Auth pages, middleware.ts (TRA-31)
- FastAPI auth dependency (TRA-31)
- dbt Supabase connection (TRA-14)

## Definition of Done

- [ ] Supabase project exists and is accessible
- [ ] Email auth enabled, confirm-email disabled for dev
- [ ] RLS approach documented — per-table setup deferred to TRA-12
- [ ] All env vars set in Railway (prod + staging) and Vercel
- [ ] Three `.env.example` files committed and merged to main via PR
