import React from 'react'
import { BookOutlined, ClockCircleOutlined } from '@ant-design/icons'
import type { SkillNode } from '@/types/skillTree'
import { SKILL_LEVEL_MAP, SKILL_TYPE_MAP } from '@/utils/constants'

interface SkillNodeCardProps {
  node: SkillNode
  onClick?: (node: SkillNode) => void
}

const levelStyleMap: Record<string, { bg: string; border: string; color: string; glow: string }> = {
  beginner: {
    bg: 'rgba(0, 255, 136, 0.08)',
    border: 'rgba(0, 255, 136, 0.2)',
    color: 'var(--neon-green)',
    glow: 'var(--shadow-glow-blue)',
  },
  intermediate: {
    bg: 'rgba(0, 212, 255, 0.08)',
    border: 'rgba(0, 212, 255, 0.2)',
    color: 'var(--neon-blue)',
    glow: 'var(--shadow-glow-blue)',
  },
  advanced: {
    bg: 'rgba(255, 184, 0, 0.08)',
    border: 'rgba(255, 184, 0, 0.2)',
    color: 'var(--neon-amber)',
    glow: 'var(--shadow-glow-blue)',
  },
  expert: {
    bg: 'rgba(255, 45, 120, 0.08)',
    border: 'rgba(255, 45, 120, 0.2)',
    color: 'var(--neon-pink)',
    glow: 'var(--shadow-glow-pink)',
  },
}

const SkillNodeCard: React.FC<SkillNodeCardProps> = ({ node, onClick }) => {
  const style = levelStyleMap[node.level] ?? levelStyleMap.intermediate!

  return (
    <div
      onClick={() => onClick?.(node)}
      style={{
        padding: '12px 16px',
        borderRadius: 'var(--radius-sm)',
        background: style.bg,
        border: `1px solid ${style.border}`,
        cursor: 'pointer',
        marginBottom: 8,
        transition: 'all var(--transition-normal)',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.boxShadow = style.glow
        e.currentTarget.style.transform = 'translateX(4px)'
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = 'none'
        e.currentTarget.style.transform = 'translateX(0)'
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 6,
        }}
      >
        <span style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: 13 }}>
          {node.name}
        </span>
        <span
          style={{
            padding: '2px 8px',
            borderRadius: 20,
            background: style.bg,
            border: `1px solid ${style.border}`,
            color: style.color,
            fontSize: 11,
            fontWeight: 500,
          }}
        >
          {SKILL_LEVEL_MAP[node.level] ?? node.level}
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
        {node.description}
      </div>
      <div style={{ display: 'flex', gap: 8, alignItems: 'center', fontSize: 11 }}>
        <span style={{ color: 'var(--neon-purple)' }}>
          <BookOutlined /> {SKILL_TYPE_MAP[node.type] ?? node.type}
        </span>
        <span style={{ color: 'var(--text-tertiary)' }}>
          <ClockCircleOutlined /> {node.learning_time}h
        </span>
        <div
          style={{
            flex: 1,
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
              width: `${node.completion_rate}%`,
              transition: 'width 0.5s ease',
              boxShadow: '0 0 6px rgba(0, 212, 255, 0.3)',
            }}
          />
        </div>
        <span style={{ color: 'var(--text-tertiary)', fontSize: 10 }}>{node.completion_rate}%</span>
      </div>
    </div>
  )
}

export default SkillNodeCard
