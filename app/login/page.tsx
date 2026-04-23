'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Lock } from 'lucide-react'

import { auth } from '../../../lib/api'

export default function LoginPage() {
  const router = useRouter()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function onSubmit() {
    if (isSubmitting) return
    setError(null)
    setIsSubmitting(true)
    try {
      await auth.login(username, password)
      router.push('/dashboard')
    } catch (e) {
      setError('Invalid username or password.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'var(--bg)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <div
        style={{
          width: 400,
          padding: 40,
          background: 'var(--surface)',
          border: '1px solid var(--border)',
          borderRadius: 8,
        }}
      >
        <div
          style={{
            fontFamily:
              '"DM Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
            textTransform: 'uppercase',
            letterSpacing: '0.14em',
            fontSize: 12,
            color: 'var(--accent)',
            userSelect: 'none',
          }}
        >
          LIOCICHLA
        </div>
        <div style={{ marginTop: 6, fontSize: 12, color: 'var(--text-muted)' }}>
          Asset Intelligence Platform
        </div>

        <div style={{ height: 1, background: 'var(--border)', margin: '24px 0' }} />

        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          <div>
            <div
              style={{
                fontSize: 11,
                textTransform: 'uppercase',
                letterSpacing: '0.12em',
                color: 'var(--text-muted)',
                marginBottom: 8,
                userSelect: 'none',
              }}
            >
              Username
            </div>
            <div style={{ borderBottom: '1px solid var(--border)', transition: 'border-color 200ms ease' }}>
              <input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') onSubmit()
                }}
                autoComplete="username"
                style={{
                  width: '100%',
                  padding: '8px 0',
                  background: 'transparent',
                  border: 'none',
                  outline: 'none',
                  color: 'var(--text-primary)',
                  fontSize: 13,
                }}
                onFocus={(e) => {
                  const wrap = e.currentTarget.parentElement
                  if (wrap) wrap.style.borderBottomColor = 'var(--accent)'
                }}
                onBlur={(e) => {
                  const wrap = e.currentTarget.parentElement
                  if (wrap) wrap.style.borderBottomColor = 'var(--border)'
                }}
              />
            </div>
          </div>

          <div>
            <div
              style={{
                fontSize: 11,
                textTransform: 'uppercase',
                letterSpacing: '0.12em',
                color: 'var(--text-muted)',
                marginBottom: 8,
                userSelect: 'none',
              }}
            >
              Password
            </div>
            <div style={{ borderBottom: '1px solid var(--border)', transition: 'border-color 200ms ease' }}>
              <input
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') onSubmit()
                }}
                type="password"
                autoComplete="current-password"
                style={{
                  width: '100%',
                  padding: '8px 0',
                  background: 'transparent',
                  border: 'none',
                  outline: 'none',
                  color: 'var(--text-primary)',
                  fontSize: 13,
                }}
                onFocus={(e) => {
                  const wrap = e.currentTarget.parentElement
                  if (wrap) wrap.style.borderBottomColor = 'var(--accent)'
                }}
                onBlur={(e) => {
                  const wrap = e.currentTarget.parentElement
                  if (wrap) wrap.style.borderBottomColor = 'var(--border)'
                }}
              />
            </div>
          </div>
        </div>

        <button
          type="button"
          onClick={onSubmit}
          disabled={isSubmitting}
          style={{
            width: '100%',
            marginTop: 32,
            height: 44,
            background: 'var(--accent)',
            borderRadius: 4,
            border: 'none',
            cursor: isSubmitting ? 'default' : 'pointer',
            opacity: isSubmitting ? 0.9 : 1,
            transition: 'opacity 150ms ease',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontFamily:
              '"DM Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
            textTransform: 'uppercase',
            letterSpacing: '0.12em',
            fontSize: 13,
          }}
          onMouseEnter={(e) => {
            if (!isSubmitting) e.currentTarget.style.opacity = '0.9'
          }}
          onMouseLeave={(e) => {
            if (!isSubmitting) e.currentTarget.style.opacity = '1'
          }}
        >
          {isSubmitting ? (
            <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span className="liocichlaDot" />
              <span className="liocichlaDot" style={{ animationDelay: '120ms' }} />
              <span className="liocichlaDot" style={{ animationDelay: '240ms' }} />
            </span>
          ) : (
            'AUTHENTICATE'
          )}
        </button>

        {error ? (
          <div style={{ marginTop: 12, color: 'var(--danger)', fontSize: 12 }}>{error}</div>
        ) : null}

        <div
          style={{
            marginTop: 24,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 8,
            color: 'var(--text-muted)',
            fontSize: 11,
            userSelect: 'none',
          }}
        >
          <Lock size={14} />
          Secured with OAuth 2.0
        </div>
      </div>

      <style jsx global>{`
        .liocichlaDot {
          width: 6px;
          height: 6px;
          border-radius: 999px;
          background: rgba(255, 255, 255, 0.9);
          animation: liocichlaDots 900ms ease-in-out infinite;
        }

        @keyframes liocichlaDots {
          0%,
          100% {
            transform: translateY(0);
            opacity: 0.5;
          }
          50% {
            transform: translateY(-3px);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  )
}

