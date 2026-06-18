# Next.js Project Scaffold (TRA-30) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold `apps/web/` with Next.js 14 (app router), Tailwind CSS, Shadcn/ui (slate, CSS variables), Tremor, Recharts, and Supabase SSR client; `build`, `type-check`, and `lint` all pass.

**Architecture:** All config files written manually (no interactive CLIs). Route groups `(auth)` and `(dashboard)` isolate layouts at `/login|/signup` and `/dashboard`. `middleware.ts` checks Supabase session on every matched request and redirects accordingly.

**Tech Stack:** Next.js 14, TypeScript 5, Tailwind CSS v3, tailwindcss-animate, Shadcn/ui (slate, CSS variables), @tremor/react v3, Recharts v2, @supabase/ssr, @supabase/supabase-js, lucide-react, clsx, tailwind-merge, class-variance-authority

---

### Task 1: Create feature branch

**Files:** None

- [ ] **Step 1: Checkout branch**

```bash
git checkout -b feature/TRA-30-nextjs-scaffold
```

Expected: `Switched to a new branch 'feature/TRA-30-nextjs-scaffold'`

---

### Task 2: Write package.json and install dependencies

**Files:**
- Modify: `apps/web/package.json`
- Modify: `package-lock.json` (root)

- [ ] **Step 1: Write apps/web/package.json**

Replace the entire contents of `apps/web/package.json` with:

```json
{
  "name": "@tracktal/web",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "next": "14",
    "react": "^18",
    "react-dom": "^18",
    "@supabase/ssr": "latest",
    "@supabase/supabase-js": "latest",
    "@tremor/react": "^3",
    "recharts": "^2",
    "class-variance-authority": "latest",
    "clsx": "latest",
    "tailwind-merge": "latest",
    "lucide-react": "latest"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "autoprefixer": "^10",
    "eslint": "^8",
    "eslint-config-next": "14",
    "postcss": "^8",
    "tailwindcss": "^3",
    "tailwindcss-animate": "latest",
    "typescript": "^5"
  }
}
```

- [ ] **Step 2: Install from repo root**

Run from the repo root (`tracktal/`):

```bash
npm install
```

Expected: Resolves workspace packages. No errors. `package-lock.json` updated.

- [ ] **Step 3: Verify Next.js installed**

```bash
npm ls next --workspace=@tracktal/web
```

Expected: `next@14.x.x` listed.

- [ ] **Step 4: Commit**

```bash
git add apps/web/package.json package-lock.json
git commit -m "feat(TRA-30): add Next.js 14 and all scaffold dependencies"
```

---

### Task 3: Write Next.js config files

**Files:**
- Create: `apps/web/tsconfig.json`
- Create: `apps/web/next.config.ts`
- Create: `apps/web/postcss.config.mjs`
- Create: `apps/web/.eslintrc.json`
- Create: `apps/web/.gitignore`

- [ ] **Step 1: Write tsconfig.json**

Create `apps/web/tsconfig.json`:

```json
{
  "compilerOptions": {
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

- [ ] **Step 2: Write next.config.ts**

Create `apps/web/next.config.ts`:

```typescript
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {}

export default nextConfig
```

- [ ] **Step 3: Write postcss.config.mjs**

Create `apps/web/postcss.config.mjs`:

```javascript
/** @type {import('postcss').Config} */
const config = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}

export default config
```

- [ ] **Step 4: Write .eslintrc.json**

Create `apps/web/.eslintrc.json`:

```json
{
  "extends": ["next/core-web-vitals"]
}
```

- [ ] **Step 5: Write .gitignore**

Create `apps/web/.gitignore`:

```
# Next.js
.next/
out/

# Dependencies
node_modules/

# Env files
.env*.local

# Build
*.tsbuildinfo
next-env.d.ts
```

- [ ] **Step 6: Commit**

```bash
git add apps/web/tsconfig.json apps/web/next.config.ts apps/web/postcss.config.mjs apps/web/.eslintrc.json apps/web/.gitignore
git commit -m "feat(TRA-30): add Next.js config files"
```

---

### Task 4: Write Tailwind and Shadcn/ui setup

**Files:**
- Create: `apps/web/tailwind.config.ts`
- Create: `apps/web/app/globals.css`
- Create: `apps/web/components.json`
- Create: `apps/web/lib/utils.ts`

- [ ] **Step 1: Write tailwind.config.ts**

Create `apps/web/tailwind.config.ts`:

```typescript
import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ['class'],
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './node_modules/@tremor/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}

