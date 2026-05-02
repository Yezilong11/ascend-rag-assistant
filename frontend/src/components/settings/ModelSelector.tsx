import React from 'react'
import type { ModelInfo } from '@/types/rag'

interface ModelSelectorProps {
  availableModels: Record<string, ModelInfo>
  value: string
  onChange: (value: string) => void
  disabled?: boolean
}

const ModelSelector: React.FC<ModelSelectorProps> = ({
  availableModels,
  value,
  onChange,
  disabled,
}) => {
  const entries = Object.entries(availableModels)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      {entries.map(([key, info]) => {
        const isSelected = value === key
        return (
          <div
            key={key}
            onClick={() => !disabled && onChange(key)}
            style={{
              padding: '10px 14px',
              borderRadius: 'var(--radius-sm)',
              background: isSelected ? 'rgba(0, 212, 255, 0.08)' : 'var(--bg-glass)',
              border: isSelected
                ? '1px solid rgba(0, 212, 255, 0.3)'
                : '1px solid var(--border-glass)',
              cursor: disabled ? 'not-allowed' : 'pointer',
              transition: 'all var(--transition-normal)',
              opacity: disabled ? 0.5 : 1,
            }}
            onMouseEnter={(e) => {
              if (!disabled && !isSelected) {
                e.currentTarget.style.borderColor = 'rgba(0, 212, 255, 0.15)'
                e.currentTarget.style.background = 'var(--bg-glass-hover)'
              }
            }}
            onMouseLeave={(e) => {
              if (!isSelected) {
                e.currentTarget.style.borderColor = 'var(--border-glass)'
                e.currentTarget.style.background = 'var(--bg-glass)'
              }
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div
                style={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  background: isSelected ? 'var(--neon-blue)' : 'var(--bg-tertiary)',
                  boxShadow: isSelected ? '0 0 6px var(--neon-blue)' : 'none',
                  transition: 'all var(--transition-normal)',
                }}
              />
              <div>
                <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: 13 }}>
                  {info.name}
                </div>
                <div style={{ color: 'var(--text-tertiary)', fontSize: 11 }}>
                  {info.description}
                </div>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default ModelSelector
