# TRA-8: Vercel Deployment for Next.js Frontend

**Date:** 2026-06-08
**Ticket:** TRA-8 — Set up Vercel deployment for Next.js frontend
**Status:** Approved

---

## Summary

Connect `apps/web` to Vercel for production and preview deployments. Configure monorepo build settings so Vercel installs from the repo root (enabling `packages/shared` access) while treating `apps/web` as the deployment root. Set Supabase environment variables in Vercel dashboard. Domain configuration deferred to a follow-up ticket (domain not yet purchased).

---

## Vercel Project Settings

Configure in Vercel dashboard after connecting the GitHub repo:

| Setting | Value |
|---|---|
| Root Directory | `apps/web` |
| Framework | Next.js (auto-detected) |
| Build Command | `next build` (default) |
| Install Command | `cd ../.. && npm install` |
| Output Directory | `.next` (default) |
| Node Version | 20.x |

The custom install command runs `npm install` from the monorepo root so all workspace packages (including `packages/shared`) are available during build. Vercel auto-detects Turborepo and enables remote cache automatically.

---

## Environment Variables

Set in Vercel dashboard for all environments (Production, Preview, Development):

| Variable | Source |
|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project dashboard → Settings → API |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase project dashboard → Settings → API |

Both are `NEXT_PUBLIC_` prefixed — safe to expose to the browser. Values already documented in `apps/web/.env.example`. No secrets are committed to the repository.

---

## Preview Deployments

Vercel's GitHub integration provides preview deployments automatically on every PR. No extra configuration required. Each PR receives a unique preview URL.

---

## Turborepo Remote Cache

Vercel auto-detects Turborepo when the install command runs from the monorepo root. Remote cache is enabled automatically — no additional env vars or `vercel.json` configuration needed.

---

## No `vercel.json` Required

All configuration lives in Vercel dashboard project settings. Nothing is committed to the repository for this ticket. `.env.example` already documents the two required env vars with a comment referencing TRA-8.

---

## Domain Configuration (Deferred)

`tracktal.com` is not yet purchased. Domain wiring is excluded from this ticket and tracked in a separate Linear issue:

**"TRA-XX: Connect tracktal.com domain to Vercel via Cloudflare DNS"**

When the domain is purchased, the steps are:
1. Add `tracktal.com` in Vercel dashboard → Domains
2. Vercel provides DNS records (CNAME `@` → `cname.vercel-dns.com`, CNAME `www` → `cname.vercel-dns.com`)
3. Add those records in Cloudflare DNS panel
4. Vercel auto-provisions SSL via Let's Encrypt

---

## Success Criteria

- Vercel project connected to GitHub repo
- Root directory set to `apps/web`, install command overridden to `cd ../.. && npm install`
- `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` set in Vercel dashboard for all environments
- Preview deployments trigger on every PR
- Turborepo remote cache active (verified in Vercel dashboard → Settings → Turborepo)
- New Linear issue created for domain DNS wiring
