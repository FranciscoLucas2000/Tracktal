# Auth Pages Design — TRA-31

**Date:** 2026-06-18  
**Ticket:** [TRA-31](https://linear.app/tracktal/issue/TRA-31/t-027-auth-pages-login-signup)  
**Scope:** Login, signup, forgot password, reset password pages + auth callback route

---

## Overview

Build `/login`, `/signup`, `/forgot-password`, and `/reset-password` pages using Supabase Auth. Email + password only (no OAuth). Redirect to `/dashboard` after successful auth. Middleware protecting `/dashboard/*` is already in place.

---

## Visual Style

- Dark card (`bg-card` / `#1e293b`) on dark muted background (`#0f172a`)
- Card: `max-w-sm`, `rounded-lg`, `border`, `p-8`, `shadow-sm` (existing auth layout)
- Error state: red banner above input fields
- Inputs include password show/hide toggle (lucide-react `Eye`/`EyeOff`)

---

## Architecture

### New files

```
apps/web/
  components/
    auth/
      AuthForm.tsx              ← shared 'use client' component
  app/
    (auth)/
      forgot-password/
        page.tsx                ← standalone forgot-password page
      reset-password/
        page.tsx                ← standalone reset-password page
    auth/
      confirm/
        route.ts                ← Supabase email callback handler
```

### Modified files

```
apps/web/
  app/
    (auth)/
      login/page.tsx            ← replace stub with <AuthForm mode="login" />
      signup/page.tsx           ← replace stub with <AuthForm mode="signup" />
```

---

## Component: AuthForm

**Location:** `apps/web/components/auth/AuthForm.tsx`

```tsx
interface AuthFormProps {
  mode: 'login' | 'signup'
}
```

**State:**
- `email: string`
- `password: string`
- `loading: boolean`
- `error: string | null` — shown as red banner above fields
- `message: string | null` — shown as info banner (post-signup email confirm)

**Behavior:**

| Mode | Supabase call | Success | Error |
|------|--------------|---------|-------|
| login | `signInWithPassword({ email, password })` | `router.push('/dashboard')` | Set `error` |
| signup | `signUp({ email, password })` | Session present → `router.push('/dashboard')`; no session → set `message` "Check your email to confirm your account" | Set `error` |

**Client-side validation:** Non-empty email + password before submit. No complex rules — Supabase enforces server-side.

**UI elements:**
- Error banner: `bg-red-500/15 border border-red-500/40 text-red-300` above inputs
- Info banner: `bg-indigo-500/12 border border-indigo-500/30 text-indigo-300` for post-signup message
- Password field: show/hide toggle with `Eye`/`EyeOff` from lucide-react
- Submit button: disabled + spinner while `loading`
- Footer links:
  - Login mode: "Forgot password?" → `/forgot-password` | "No account? Sign up" → `/signup`
  - Signup mode: "Already have an account? Sign in" → `/login`

---

## Page: /forgot-password

**Location:** `apps/web/app/(auth)/forgot-password/page.tsx`

Standalone client component (no `AuthForm` reuse).

**Behavior:**
- Email input + submit
- Calls `supabase.auth.resetPasswordForEmail(email, { redirectTo: \`${process.env.NEXT_PUBLIC_SITE_URL}/auth/confirm?next=/reset-password\` })`
- `NEXT_PUBLIC_SITE_URL` must be set in Vercel env vars (e.g. `https://tracktal.com` in prod, `http://localhost:3000` locally)
- Always shows success message after submit regardless of whether email exists: "If that email is registered, you'll receive a reset link shortly."
- "← Back to sign in" link → `/login`

---

## Route: /auth/confirm

**Location:** `apps/web/app/auth/confirm/route.ts`

Next.js route handler (GET).

**Behavior:**
1. Read `code` and `next` from query params
2. Call `supabase.auth.exchangeCodeForSession(code)`
3. Success → redirect to `next` (default: `/dashboard`)
4. Error → redirect to `/login?error=link-expired`

---

## Page: /reset-password

**Location:** `apps/web/app/(auth)/reset-password/page.tsx`

Standalone client component.

**Behavior:**
- If no active session → redirect to `/login`
- Two fields: new password + confirm password
- Client-side: validate fields match before submit
- Calls `supabase.auth.updateUser({ password })`
- Success → `router.push('/dashboard')`
- Error → red banner above fields

**Note:** Session is established by `/auth/confirm` before redirect, so user is authenticated when they arrive here. No middleware changes needed.

---

## Error Handling Summary

| Page | Error source | Display |
|------|-------------|---------|
| Login | Invalid credentials, network | Red banner above fields |
| Signup | Email already registered, weak password | Red banner above fields |
| Forgot password | None exposed to user | Always show success message |
| Reset password | Passwords don't match (client) | Red banner above fields |
| Reset password | Supabase updateUser error | Red banner above fields |
| Auth confirm | Invalid/expired code | Redirect to `/login?error=link-expired` |

---

## Out of Scope (v1)

- OAuth providers
- Magic link login
- Email change flow
- Account deletion
- Password strength meter
