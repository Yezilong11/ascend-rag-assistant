import React from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { MessageOutlined, ApartmentOutlined, SettingOutlined, GlobalOutlined, PictureOutlined } from '@ant-design/icons'

const menuItems = [
  {
    key: '/chat',
    icon: <MessageOutlined />,
    label: '智能问答',
  },
  {
    key: '/skill-tree',
    icon: <ApartmentOutlined />,
    label: '技能树',
  },
  {
    key: '/rss',
    icon: <GlobalOutlined />,
    label: 'RSS 资讯',
  },
  {
    key: '/multimodal',
    icon: <PictureOutlined />,
    label: '多模态知识库',
  },
  {
    key: '/settings',
    icon: <SettingOutlined />,
    label: '系统设置',
  },
]

const Sidebar: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <aside
      style={{
        width: 'var(--sidebar-width)',
        height: '100vh',
        position: 'fixed',
        left: 0,
        top: 0,
        bottom: 0,
        background: 'var(--bg-glass)',
        backdropFilter: 'blur(var(--blur-heavy))',
        WebkitBackdropFilter: 'blur(var(--blur-heavy))',
        borderRight: '1px solid var(--border-glass)',
        display: 'flex',
        flexDirection: 'column',
        zIndex: 20,
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          height: 'var(--header-height)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 10,
          borderBottom: '1px solid var(--border-glass)',
          padding: '0 20px',
        }}
      >
        <div
          style={{
            width: 32,
            height: 32,
            borderRadius: 8,
            background: 'var(--gradient-primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 18,
            boxShadow: '0 0 15px rgba(0, 212, 255, 0.3)',
          }}
        >
          🤖
        </div>
        <span
          style={{
            fontSize: 15,
            fontWeight: 700,
            background: 'var(--gradient-primary)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}
        >
          AI助教
        </span>
      </div>

      <nav style={{ flex: 1, padding: '12px 12px' }}>
        {menuItems.map((item) => {
          const isActive = location.pathname === item.key
          return (
            <div
              key={item.key}
              onClick={() => navigate(item.key)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 12,
                padding: '12px 16px',
                borderRadius: 'var(--radius-sm)',
                cursor: 'pointer',
                marginBottom: 4,
                color: isActive ? 'var(--neon-blue)' : 'var(--text-secondary)',
                background: isActive ? 'rgba(0, 212, 255, 0.08)' : 'transparent',
                border: isActive ? '1px solid rgba(0, 212, 255, 0.15)' : '1px solid transparent',
                transition: 'all var(--transition-normal)',
                position: 'relative',
                overflow: 'hidden',
              }}
              onMouseEnter={(e) => {
                if (!isActive) {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)'
                  e.currentTarget.style.color = 'var(--text-primary)'
                  e.currentTarget.style.borderColor = 'var(--border-glass)'
                }
              }}
              onMouseLeave={(e) => {
                if (!isActive) {
                  e.currentTarget.style.background = 'transparent'
                  e.currentTarget.style.color = 'var(--text-secondary)'
                  e.currentTarget.style.borderColor = 'transparent'
                }
              }}
            >
              {isActive && (
                <div
                  style={{
                    position: 'absolute',
                    left: 0,
                    top: '50%',
                    transform: 'translateY(-50%)',
                    width: 3,
                    height: '60%',
                    borderRadius: '0 2px 2px 0',
                    background: 'var(--gradient-primary)',
                    boxShadow: '0 0 8px var(--neon-blue)',
                  }}
                />
              )}
              <span style={{ fontSize: 16, display: 'flex' }}>{item.icon}</span>
              <span style={{ fontSize: 14, fontWeight: isActive ? 600 : 400 }}>{item.label}</span>
            </div>
          )
        })}
      </nav>

      <div
        style={{
          padding: '16px 20px',
          borderTop: '1px solid var(--border-glass)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div className="glow-dot glow-dot-blue" style={{ width: 6, height: 6 }} />
          <span style={{ fontSize: 11, color: 'var(--text-tertiary)' }}>系统运行中</span>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
