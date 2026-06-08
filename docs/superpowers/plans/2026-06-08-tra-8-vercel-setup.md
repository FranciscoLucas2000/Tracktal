# TRA-8: Vercel Deployment Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Connect `apps/web` to Vercel with correct monorepo settings, Supabase env vars, and preview deployments on every PR.

**Architecture:** Vercel project root = `apps/web`, install command overridden to `cd ../.. && npm install` so the monorepo root is used. All config lives in Vercel dashboard — nothing committed to repo. Domain wiring deferred to a new Linear issue.

**Tech Stack:** Vercel dashboard, GitHub integration, Turborepo remote cache (auto-detected).

---

## File Map

No files created or modified in the repository. All configuration is done in the Vercel dashboard.

---

### Task 1: Create feature branch

- [ ] **Step 1: Create and push feature branch**

```bash
git checkout -b feature/TRA-8-vercel-deployment
git push -u origin feature/TRA-8-vercel-deployment
```

Expected: branch created locally and on remote.

- [ ] **Step 2: Mark TRA-8 as In Progress in Linear**

Open Linear → TRA-8 → set status to **In Progress**.

---

### Task 2: Create Linear issue for domain DNS wiring

- [ ] **Step 1: Create new Linear issue**

In Linear, create a new issue with:
- **Title:** Connect tracktal.com domain to Vercel via Cloudflare DNS
- **Description:**
  ```
  Once tracktal.com is purchased, wire it to Vercel via Cloudflare DNS.

  Steps:
  1. Add tracktal.com in Vercel dashboard → Project → Settings → Domains
  2. Vercel provides DNS records to create in Cloudflare
  3. In Cloudflare DNS panel, add:
     - CNAME  @    cname.vercel-dns.com
     - CNAME  www  cname.vercel-dns.com
  4. Vercel auto-provisions SSL via Let's Encrypt (allow up to 24h propagation)

  Blocked by: domain purchase.
  ```
- **Project:** Phase 1 — Project Setup
- **Priority:** Medium
- **Epic:** Infrastructure / Deployment

- [ ] **Step 2: Note the new issue ID**

Record the new issue ID (e.g. TRA-XX) — reference it in the PR description for TRA-8.

---

### Task 3: Connect Vercel to GitHub

> These steps require a browser and a Vercel account (vercel.com). Log in with GitHub SSO.

- [ ] **Step 1: Create new Vercel project**

Go to [vercel.com/new](https://vercel.com/new).

- [ ] **Step 2: Import GitHub repository**

Select **"Import Git Repository"** → choose `tracktal` monorepo.

- [ ] **Step 3: Configure root directory**

In the import screen, expand **"Root Directory"** and set it to:
```
apps/web
```

Vercel will auto-detect Next.js framework. Confirm **Framework Preset** shows `Next.js`.

- [ ] **Step 4: Override install command**

Expand **"Build and Output Settings"** → toggle **Install Command** to override → set to:
```
cd ../.. && npm install
```

Leave **Build Command** and **Output Directory** at defaults (`next build` and `.next`).

- [ ] **Step 5: Do NOT deploy yet**

Do not click **Deploy** — set env vars first (Task 4).

---

### Task 4: Set environment variables

> Get values from Supabase dashboard → Project → Settings → API.

- [ ] **Step 1: Add NEXT_PUBLIC_SUPABASE_URL**

In the Vercel import screen (or after project creation: Settings → Environment Variables):
- **Name:** `NEXT_PUBLIC_SUPABASE_URL`
- **Value:** `https://<your-project-ref>.supabase.co`
- **Environments:** check Production, Preview, Development

- [ ] **Step 2: Add NEXT_PUBLIC_SUPABASE_ANON_KEY**

- **Name:** `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- **Value:** the `anon` / `public` key from Supabase
- **Environments:** check Production, Preview, Development

- [ ] **Step 3: Verify both vars are saved**

In Vercel → Settings → Environment Variables, confirm both rows appear for all three environments.

---

### Task 5: Deploy and verify

- [ ] **Step 1: Trigger first deployment**

Click **Deploy** (or in the Vercel dashboard, trigger a manual deployment from `feature/TRA-8-vercel-deployment` branch).

Since `apps/web` is a stub package.json with no actual Next.js installed, the build will fail — this is expected at this stage. The goal is to confirm Vercel picks up the correct root directory and install command.

Expected output in build logs:
```
Running "cd ../.. && npm install"
...
```

If the install command runs from repo root, Task 5 is successful regardless of build failure.

- [ ] **Step 2: Verify install command ran from monorepo root**

In build logs, confirm:
- `cd ../.. && npm install` executed
- `node_modules` resolved from repo root (not `apps/web`)

- [ ] **Step 3: Check Turborepo remote cache setting**

Go to Vercel project → Settings → scroll to **"Turborepo Remote Cache"** section.
Confirm it shows as enabled or detected.

If the section does not appear, it will activate once Next.js is scaffolded (TRA-26) and a real build runs.

---

### Task 6: Verify preview deployments

- [ ] **Step 1: Confirm GitHub integration is active**

Go to Vercel project → Settings → Git → confirm the `tracktal` repo is connected and **"Preview Deployments"** is enabled for all branches.

- [ ] **Step 2: Check deployment comment setting**

In Settings → Git → confirm **"Comment on Pull Requests"** is enabled. This posts the preview URL as a PR comment automatically.

---

### Task 7: Commit, PR, and close out

- [ ] **Step 1: Commit the spec (already done)**

The spec was committed to `main` directly during brainstorming. No further commits needed on this feature branch unless config files are added.

- [ ] **Step 2: Open PR**

```bash
gh pr create \
  --title "feat(TRA-8): set up Vercel deployment for Next.js frontend" \
  --body "Connects apps/web to Vercel with monorepo install command override. Sets Supabase env vars. Preview deployments enabled on all PRs. Domain wiring deferred to TRA-XX.

Closes TRA-8" \
  --base main \
  --head feature/TRA-8-vercel-deployment
```

TRA-43 was created in Task 2 — use that ID.

- [ ] **Step 3: Post PR link to Linear**

Open Linear → TRA-8 → add comment with the GitHub PR URL.
Set status to **In Review**.

- [ ] **Step 4: Mark TRA-8 as Done after merge**

After the PR is merged to `main`, set TRA-8 status to **Done** in Linear.
