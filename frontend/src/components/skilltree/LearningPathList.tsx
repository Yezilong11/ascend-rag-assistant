import React from 'react'
import { ClockCircleOutlined, NodeIndexOutlined } from '@ant-design/icons'
import type { LearningPath } from '@/types/skillTree'
import { SKILL_LEVEL_MAP } from '@/utils/constants'

interface LearningPathListProps {
  paths: Record<string, LearningPath>
  skillNodes: Record<string, { name: string }>
}

const difficultyColorMap: Record<string, { bg: string; border: string; color: string }> = {
  beginner: {
    bg: 'rgba(0, 255, 136, 0.06)',
    border: 'rgba(0, 255, 136, 0.15)',
    color: 'var(--neon-green)',
  },
  intermediate: {
    bg: 'rgba(0, 212, 255, 0.06)',
    border: 'rgba(0, 212, 255, 0.15)',
    color: 'var(--neon-blue)',
  },
  advanced: {
    bg: 'rgba(255, 184, 0, 0.06)',
    border: 'rgba(255, 184, 0, 0.15)',
    color: 'var(--neon-amber)',
  },
  expert: {
    bg: 'rgba(255, 45, 120, 0.06)',
    border: 'rgba(255, 45, 120, 0.15)',
    color: 'var(--neon-pink)',
  },
}

const LearningPathList: React.FC<LearningPathListProps> = ({ paths, skillNodes }) => {
  const pathList = Object.values(paths)

  if (pathList.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: 24, color: 'var(--text-tertiary)' }}>
        <NodeIndexOutlined
          style={{ fontSize: 32, marginBottom: 8, display: 'block', opacity: 0.3 }}
        />
        暂无学习路径，请点击"生成路径"按钮
      </div>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {pathList.map((path) => {
        const style = difficultyColorMap[path.difficulty] ?? difficultyColorMap.intermediate!
        return (
          <div
            key={path.path_id}
            style={{
              padding: '12px 16px',
              borderRadius: 'var(--radius-sm)',
              background: style.bg,
              border: `1px solid ${style.border}`,
            }}
          >
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: 8,
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <NodeIndexOutlined style={{ color: style.color }} />
                <span style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: 13 }}>
                  学习路径
                </span>
              </div>
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
                {SKILL_LEVEL_MAP[path.difficulty] ?? path.difficulty}
              </span>
            </div>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                marginBottom: 8,
                color: 'var(--text-tertiary)',
                fontSize: 12,
              }}
            >
              <ClockCircleOutlined /> 预计 {path.estimated_time} 小时 · {path.skill_ids.length}{' '}
              个技能
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
              {path.skill_ids.map((id, index) => {
                const node = skillNodes[id]
                return node ? (
                  <span
                    key={id}
                    style={{
                      padding: '2px 8px',
                      borderRadius: 12,
                      background: 'rgba(0, 212, 255, 0.08)',
                      border: '1px solid rgba(0, 212, 255, 0.15)',
                      color: 'var(--neon-blue)',
                      fontSize: 11,
                    }}
                  >
                    {index > 0 && '→ '}
                    {node.name}
                  </span>
                ) : null
              })}
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default LearningPathList
