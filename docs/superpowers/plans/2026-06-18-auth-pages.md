# Auth Pages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `/login`, `/signup`, `/forgot-password`, and `/reset-password` pages with full Supabase email+password auth flow.

**Architecture:** Shared `AuthForm` client component handles login and signup via `mode` prop. Three standalone client components handle forgot-password and reset-password. A Next.js route handler at `/auth/confirm` exchanges Supabase email codes for sessions. No Server Actions — all auth calls use the existing `createBrowserClient` from `@/lib/supabase/client`.

**Tech Stack:** Next.js 14 App Router, `@supabase/ssr`, Tailwind CSS with shadcn/ui CSS variables, lucide-react (Eye/EyeOff/Loader2)

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `apps/web/components/auth/AuthForm.tsx` | CREATE | Shared login/signup client component |
| `apps/web/app/(auth)/login/page.tsx` | MODIFY | Thin wrapper: `<AuthForm mode="login" />` |
| `apps/web/app/(auth)/signup/page.tsx` | MODIFY | Thin wrapper: `<AuthForm mode="signup" />` |
| `apps/web/app/auth/confirm/route.ts` | CREATE | Route handler: exchange code → session |
| `apps/web/app/(auth)/forgot-password/page.tsx` | CREATE | Email input → Supabase resetPasswordForEmail |
| `apps/web/app/(auth)/reset-password/page.tsx` | CREATE | New password → Supabase updateUser |
| `apps/web/.env.example` | MODIFY | Add NEXT_PUBLIC_SITE_URL |

---

## Task 1: Create AuthForm component

**Files:**
- Create: `apps/web/components/auth/AuthForm.tsx`

- [ ] **Step 1: Create the file with full implementation**

```tsx
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Eye, EyeOff, Loader2 } from 'lucide-react'
import { createClient } from '@/lib/supabase/client'

interface AuthFormProps {
  mode: 'login' | 'signup'
}

export default function AuthForm({ mode }: AuthFormProps) {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setMessage(null)

    if (!email || !password) {
      setError('Email and password are required.')
      return
    }

    setLoading(true)
    const supabase = createClient()

    if (mode === 'login') {
      const { error } = await supabase.auth.signInWithPassword({ email, password })
      if (error) {
        setError(error.message)
        setLoading(false)
        return
      }
      router.refresh()
      router.push('/dashboard')
      return
    }

    const { data, error } = await supabase.auth.signUp({ email, password })
    if (error) {
      setError(error.message)
      setLoading(false)
      return
    }
    if (data.session) {
      router.refresh()
      router.push('/dashboard')
    } else {
      setMessage('Check your email to confirm your account.')
      setLoading(false)
    }
  }

  return (
    <div className="w-full max-w-sm space-y-6 rounded-lg border bg-card p-8 shadow-sm">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Tracktal</h1>
        <p className="text-sm text-muted-foreground">
          {mode === 'login' ? 'Sign in to your account' : 'Create your account'}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="rounded-md border border-destructive/40 bg-destructive/15 px-3 py-2 text-sm text-destructive-foreground">
            {error}
          </div>
        )}
        {message && (
          <div className="rounded-md border border-blue-500/40 bg-blue-500/15 px-3 py-2 text-sm text-blue-300">
            {message}
          </div>
        )}

        <div className="space-y-2">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={loading}
            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
          />
          <div className="relative">
            <input
              type={showPassword ? 'text' : 'password'}
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
              className="w-full rounded-md border border-input bg-background px-3 py-2 pr-10 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
            />
            <button
              type="button"
              onClick={() => setShowPassword((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              aria-label={showPassword ? 'Hide password' : 'Show password'}
            >
              {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
        </div>

        {mode === 'login' && (
          <div className="text-right">
            <a href="/forgot-password" className="text-xs text-primary hover:underline">
              Forgot password?
            </a>
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="flex w-full items-center justify-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          {loading && <Loader2 size={16} className="animate-spin" />}
          {mode === 'login' ? 'Sign in' : 'Create account'}
        </button>
      </form>

      <p className="text-center text-sm text-muted-foreground">
        {mode === 'login' ? (
          <>
            No account?{' '}
            <a href="/signup" className="text-primary hover:underline">
              Sign up
            </a>
          </>
        ) : (
          <>
            Already have an account?{' '}
            <a href="/login" className="text-primary hover:underline">
              Sign in
            </a>
          </>
        )}
      </p>
    </div>
  )
}
```

- [ ] **Step 2: Type-check**