export default config
```

- [ ] **Step 2: Write app/globals.css**

Create `apps/web/app/globals.css` with Tailwind directives and shadcn slate CSS variables:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;
    --primary: 210 40% 98%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 212.7 26.8% 83.9%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

- [ ] **Step 3: Write components.json**

Create `apps/web/components.json`:

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "app/globals.css",
    "baseColor": "slate",
    "cssVariables": true,
    "prefix": ""
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  },
  "iconLibrary": "lucide"
}
```

- [ ] **Step 4: Write lib/utils.ts**

Create `apps/web/lib/utils.ts`:

```typescript
import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

- [ ] **Step 5: Commit**

```bash
git add apps/web/tailwind.config.ts apps/web/app/globals.css apps/web/components.json apps/web/lib/utils.ts
git commit -m "feat(TRA-30): add Tailwind config and shadcn/ui slate CSS variables"
```

---

### Task 5: Write root app layout and landing page

**Files:**
- Create: `apps/web/app/layout.tsx`
- Create: `apps/web/app/page.tsx`
- Create: `apps/web/app/favicon.ico` (placeholder)

- [ ] **Step 1: Write root layout**

Create `apps/web/app/layout.tsx`:

```typescript
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Tracktal',
  description: 'Job market intelligence for Portugal and Spain.',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
