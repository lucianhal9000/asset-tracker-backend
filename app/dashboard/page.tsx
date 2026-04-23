'use client'

import { useEffect, useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { assets, type Asset, type AssetStats } from '../../../lib/api'

type LoadState<T> =
  | { status: 'idle' | 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; message: string }

function StatCard({
  label,
  value,
  dotColor,
  loading,
}: {
  label: string
  value: number
  dotColor: string
  loading: boolean
}) {
  return (
    <div
      style={{
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: 8,
        padding: 24,
        position: 'relative',
        transition: 'transform 150ms ease',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-1px)'
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0px)'
      }}
    >
      <div
        aria-hidden="true"
        style={{
          position: 'absolute',
          top: 14,
          right: 14,
          width: 10,
          height: 10,
          borderRadius: 999,
          background: dotColor,
        }}
      />

      {loading ? (
        <div>
          <div
            style={{
              width: 80,
              height: 40,
              borderRadius: 8,
              background: 'var(--surface-elevated)',
              animation: 'liocichlaPulseSkel 1.2s ease-in-out infinite',
            }}
          />
          <div
            style={{
              marginTop: 10,
              width: 90,
              height: 14,
              borderRadius: 8,
              background: 'var(--surface-elevated)',
              animation: 'liocichlaPulseSkel 1.2s ease-in-out infinite',
            }}
          />
        </div>
      ) : (
        <div>
          <div
            style={{
              fontSize: 32,
              fontFamily:
                '"DM Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
              color: 'var(--text-primary)',
              lineHeight: '40px',
            }}
          >
            {value}
          </div>
          <div
            style={{
              marginTop: 10,
              fontSize: 11,
              textTransform: 'uppercase',
              letterSpacing: '0.12em',
              color: 'var(--text-muted)',
              userSelect: 'none',
            }}
          >
            {label}
          </div>
        </div>
      )}

      <style jsx global>{`
        @keyframes liocichlaPulseSkel {
          0%,
          100% {
            opacity: 0.55;
          }
          50% {
            opacity: 1;
          }
        }
      `}</style>
    </div>
  )
}

function StatusDot({ status }: { status: Asset['status'] }) {
  const color =
    status === 'active'
      ? 'var(--success)'
      : status === 'inactive'
        ? 'var(--text-muted)'
        : 'var(--danger)'

  return (
    <span
      aria-label={status}
      style={{
        width: 10,
        height: 10,
        borderRadius: 999,
        background: color,
        display: 'inline-block',
      }}
    />
  )
}

