import React from 'react'

const WelcomeCard: React.FC = () => {
  return (
    <div
      className="animate-slide-up"
      style={{
        maxWidth: 640,
        margin: '60px auto',
        textAlign: 'center',
      }}
    >
      <div
        className="animate-float"
        style={{
          width: 80,
          height: 80,
          borderRadius: 24,
          background: 'var(--gradient-primary)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 24px',
          boxShadow: '0 0 30px rgba(0, 212, 255, 0.3), 0 0 60px rgba(0, 212, 255, 0.1)',
          fontSize: 36,
        }}
      >
        🤖
      </div>
      <h2
        style={{
          fontSize: 28,
          fontWeight: 800,
          marginBottom: 12,
          background: 'var(--gradient-primary)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
        }}
      >
        昇腾AI竞赛智能助教
      </h2>
      <p style={{ color: 'var(--text-secondary)', fontSize: 15, lineHeight: 1.7, marginBottom: 8 }}>
        基于 RAG 技术的智能问答系统
      </p>
      <p style={{ color: 'var(--text-tertiary)', fontSize: 13, lineHeight: 1.6 }}>
        请在下方输入框中输入您的问题，或点击推荐问题开始对话
      </p>
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          gap: 24,
          marginTop: 32,
        }}
      >
        {[
          { icon: '⚡', label: '实时问答', desc: '基于知识库' },
          { icon: '🎯', label: '精准检索', desc: 'RAG增强' },
          { icon: '📊', label: '来源追溯', desc: '可信引用' },
        ].map((item) => (
          <div
            key={item.label}
            className="glass-card-static"
            style={{
              padding: '16px 20px',
              textAlign: 'center',
              minWidth: 120,
            }}
          >
            <div style={{ fontSize: 24, marginBottom: 8 }}>{item.icon}</div>
            <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>
              {item.label}
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-tertiary)', marginTop: 2 }}>
              {item.desc}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default WelcomeCard
