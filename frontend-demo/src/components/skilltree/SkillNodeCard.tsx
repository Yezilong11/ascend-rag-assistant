import { Card, Typography, Tag, Progress, Space } from 'antd'
import type { SkillNode, SkillLevel, SkillType } from '../../types'

const { Text } = Typography

interface SkillNodeCardProps {
  skill: SkillNode
  onClick?: (skill: SkillNode) => void
}

const levelColors: Record<SkillLevel, string> = {
  beginner: 'green',
  intermediate: 'blue',
  advanced: 'orange',
  expert: 'red',
}

const levelLabels: Record<SkillLevel, string> = {
  beginner: '初级',
  intermediate: '中级',
  advanced: '高级',
  expert: '专家',
}

const typeLabels: Record<SkillType, string> = {
  technical: '技术类',
  theoretical: '理论类',
  practical: '实践类',
  competition: '竞赛类',
}

export function SkillNodeCard({ skill, onClick }: SkillNodeCardProps) {
  return (
    <Card
      hoverable
      className="!rounded-lg !border-gray-200 hover:!border-blue-400 transition-colors cursor-pointer"
      onClick={() => onClick?.(skill)}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <Text strong className="text-base">{skill.name}</Text>
            <Tag color={levelColors[skill.level]} className="!rounded-full">
              {levelLabels[skill.level]}
            </Tag>
            <Tag className="!rounded-full">{typeLabels[skill.skill_type]}</Tag>
          </div>

          <Text type="secondary" className="text-sm line-clamp-2">
            {skill.description}
          </Text>

          <div className="mt-4 space-y-2">
            <div className="flex items-center justify-between text-sm">
              <Text type="secondary">完成进度</Text>
              <Text strong>{skill.completion_rate}%</Text>
            </div>
            <Progress
              percent={skill.completion_rate}
              showInfo={false}
              strokeColor={{
                '0%': '#3b82f6',
                '100%': '#60a5fa',
              }}
              trailColor="#e2e8f0"
              size="small"
            />
          </div>

          <div className="mt-3 flex items-center gap-4 text-xs text-gray-400">
            <Space size="small">
              <span>⏱️ {skill.learning_time}h</span>
              <span>📚 {skill.resources.length} 资源</span>
              <span>🔗 {skill.prerequisites.length} 前置</span>
            </Space>
          </div>
        </div>
      </div>
    </Card>
  )
}
