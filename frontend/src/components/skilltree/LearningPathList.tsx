import React from 'react'
import { List, Tag, Typography } from 'antd'
import { ClockCircleOutlined } from '@ant-design/icons'
import type { LearningPath } from '@/types/skillTree'
import { SKILL_LEVEL_MAP } from '@/utils/constants'

interface LearningPathListProps {
  paths: Record<string, LearningPath>
  skillNodes: Record<string, { name: string }>
}

const LearningPathList: React.FC<LearningPathListProps> = ({ paths, skillNodes }) => {
  const pathList = Object.values(paths)

  if (pathList.length === 0) {
    return <Typography.Text type="secondary">暂无学习路径，请先生成</Typography.Text>
  }

  return (
    <List
      dataSource={pathList}
      renderItem={(path) => (
        <List.Item>
          <List.Item.Meta
            title={
              <span>
                学习路径{' '}
                <Tag color="blue">{SKILL_LEVEL_MAP[path.difficulty] ?? path.difficulty}</Tag>
              </span>
            }
            description={
              <div>
                <div style={{ marginBottom: 4 }}>
                  <ClockCircleOutlined style={{ marginRight: 4 }} />
                  预计 {path.estimated_time} 小时
                </div>
                <div>
                  {path.skill_ids.map((id) => {
                    const node = skillNodes[id]
                    return node ? (
                      <Tag key={id} style={{ marginBottom: 4 }}>
                        {node.name}
                      </Tag>
                    ) : null
                  })}
                </div>
              </div>
            }
          />
        </List.Item>
      )}
    />
  )
}

export default LearningPathList
