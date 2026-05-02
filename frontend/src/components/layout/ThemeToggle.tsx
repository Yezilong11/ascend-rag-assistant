import React from 'react'
import { useAppStore } from '@/stores/appStore'
import { MoonOutlined, SunOutlined } from '@ant-design/icons'

const ThemeToggle: React.FC = () => {
  const theme = useAppStore((s) => s.theme)
  const setTheme = useAppStore((s) => s.setTheme)

  const handleToggle = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark')
  }

  return (
    <button
      onClick={handleToggle}
      style={{
        background: 'var(--bg-glass)',
        border: '1px solid var(--border-glass)',
        borderRadius: 'var(--radius-sm)',
        color: 'var(--neon-blue)',
        width: 36,
        height: 36,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        cursor: 'pointer',
        transition: 'all var(--transition-normal)',
        fontSize: 16,
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = 'var(--neon-blue)'
        e.currentTarget.style.boxShadow = 'var(--shadow-glow-blue)'
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = 'var(--border-glass)'
        e.currentTarget.style.boxShadow = 'none'
      }}
    >
      {theme === 'dark' ? <MoonOutlined /> : <SunOutlined />}
    </button>
  )
}

export default ThemeToggle
