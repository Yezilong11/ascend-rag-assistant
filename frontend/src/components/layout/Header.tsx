import React from 'react'
import ThemeToggle from './ThemeToggle'

const AppHeader: React.FC = () => {
  return (
    <header
      style={{
        height: 'var(--header-height)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 32px',
        background: 'var(--bg-glass)',
        backdropFilter: 'blur(var(--blur-glass))',
        WebkitBackdropFilter: 'blur(var(--blur-glass))',
        borderBottom: '1px solid var(--border-glass)',
        position: 'sticky',
        top: 0,
        zIndex: 10,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <div
          style={{
            width: 8,
            height: 8,
            borderRadius: '50%',
            background: 'var(--neon-blue)',
            boxShadow: '0 0 10px var(--neon-blue), 0 0 20px rgba(0, 212, 255, 0.3)',
            animation: 'pulseGlow 2s ease-in-out infinite',
          }}
        />
        <h1
          style={{
            margin: 0,
            fontSize: 18,
            fontWeight: 700,
            background: 'var(--gradient-primary)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            letterSpacing: '0.5px',
          }}
        >
          昇腾AI竞赛智能助教
        </h1>
        <span
          style={{
            fontSize: 11,
            padding: '2px 8px',
            borderRadius: 20,
            background: 'rgba(0, 212, 255, 0.1)',
            border: '1px solid rgba(0, 212, 255, 0.2)',
            color: 'var(--neon-blue)',
            fontWeight: 500,
          }}
        >
          RAG Powered
        </span>
      </div>
      <ThemeToggle />
    </header>
  )
}

export default AppHeader