```bash
cd apps/web && npm run type-check
```

Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add apps/web/components/auth/AuthForm.tsx
git commit -m "feat(TRA-31): add AuthForm shared component"
```

---

## Task 2: Wire up login and signup pages

**Files:**
- Modify: `apps/web/app/(auth)/login/page.tsx`
- Modify: `apps/web/app/(auth)/signup/page.tsx`

- [ ] **Step 1: Replace login page stub**

```tsx
// apps/web/app/(auth)/login/page.tsx
import AuthForm from '@/components/auth/AuthForm'

export default function LoginPage() {
  return <AuthForm mode="login" />
}
```

- [ ] **Step 2: Replace signup page stub**

```tsx
// apps/web/app/(auth)/signup/page.tsx
import AuthForm from '@/components/auth/AuthForm'

export default function SignupPage() {
  return <AuthForm mode="signup" />
}
```

- [ ] **Step 3: Type-check**

```bash
cd apps/web && npm run type-check
```

Expected: no errors.

- [ ] **Step 4: Smoke test in browser**

```bash
cd apps/web && npm run dev
```

1. Open `http://localhost:3000/login` — see Tracktal card with email + password inputs, show/hide toggle, "Forgot password?" link, "Sign up" link.
2. Open `http://localhost:3000/signup` — see card with email + password inputs, "Sign in" link. No "Forgot password?".
3. Submit login with empty fields — see "Email and password are required." banner above inputs.

- [ ] **Step 5: Commit**

```bash
git add apps/web/app/"(auth)"/login/page.tsx apps/web/app/"(auth)"/signup/page.tsx
git commit -m "feat(TRA-31): wire AuthForm into login and signup pages"
```

---

## Task 3: Create auth/confirm route handler

**Files:**
- Create: `apps/web/app/auth/confirm/route.ts`

This route handler receives the Supabase magic link callback (`?code=...`), exchanges it for a session, and redirects to the target page. Used by both email confirmation (signup) and password reset flows.

- [ ] **Step 1: Create the route handler**

```ts
// apps/web/app/auth/confirm/route.ts
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const code = searchParams.get('code')
  const next = searchParams.get('next') ?? '/dashboard'

  if (!code) {
    return NextResponse.redirect(new URL('/login?error=link-expired', request.url))
  }

  const cookieStore = cookies()
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll()
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) =>
            cookieStore.set(name, value, options)
          )
        },
      },
    }
  )

  const { error } = await supabase.auth.exchangeCodeForSession(code)

  if (error) {
    return NextResponse.redirect(new URL('/login?error=link-expired', request.url))
  }

  return NextResponse.redirect(new URL(next, request.url))
}
```

- [ ] **Step 2: Type-check**

```bash
cd apps/web && npm run type-check
```

Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add apps/web/app/auth/confirm/route.ts
git commit -m "feat(TRA-31): add auth/confirm route handler for email callbacks"
```

---

## Task 4: Create forgot-password page

**Files:**
- Create: `apps/web/app/(auth)/forgot-password/page.tsx`

- [ ] **Step 1: Create the page**

```tsx
// apps/web/app/(auth)/forgot-password/page.tsx
'use client'

import { useState } from 'react'
import { Loader2 } from 'lucide-react'
import { createClient } from '@/lib/supabase/client'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    const supabase = createClient()
    await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${process.env.NEXT_PUBLIC_SITE_URL}/auth/confirm?next=/reset-password`,
    })
    // Always show success — don't reveal whether email is registered
    setSubmitted(true)
    setLoading(false)
  }

  return (
    <div className="w-full max-w-sm space-y-6 rounded-lg border bg-card p-8 shadow-sm">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Reset password</h1>
        <p className="text-sm text-muted-foreground">
          Enter your email to receive a reset link
        </p>
      </div>

      {submitted ? (
        <div className="rounded-md border border-blue-500/40 bg-blue-500/15 px-3 py-2 text-sm text-blue-300">
          If that email is registered, you&apos;ll receive a reset link shortly.
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={loading}
            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={loading}
            className="flex w-full items-center justify-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            {loading && <Loader2 size={16} className="animate-spin" />}
            Send reset link
          </button>
        </form>
      )}

      <p className="text-center text-sm">
        <a href="/login" className="text-primary hover:underline">
          ← Back to sign in
        </a>
      </p>
    </div>
  )
}
```

- [ ] **Step 2: Type-check**

```bash
cd apps/web && npm run type-check
```

Expected: no errors.

- [ ] **Step 3: Smoke test**

Open `http://localhost:3000/forgot-password`. Verify:
- Card renders with email input and "Send reset link" button
- Submit with any email → success message appears (no error even for unknown email)
- "← Back to sign in" link works

- [ ] **Step 4: Commit**

```bash
git add apps/web/app/"(auth)"/forgot-password/page.tsx
git commit -m "feat(TRA-31): add forgot-password page"
```

---

## Task 5: Create reset-password page

