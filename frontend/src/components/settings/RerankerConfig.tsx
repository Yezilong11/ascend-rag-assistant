import React from 'react'
import type { RerankerInfo } from '@/types/rag'

interface RerankerConfigProps {
  availableRerankers: Record<string, RerankerInfo>
  enabled: boolean
  model: string
  topK: number
  onEnabledChange: (enabled: boolean) => void
  onModelChange: (model: string) => void
  onTopKChange: (topK: number) => void
  disabled?: boolean
}

const RerankerConfig: React.FC<RerankerConfigProps> = ({
  availableRerankers,
  enabled,
  model,
  topK,
  onEnabledChange,
  onModelChange,
  onTopKChange,
  disabled,
}) => {
  const rerankerEntries = Object.entries(availableRerankers)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      <div
        onClick={() => !disabled && onEnabledChange(!enabled)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          cursor: disabled ? 'not-allowed' : 'pointer',
          padding: '8px 12px',
          borderRadius: 'var(--radius-sm)',
          background: 'var(--bg-glass)',
          border: '1px solid var(--border-glass)',
          transition: 'all var(--transition-normal)',
        }}
      >
        <div
          style={{
            width: 36,
            height: 20,
            borderRadius: 10,
            background: enabled ? 'var(--gradient-primary)' : 'var(--bg-tertiary)',
            position: 'relative',
            transition: 'all var(--transition-normal)',
            boxShadow: enabled ? '0 0 8px rgba(0, 212, 255, 0.3)' : 'none',
          }}
        >
          <div
            style={{
              width: 16,
              height: 16,
              borderRadius: '50%',
              background: '#fff',
              position: 'absolute',
              top: 2,
              left: enabled ? 18 : 2,
              transition: 'all var(--transition-normal)',
              boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
            }}
          />
        </div>
        <span style={{ color: 'var(--text-primary)', fontSize: 13, fontWeight: 500 }}>
          启用重排序
        </span>
      </div>

      {enabled && (
        <div className="animate-slide-up" style={{ paddingLeft: 8 }}>
          <div style={{ marginBottom: 10 }}>
            <div style={{ color: 'var(--text-secondary)', fontSize: 12, marginBottom: 6 }}>
              重排序模型
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              {rerankerEntries.map(([key, info]) => {
                const isSelected = model === key
                return (
                  <div
                    key={key}
                    onClick={() => !disabled && onModelChange(key)}
                    style={{
                      padding: '8px 12px',
                      borderRadius: 'var(--radius-sm)',
                      background: isSelected ? 'rgba(123, 47, 255, 0.08)' : 'transparent',
                      border: isSelected
                        ? '1px solid rgba(123, 47, 255, 0.2)'
                        : '1px solid transparent',
                      cursor: disabled ? 'not-allowed' : 'pointer',
                      transition: 'all var(--transition-normal)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 8,
                    }}
                  >
                    <div
                      style={{
                        width: 6,
                        height: 6,
                        borderRadius: '50%',
                        background: isSelected ? 'var(--neon-purple)' : 'var(--bg-tertiary)',
                        boxShadow: isSelected ? '0 0 4px var(--neon-purple)' : 'none',
                      }}
                    />
                    <span style={{ color: 'var(--text-primary)', fontSize: 12 }}>{info.name}</span>
                    <span style={{ color: 'var(--text-tertiary)', fontSize: 11 }}>
                      ({info.size})
                    </span>
                  </div>
                )
              })}
            </div>
          </div>

          <div>
            <div style={{ color: 'var(--text-secondary)', fontSize: 12, marginBottom: 6 }}>
              Top K: {topK}
            </div>
            <input
              type="range"
              min={1}
              max={10}
              value={topK}
              onChange={(e) => onTopKChange(Number(e.target.value))}
              disabled={disabled}
              style={{
                width: '100%',
                accentColor: 'var(--neon-purple)',
                height: 4,
              }}
            />
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: 10,
                color: 'var(--text-tertiary)',
              }}
            >
              <span>1</span>
              <span>10</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default RerankerConfig
