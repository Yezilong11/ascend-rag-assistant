import React from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import AppHeader from './Header'
import ParticleBackground from '@/components/effects/ParticleBackground'
import GlowOrbs from '@/components/effects/GlowOrbs'

const AppLayout: React.FC = () => {
  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <ParticleBackground />
      <GlowOrbs />
      <Sidebar />
      <div
        style={{
          marginLeft: 'var(--sidebar-width)',
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
          zIndex: 1,
        }}
      >
        <AppHeader />
        <main
          style={{
            flex: 1,
            padding: 24,
            minHeight: 0,
          }}
        >
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default AppLayout