**Files:**
- Create: `apps/web/app/(auth)/reset-password/page.tsx`

This page is reached after `/auth/confirm` sets a session from the password-reset email link.

- [ ] **Step 1: Create the page**

```tsx
// apps/web/app/(auth)/reset-password/page.tsx
'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Eye, EyeOff, Loader2 } from 'lucide-react'
import { createClient } from '@/lib/supabase/client'

export default function ResetPasswordPage() {
  const router = useRouter()
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Guard: redirect to /login if no active session
  useEffect(() => {
    const supabase = createClient()
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (!session) router.replace('/login')
    })
  }, [router])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)

    if (password !== confirm) {
      setError('Passwords do not match.')
      return
    }

    setLoading(true)
    const supabase = createClient()
    const { error } = await supabase.auth.updateUser({ password })

    if (error) {
      setError(error.message)
      setLoading(false)
      return
    }

    router.push('/dashboard')
  }

  return (
    <div className="w-full max-w-sm space-y-6 rounded-lg border bg-card p-8 shadow-sm">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">New password</h1>
        <p className="text-sm text-muted-foreground">
          Choose a new password for your account
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="rounded-md border border-destructive/40 bg-destructive/15 px-3 py-2 text-sm text-destructive-foreground">
            {error}
          </div>
        )}

        <div className="space-y-2">
          <div className="relative">
            <input
              type={showPassword ? 'text' : 'password'}
              placeholder="New password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
              className="w-full rounded-md border border-input bg-background px-3 py-2 pr-10 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
            />
            <button
              type="button"
              onClick={() => setShowPassword((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              aria-label={showPassword ? 'Hide password' : 'Show password'}
            >
              {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
          <input
            type="password"
            placeholder="Confirm password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            required
            disabled={loading}
            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="flex w-full items-center justify-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          {loading && <Loader2 size={16} className="animate-spin" />}
          Update password
        </button>
      </form>
    </div>
  )
}
```

- [ ] **Step 2: Type-check**

```bash
cd apps/web && npm run type-check
```

Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add apps/web/app/"(auth)"/reset-password/page.tsx
git commit -m "feat(TRA-31): add reset-password page"
```

---

## Task 6: Environment variable + end-to-end verification

**Files:**
- Modify: `apps/web/.env.example`
- Modify: `apps/web/.env.local` (local only — not committed)

- [ ] **Step 1: Add NEXT_PUBLIC_SITE_URL to .env.example**

Add this line to `apps/web/.env.example`:

```
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

- [ ] **Step 2: Add to .env.local**

Add to `apps/web/.env.local` (already gitignored):

```
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

- [ ] **Step 3: Verify signup flow**

With dev server running (`npm run dev` in `apps/web`):

1. Go to `http://localhost:3000/signup`
2. Sign up with a real email address
3. If Supabase email confirmation is **disabled**: should redirect to `/dashboard`
4. If Supabase email confirmation is **enabled**: should see "Check your email to confirm your account."
5. Click the confirmation email link → lands on `/auth/confirm?code=...` → redirects to `/dashboard`

- [ ] **Step 4: Verify login flow**

1. Go to `http://localhost:3000/login`
2. Sign in with correct credentials → redirects to `/dashboard`
3. Sign in with wrong password → see red error banner: "Invalid login credentials"
4. Go to `/dashboard` while logged out → middleware redirects to `/login` ✓
5. Go to `/login` while logged in → middleware redirects to `/dashboard` ✓

- [ ] **Step 5: Verify forgot password flow**

1. Go to `http://localhost:3000/forgot-password`
2. Submit a registered email → success message shown (no redirect)
3. Click the reset link in email → lands on `/auth/confirm?code=...&next=/reset-password` → redirects to `/reset-password`
4. Enter mismatched passwords → see "Passwords do not match." banner
5. Enter matching passwords → redirects to `/dashboard`

- [ ] **Step 6: Commit**

```bash
git add apps/web/.env.example
git commit -m "feat(TRA-31): add NEXT_PUBLIC_SITE_URL env var"
```

- [ ] **Step 7: Open PR**

```bash
git push -u origin feature/TRA-31-auth-pages
gh pr create \
  --title "feat(TRA-31): auth pages (login, signup, forgot/reset password)" \
  --body "Closes TRA-31

## What
- Login and signup pages using shared \`AuthForm\` client component
- Full forgot-password + reset-password flow via Supabase email links
- \`/auth/confirm\` route handler exchanges email codes for sessions
- Password show/hide toggle, error banners, loading states

## Test
1. Sign up with email → confirm email → land on dashboard
2. Login with correct creds → dashboard; wrong creds → error banner
3. Forgot password → email link → reset form → dashboard
4. Unauthenticated \`/dashboard\` → redirected to \`/login\`"
```