```

- [ ] **Step 2: Write landing page**

Create `apps/web/app/page.tsx`:

```typescript
export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold tracking-tight">Tracktal</h1>
      <p className="mt-4 text-lg text-muted-foreground">
        Job market intelligence for Portugal and Spain.
      </p>
    </main>
  )
}
```

- [ ] **Step 3: Create empty public directory**

The `public/` directory is needed for Next.js static file serving. Create a placeholder:

```bash
mkdir -p apps/web/public
```

- [ ] **Step 4: Verify build**

From `apps/web/`:

```bash
npm run build
```

Expected: Build succeeds. Output shows route `/` as a static page.

- [ ] **Step 5: Commit**

```bash
git add apps/web/app/layout.tsx apps/web/app/page.tsx apps/web/public/
git commit -m "feat(TRA-30): add root layout and landing page placeholder"
```

---

### Task 6: Scaffold route groups

**Files:**
- Create: `apps/web/app/(auth)/layout.tsx`
- Create: `apps/web/app/(auth)/login/page.tsx`
- Create: `apps/web/app/(auth)/signup/page.tsx`
- Create: `apps/web/app/(dashboard)/layout.tsx`
- Create: `apps/web/app/(dashboard)/dashboard/page.tsx`
- Create: `apps/web/.env.local`

- [ ] **Step 1: Write (auth) layout**

Create `apps/web/app/(auth)/layout.tsx`:

```typescript
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/40">
      {children}
    </div>
  )
}
```

- [ ] **Step 2: Write login page**

Create `apps/web/app/(auth)/login/page.tsx`:

```typescript
export default function LoginPage() {
  return (
    <div className="w-full max-w-sm space-y-4 rounded-lg border bg-card p-8 shadow-sm">
      <h1 className="text-2xl font-semibold tracking-tight">Sign in</h1>
      <p className="text-sm text-muted-foreground">Coming soon.</p>
    </div>
  )
}
```

- [ ] **Step 3: Write signup page**

Create `apps/web/app/(auth)/signup/page.tsx`:

```typescript
export default function SignupPage() {
  return (
    <div className="w-full max-w-sm space-y-4 rounded-lg border bg-card p-8 shadow-sm">
      <h1 className="text-2xl font-semibold tracking-tight">Create account</h1>
      <p className="text-sm text-muted-foreground">Coming soon.</p>
    </div>
  )
}
```

- [ ] **Step 4: Write (dashboard) layout**

Create `apps/web/app/(dashboard)/layout.tsx`:

```typescript
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen">
      <aside className="w-64 shrink-0 border-r bg-muted/20" />
      <main className="flex-1 p-8">{children}</main>
    </div>
  )
}
```

- [ ] **Step 5: Write dashboard page**

Create `apps/web/app/(dashboard)/dashboard/page.tsx`:

```typescript
export default function DashboardPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
      <p className="text-muted-foreground">Coming soon.</p>
    </div>
  )
}
```

- [ ] **Step 6: Create .env.local with placeholder values**

Create `apps/web/.env.local`:

```
NEXT_PUBLIC_SUPABASE_URL=https://placeholder.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=placeholder-anon-key
```

These placeholders let the build and type-check pass locally. Real values are set in Vercel dashboard and `.env.local` once the Supabase project is live (TRA-8).

- [ ] **Step 7: Verify .env.local is gitignored**

```bash
git status
```

Expected: `.env.local` does NOT appear in untracked files (covered by `apps/web/.gitignore`).

- [ ] **Step 8: Verify build**

```bash
npm run build
```

Expected: Build succeeds. Routes listed: `/`, `/login`, `/signup`, `/dashboard`.

- [ ] **Step 9: Commit**

```bash
git add apps/web/app/
git commit -m "feat(TRA-30): scaffold (auth) and (dashboard) route groups"
```

---

### Task 7: Add Supabase SSR client helpers

**Files:**
- Create: `apps/web/lib/supabase/client.ts`
- Create: `apps/web/lib/supabase/server.ts`

- [ ] **Step 1: Write browser client**

Create `apps/web/lib/supabase/client.ts`:

```typescript
import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}
```

- [ ] **Step 2: Write server client**

Create `apps/web/lib/supabase/server.ts`:

```typescript
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export function createClient() {
  const cookieStore = cookies()

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll()
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            )
          } catch {
            // Read-only in Server Components — safe to ignore
          }
        },
      },
    }
  )
}
```

- [ ] **Step 3: Verify type-check**

```bash
npm run type-check
```

Expected: No errors.

- [ ] **Step 4: Commit**

```bash
git add apps/web/lib/supabase/
git commit -m "feat(TRA-30): add Supabase SSR browser and server clients"
```

---

### Task 8: Add auth middleware

**Files:**
- Create: `apps/web/middleware.ts`

- [ ] **Step 1: Write middleware.ts**

Create `apps/web/middleware.ts`:

```typescript
import { createServerClient } from '@supabase/ssr'
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  let response = NextResponse.next({ request })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll()
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) =>
            request.cookies.set(name, value)
          )
          response = NextResponse.next({ request })
          cookiesToSet.forEach(({ name, value, options }) =>
            response.cookies.set(name, value, options)
          )
        },
      },
    }
  )

  const {
    data: { user },
  } = await supabase.auth.getUser()

  const isDashboard = request.nextUrl.pathname.startsWith('/dashboard')
  const isAuthPage =
    request.nextUrl.pathname === '/login' ||
    request.nextUrl.pathname === '/signup'

  if (isDashboard && !user) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  if (isAuthPage && user) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  return response
}

export const config = {
  matcher: ['/dashboard/:path*', '/login', '/signup'],
}
```

- [ ] **Step 2: Verify type-check**

```bash
npm run type-check
```

Expected: No errors.

- [ ] **Step 3: Commit**

```bash
git add apps/web/middleware.ts
git commit -m "feat(TRA-30): add middleware protecting /dashboard routes"
```

---

### Task 9: Final verification and PR

**Files:** None

- [ ] **Step 1: Run full build**

From `apps/web/`:

```bash
npm run build
```

Expected output includes:
```
Route (app)                Size     First Load JS
┌ ○ /                      ...
├ ○ /dashboard             ...
├ ○ /login                 ...
└ ○ /signup                ...
```
No errors. No TypeScript warnings.

- [ ] **Step 2: Run type-check**

```bash
npm run type-check
```

Expected: Silent output (no errors).

- [ ] **Step 3: Run lint**

```bash
npm run lint
```

Expected: `✔ No ESLint warnings or errors`

- [ ] **Step 4: Mark TRA-30 In Review in Linear**

Update ticket TRA-30 status → `In Review`.

- [ ] **Step 5: Open PR**

```bash
git push -u origin feature/TRA-30-nextjs-scaffold
```

Then open a PR targeting `main`. Title: `feat(TRA-30): Next.js 14 project scaffold`. Link the Linear ticket in the PR description.
