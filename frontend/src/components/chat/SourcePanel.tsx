import React from 'react'
import { FileTextOutlined } from '@ant-design/icons'
import type { Source } from '@/types/chat'

interface SourcePanelProps {
  sources: Source[]
}

const SourcePanel: React.FC<SourcePanelProps> = ({ sources }) => {
  if (sources.length === 0) return null

  return (
    <div style={{ marginTop: 8, marginLeft: 44 }}>
      <div
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 6,
          padding: '3px 10px',
          borderRadius: 20,
          background: 'rgba(0, 212, 255, 0.08)',
          border: '1px solid rgba(0, 212, 255, 0.2)',
          color: 'var(--neon-blue)',
          fontSize: 11,
          marginBottom: 8,
        }}
      >
        📎 参考 {sources.length} 个来源
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {sources.map((source, index) => (
          <div
            key={index}
            className="glass-card-static"
            style={{
              padding: '10px 14px',
              fontSize: 12,
              cursor: 'pointer',
            }}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                marginBottom: 4,
                color: 'var(--neon-blue)',
                fontWeight: 600,
              }}
            >
              <FileTextOutlined style={{ fontSize: 12 }} />
              来源 {index + 1}: {source.source}
            </div>
            <div
              style={{
                color: 'var(--text-tertiary)',
                lineHeight: 1.5,
                display: '-webkit-box',
                WebkitLineClamp: 3,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden',
              }}
            >
              {source.content}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default SourcePanel