export default function DashboardPage() {
  const [statsState, setStatsState] = useState<LoadState<AssetStats>>({ status: 'idle' })
  const [recentState, setRecentState] = useState<LoadState<Asset[]>>({ status: 'idle' })

  const activityData = useMemo(
    () => [
      { day: 'Mon', value: 14 },
      { day: 'Tue', value: 18 },
      { day: 'Wed', value: 10 },
      { day: 'Thu', value: 22 },
      { day: 'Fri', value: 17 },
      { day: 'Sat', value: 26 },
      { day: 'Sun', value: 20 },
    ],
    []
  )

  useEffect(() => {
    let mounted = true

    ;(async () => {
      try {
        setStatsState({ status: 'loading' })
        const data = await assets.stats()
        if (!mounted) return
        setStatsState({ status: 'success', data })
      } catch {
        if (!mounted) return
        setStatsState({ status: 'error', message: 'Failed to load stats.' })
      }
    })()

    ;(async () => {
      try {
        setRecentState({ status: 'loading' })
        const data = await assets.list()
        if (!mounted) return
        setRecentState({ status: 'success', data: data.slice(0, 5) })
      } catch {
        if (!mounted) return
        setRecentState({ status: 'error', message: 'Failed to load recent assets.' })
      }
    })()

    return () => {
      mounted = false
    }
  }, [])

  const statsLoading = statsState.status === 'loading' || statsState.status === 'idle'
  const stats =
    statsState.status === 'success'
      ? statsState.data
      : { total: 0, active: 0, inactive: 0, lost: 0 }

  return (
    <div>
      {statsState.status === 'error' ? (
        <div style={{ color: 'var(--danger)', fontSize: 13, marginBottom: 16 }}>
          {statsState.message}
        </div>
      ) : null}

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, minmax(0, 1fr))',
          gap: 16,
        }}
      >
        <StatCard label="Total" value={stats.total} dotColor="var(--accent)" loading={statsLoading} />
        <StatCard label="Active" value={stats.active} dotColor="var(--success)" loading={statsLoading} />
        <StatCard
          label="Inactive"
          value={stats.inactive}
          dotColor="var(--text-muted)"
          loading={statsLoading}
        />
        <StatCard label="Lost" value={stats.lost} dotColor="var(--danger)" loading={statsLoading} />
      </div>

      <div style={{ display: 'flex', gap: 24, marginTop: 24 }}>
        <div style={{ width: '65%' }}>
          <div
            style={{
              fontSize: 14,
              fontFamily:
                '"DM Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
              color: 'var(--text-muted)',
              marginBottom: 12,
              userSelect: 'none',
            }}
          >
            Activity
          </div>

          <div
            style={{
              background: 'var(--surface)',
              border: '1px solid var(--border)',
              borderRadius: 8,
              padding: 16,
              height: 280,
            }}
          >
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={activityData} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
                <CartesianGrid
                  vertical={false}
                  stroke="var(--border)"
                  strokeOpacity={0.45}
                />
                <XAxis
                  dataKey="day"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
                />
                <YAxis
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
                  width={32}
                />
                <Tooltip
                  cursor={{ stroke: 'var(--border)', strokeWidth: 1 }}
                  contentStyle={{
                    background: 'var(--surface-elevated)',
                    border: '1px solid var(--border)',
                    borderRadius: 8,
                    color: 'var(--text-primary)',
                    fontFamily:
                      '"DM Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
                    fontSize: 12,
                  }}
                  labelStyle={{ color: 'var(--text-muted)' }}
                  itemStyle={{ color: 'var(--text-primary)' }}
                />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="var(--accent)"
                  strokeWidth={2}
                  fill="var(--accent)"
                  fillOpacity={0.2}
                  dot={false}
                  activeDot={{ r: 3 }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div style={{ width: '35%' }}>
          <div
            style={{
              fontSize: 14,
              fontFamily:
                '"DM Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
              color: 'var(--text-muted)',
              marginBottom: 12,
              userSelect: 'none',
            }}
          >
            Recent Assets
          </div>

          <div
            style={{
              background: 'var(--surface)',
              border: '1px solid var(--border)',
              borderRadius: 8,
              padding: '8px 16px',
            }}
          >
            {recentState.status === 'error' ? (
              <div style={{ color: 'var(--danger)', fontSize: 13, padding: '12px 0' }}>
                {recentState.message}
              </div>
            ) : null}

            {recentState.status === 'loading' || recentState.status === 'idle' ? (
              <div style={{ padding: '12px 0', display: 'flex', flexDirection: 'column', gap: 14 }}>
                {Array.from({ length: 5 }).map((_, i) => (
                  <div
                    key={i}
                    style={{
                      height: 40,
                      borderRadius: 8,
                      background: 'var(--surface-elevated)',
                      animation: 'liocichlaPulseSkel 1.2s ease-in-out infinite',
                    }}
                  />
                ))}
              </div>
            ) : null}

            {recentState.status === 'success' ? (
              <div>
                {recentState.data.map((a, i) => (
                  <motion.div
                    key={a.id}
                    initial={{ y: -10, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.25, delay: i * 0.05 }}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '12px 0',
                      borderBottom: i === recentState.data.length - 1 ? 'none' : '1px solid var(--border)',
                    }}
                  >
                    <div style={{ minWidth: 0 }}>
                      <div style={{ color: 'var(--text-primary)', fontSize: 13, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {a.name}
                      </div>
                      <div
                        style={{
                          marginTop: 4,
                          fontSize: 11,
                          color: 'var(--text-muted)',
                          fontFamily:
                            '"DM Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                        }}
                      >
                        {a.id}
                      </div>
                    </div>
                    <StatusDot status={a.status} />
                  </motion.div>
                ))}
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  )
}

