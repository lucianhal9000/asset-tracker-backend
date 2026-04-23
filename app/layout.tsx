import type { ReactNode } from 'react'

import './globals.css'
import Sidebar from '../components/Sidebar'
import TopBar from '../components/TopBar'

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0 }}>
        <div style={{ display: 'flex' }}>
          <Sidebar />
          <main
            style={{
              marginLeft: 220,
              minHeight: '100vh',
              background: 'var(--bg)',
              width: '100%',
            }}
          >
            <TopBar />
            <div style={{ padding: 24 }}>{children}</div>
          </main>
        </div>
      </body>
    </html>
  )
}

