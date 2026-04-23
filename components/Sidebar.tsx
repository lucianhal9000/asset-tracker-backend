'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  Activity,
  FileText,
  LayoutDashboard,
  LogOut,
  Map,
  MapPin,
} from 'lucide-react'

const navItems = [
  { label: 'Dashboard', href: '/dashboard', Icon: LayoutDashboard },
  { label: 'Assets', href: '/assets', Icon: MapPin },
  { label: 'Map', href: '/map', Icon: Map },
  { label: 'Telemetry', href: '/telemetry', Icon: Activity },
  { label: 'Logs', href: '/logs', Icon: FileText },
] as const

function pageIsActive(pathname: string, href: string) {
  if (href === '/') return pathname === '/'
  return pathname === href || pathname.startsWith(`${href}/`)
}

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <aside
      style={{
        position: 'fixed',
        left: 0,
        top: 0,
        width: 220,
        height: '100vh',
        background: 'var(--surface)',
        borderRight: '1px solid var(--border)',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <div style={{ padding: '18px 16px 10px 16px' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            fontFamily: '"DM Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
            textTransform: 'uppercase',
            letterSpacing: '0.14em',
            fontSize: 12,
            color: 'var(--accent)',
            userSelect: 'none',
          }}
        >
          <span
            aria-hidden="true"
            style={{
              width: 8,
              height: 8,
              borderRadius: 999,
              background: 'var(--success)',
              display: 'inline-block',
              animation: 'liocichlaPulse 1.4s ease-in-out infinite',
              boxShadow: '0 0 0 0 rgba(34, 201, 122, 0.6)',
            }}
          />
          LIOCICHLA
        </div>
      </div>

      <nav style={{ paddingTop: 8, display: 'flex', flexDirection: 'column' }}>
        {navItems.map(({ label, href, Icon }) => {
          const active = pageIsActive(pathname, href)
          return (
            <Link
              key={href}
              href={href}
              style={{
                padding: '10px 16px',
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                fontSize: 13,
                color: active ? 'var(--text-primary)' : 'var(--text-muted)',
                background: active ? 'var(--surface-elevated)' : 'transparent',
                borderLeft: active ? '2px solid var(--accent)' : '2px solid transparent',
                transition: 'background 150ms ease, color 150ms ease',
                textDecoration: 'none',
              }}
              onMouseEnter={(e) => {
                if (active) return
                e.currentTarget.style.background = 'var(--surface-elevated)'
                e.currentTarget.style.color = 'var(--text-primary)'
              }}
              onMouseLeave={(e) => {
                if (active) return
                e.currentTarget.style.background = 'transparent'
                e.currentTarget.style.color = 'var(--text-muted)'
              }}
            >
              <Icon size={16} />
              <span>{label}</span>
            </Link>
          )
        })}
      </nav>

      <div style={{ marginTop: 'auto', padding: 16 }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: 12,
            padding: '10px 12px',
            border: '1px solid var(--border)',
            borderRadius: 10,
            background: 'var(--surface-elevated)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div
              aria-hidden="true"
              style={{
                width: 22,
                height: 22,
                borderRadius: 999,
                background: 'var(--accent)',
              }}
            />
            <div style={{ fontSize: 13, color: 'var(--text-primary)' }}>lucia</div>
          </div>
          <button
            type="button"
            aria-label="Logout"
            style={{
              display: 'grid',
              placeItems: 'center',
              width: 34,
              height: 34,
              borderRadius: 10,
              border: '1px solid var(--border)',
              background: 'transparent',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              transition: 'background 150ms ease, color 150ms ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'var(--surface)'
              e.currentTarget.style.color = 'var(--text-primary)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent'
              e.currentTarget.style.color = 'var(--text-muted)'
            }}
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>

      <style jsx global>{`
        @keyframes liocichlaPulse {
          0% {
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(34, 201, 122, 0.6);
          }
          70% {
            transform: scale(1.15);
            box-shadow: 0 0 0 10px rgba(34, 201, 122, 0);
          }
          100% {
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(34, 201, 122, 0);
          }
        }
      `}</style>
    </aside>
  )
}

