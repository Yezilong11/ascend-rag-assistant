import React, { useCallback, useEffect, useState } from 'react'
import { BookOutlined, ClockCircleOutlined } from '@ant-design/icons'
import { Slider } from 'antd'
import type { SkillNode } from '@/types/skillTree'
import { SKILL_LEVEL_MAP, SKILL_TYPE_MAP } from '@/utils/constants'

interface SkillNodeCardProps {
  node: SkillNode
  onClick?: (node: SkillNode) => void
  onUpdateCompletion?: (skillId: string, rate: number) => void
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

const PRESET_VALUES = [0, 25, 50, 75, 100]

function getCompletionColor(rate: number): string {
  if (rate <= 0) return '#ff3366'
  if (rate >= 100) return '#00ff88'
  if (rate <= 50) {
    const t = rate / 50
    const r = Math.round(255 * (1 - t) + 255 * t)
    const g = Math.round(51 * (1 - t) + 184 * t)
    const b = Math.round(102 * (1 - t) + 0 * t)
    return `rgb(${r}, ${g}, ${b})`
  }
  const t = (rate - 50) / 50
  const r = Math.round(255 * (1 - t) + 0 * t)
  const g = Math.round(184 * (1 - t) + 255 * t)
  const b = Math.round(0 * (1 - t) + 136 * t)
  return `rgb(${r}, ${g}, ${b})`
}

const SkillNodeCard: React.FC<SkillNodeCardProps> = ({ node, onClick, onUpdateCompletion }) => {
  const style = levelStyleMap[node.level] ?? levelStyleMap.intermediate!
  const [localRate, setLocalRate] = useState<number | null>(null)
  const displayRate = localRate ?? Math.round(node.completion_rate)

  useEffect(() => {
    if (localRate !== null && Math.round(node.completion_rate) === localRate) {
      setLocalRate(null)
    }
  }, [node.completion_rate, localRate])

  const handleSliderChange = useCallback((value: number) => {
    setLocalRate(value)
  }, [])

  const handleSliderAfterChange = useCallback(
    (value: number) => {
      onUpdateCompletion?.(node.id, value)
    },
    [onUpdateCompletion, node.id],
  )

  const handlePresetClick = useCallback(
    (value: number) => {
      setLocalRate(null)
      onUpdateCompletion?.(node.id, value)
    },
    [onUpdateCompletion, node.id],
  )

  const completionColor = getCompletionColor(displayRate)

  return (
    <div
      style={{
        padding: '12px 16px',
        borderRadius: 'var(--radius-sm)',
        background: style.bg,
        border: `1px solid ${style.border}`,
        cursor: onClick ? 'pointer' : 'default',
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
        onClick={() => onClick?.(node)}
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
        onClick={() => onClick?.(node)}
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
      <div style={{ display: 'flex', gap: 8, alignItems: 'center', fontSize: 11, marginBottom: 8 }}>
        <span style={{ color: 'var(--neon-purple)' }}>
          <BookOutlined /> {SKILL_TYPE_MAP[node.type] ?? node.type}
        </span>
        <span style={{ color: 'var(--text-tertiary)' }}>
          <ClockCircleOutlined /> {node.learning_time}h
        </span>
      </div>
      {onUpdateCompletion ? (
        <div onClick={(e) => e.stopPropagation()}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ flex: 1 }}>
              <Slider
                min={0}
                max={100}
                step={1}
                value={displayRate}
                onChange={handleSliderChange}
                onAfterChange={handleSliderAfterChange}
                styles={{
                  track: { background: completionColor },
                  rail: { background: 'var(--bg-tertiary)' },
                  handle: {
                    borderColor: completionColor,
                    boxShadow: `0 0 6px ${completionColor}66`,
                  },
                }}
              />
            </div>
            <span
              style={{
                color: completionColor,
                fontSize: 12,
                fontWeight: 600,
                minWidth: 36,
                textAlign: 'right',
                transition: 'color 0.2s ease',
              }}
            >
              {displayRate}%
            </span>
          </div>
          <div style={{ display: 'flex', gap: 4, marginTop: -4 }}>
            {PRESET_VALUES.map((value) => {
              const presetColor = getCompletionColor(value)
              const isActive = displayRate === value
              return (
                <button
                  key={value}
                  onClick={() => handlePresetClick(value)}
                  style={{
                    flex: 1,
                    padding: '2px 0',
                    borderRadius: 4,
                    background: isActive ? `${presetColor}20` : 'var(--bg-tertiary)',
                    border: isActive
                      ? `1px solid ${presetColor}80`
                      : '1px solid var(--border-glass)',
                    color: isActive ? presetColor : 'var(--text-tertiary)',
                    fontSize: 10,
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                    fontWeight: isActive ? 600 : 400,
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = `${presetColor}18`
                    e.currentTarget.style.color = presetColor
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = isActive ? `${presetColor}20` : 'var(--bg-tertiary)'
                    e.currentTarget.style.color = isActive ? presetColor : 'var(--text-tertiary)'
                  }}
                >
                  {value}%
                </button>
              )
            })}
          </div>
        </div>
      ) : (
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
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
                background: completionColor,
                width: `${node.completion_rate}%`,
                transition: 'width 0.3s ease, background 0.3s ease',
                boxShadow: `0 0 6px ${completionColor}44`,
              }}
            />
          </div>
          <span
            style={{
              color: completionColor,
              fontSize: 10,
              minWidth: 32,
              textAlign: 'right',
              fontWeight: 500,
              transition: 'color 0.2s ease',
            }}
          >
            {displayRate}%
          </span>
        </div>
      )}
    </div>
  )
}

export default SkillNodeCard
