import React from 'react'

const ThinkingIndicator: React.FC = () => {
  return (
    <div
      className="animate-fade-in"
      style={{
        display: 'flex',
        alignItems: 'center',
        padding: '12px 16px',
        gap: 12,
      }}
    >
      <div
        style={{
          width: 32,
          height: 32,
          borderRadius: 10,
          background: 'var(--gradient-primary)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 16,
          boxShadow: '0 0 12px rgba(0, 212, 255, 0.2)',
        }}
      >
        🤖
      </div>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          padding: '10px 18px',
          borderRadius: '16px 16px 16px 4px',
          background: 'var(--bg-glass)',
          border: '1px solid var(--border-glass)',
        }}
      >
        <div style={{ display: 'flex', gap: 4 }}>
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              style={{
                width: 6,
                height: 6,
                borderRadius: '50%',
                background: 'var(--neon-blue)',
                animation: `pulse 1.4s ease-in-out ${i * 0.2}s infinite`,
                boxShadow: '0 0 6px var(--neon-blue)',
              }}
            />
          ))}
        </div>
        <span style={{ color: 'var(--text-tertiary)', fontSize: 13 }}>AI正在思考中...</span>
      </div>
    </div>
  )
}

export default ThinkingIndicator
