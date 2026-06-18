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
