import React from 'react'
import { ApartmentOutlined } from '@ant-design/icons'
import type { SkillTreeSummary } from '@/types/skillTree'

interface SkillTreeListProps {
  skillTreeList: SkillTreeSummary[]
  isLoading: boolean
  onSelect: (id: string) => void
  selectedId?: string
}

const SkillTreeList: React.FC<SkillTreeListProps> = ({
  skillTreeList,
  isLoading,
  onSelect,
  selectedId,
}) => {
  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: 40 }}>
        <div
          style={{
            width: 32,
            height: 32,
            borderRadius: '50%',
            border: '2px solid var(--border-glass)',
            borderTopColor: 'var(--neon-blue)',
            animation: 'rotateGlow 1s linear infinite',
            margin: '0 auto 12px',
          }}
        />
        <div style={{ color: 'var(--text-tertiary)', fontSize: 13 }}>加载中...</div>
      </div>
    )
  }

  if (skillTreeList.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: 40, color: 'var(--text-tertiary)' }}>
        <ApartmentOutlined style={{ fontSize: 32, marginBottom: 12, display: 'block' }} />
        暂无技能树，请创建
      </div>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      {skillTreeList.map((item) => {
        const isSelected = selectedId === item.id
        return (
          <div
            key={item.id}
            onClick={() => onSelect(item.id)}
            className={isSelected ? 'neon-border' : ''}
            style={{
              padding: '14px 16px',
              borderRadius: 'var(--radius-sm)',
              background: isSelected ? 'rgba(0, 212, 255, 0.06)' : 'var(--bg-glass)',
              border: isSelected ? undefined : '1px solid var(--border-glass)',
              cursor: 'pointer',
              transition: 'all var(--transition-normal)',
              backdropFilter: 'blur(10px)',
              WebkitBackdropFilter: 'blur(10px)',
            }}
            onMouseEnter={(e) => {
              if (!isSelected) {
                e.currentTarget.style.borderColor = 'rgba(0, 212, 255, 0.2)'
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
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
              <div
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: 8,
                  background: 'var(--gradient-primary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 14,
                  color: '#fff',
                  boxShadow: '0 0 10px rgba(0, 212, 255, 0.2)',
                }}
              >
                <ApartmentOutlined />
              </div>
              <span style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: 14 }}>
                {item.name}
              </span>
            </div>
            <div
              style={{
                color: 'var(--text-tertiary)',
                fontSize: 12,
                lineHeight: 1.5,
                marginBottom: 8,
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden',
              }}
            >
              {item.description}
            </div>
            <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
              <span className="neon-tag">{item.skill_count} 个技能</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <div
                  style={{
                    width: 48,
                    height: 4,
                    borderRadius: 2,
                    background: 'var(--bg-tertiary)',
                    overflow: 'hidden',
                  }}
                >
                  <div
                    style={{
                      height: '100%',
                      borderRadius: 2,
                      background: 'var(--gradient-primary)',
                      width: `${item.completion_rate}%`,
                      transition: 'width 0.3s ease',
                    }}
                  />
                </div>
                <span style={{ color: 'var(--neon-blue)', fontSize: 10, fontWeight: 500 }}>
                  {item.completion_rate.toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default SkillTreeList
