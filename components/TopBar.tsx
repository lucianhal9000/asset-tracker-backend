'use client'

import { useMemo } from 'react'
import { usePathname } from 'next/navigation'
import { Bell } from 'lucide-react'

function titleFromPath(pathname: string) {
  const first = pathname.split('?')[0].split('#')[0].split('/').filter(Boolean)[0]
  if (!first) return 'Dashboard'
  return first.charAt(0).toUpperCase() + first.slice(1)
}

export default function TopBar() {
  const pathname = usePathname()
  const title = useMemo(() => titleFromPath(pathname), [pathname])

  return (
    <header
      style={{
        height: 60,
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        padding: '0 24px',
        justifyContent: 'space-between',
        background: 'var(--bg)',
      }}
    >
      <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>
        {title}
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <button
          type="button"
          aria-label="Notifications"
          style={{
            width: 36,
            height: 36,
            borderRadius: 999,
            border: '1px solid var(--border)',
            background: 'var(--surface)',
            display: 'grid',
            placeItems: 'center',
            color: 'var(--text-muted)',
            cursor: 'pointer',
            transition: 'background 150ms ease, color 150ms ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'var(--surface-elevated)'
            e.currentTarget.style.color = 'var(--text-primary)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'var(--surface)'
            e.currentTarget.style.color = 'var(--text-muted)'
          }}
        >
          <Bell size={16} />
        </button>
        <div
          aria-label="User avatar"
          style={{
            width: 34,
            height: 34,
            borderRadius: 999,
            background: 'var(--surface-elevated)',
            border: '1px solid var(--border)',
          }}
        />
      </div>
    </header>
  )
}

