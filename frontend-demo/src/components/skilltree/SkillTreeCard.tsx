import { Card, Typography, Badge, Space, Button, Dropdown } from 'antd'
import {
  DeleteOutlined,
  MoreOutlined,
  EditOutlined,
  EyeOutlined,
} from '@ant-design/icons'
import type { SkillTree } from '../../types'

const { Text, Title } = Typography

interface SkillTreeCardProps {
  skillTree: SkillTree
  onView?: (skillTree: SkillTree) => void
  onEdit?: (skillTree: SkillTree) => void
  onDelete?: (skillTreeId: string) => void
}

export function SkillTreeCard({
  skillTree,
  onView,
  onEdit,
  onDelete,
}: SkillTreeCardProps) {
  const skillCount = Object.keys(skillTree.skill_nodes || {}).length
  const pathCount = Object.keys(skillTree.learning_paths || {}).length

  const menuItems = [
    {
      key: 'view',
      icon: <EyeOutlined />,
      label: '查看详情',
      onClick: () => onView?.(skillTree),
    },
    {
      key: 'edit',
      icon: <EditOutlined />,
      label: '编辑',
      onClick: () => onEdit?.(skillTree),
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'delete',
      icon: <DeleteOutlined />,
      label: '删除',
      danger: true,
      onClick: () => onDelete?.(skillTree.id),
    },
  ]

  return (
    <Card
      hoverable
      className="!rounded-xl !shadow-sm hover:!shadow-lg transition-all duration-300 border border-gray-100"
      actions={[
        <Button
          key="view"
          type="text"
          onClick={() => onView?.(skillTree)}
          icon={<EyeOutlined />}
        >
          查看
        </Button>,
        <Button
          key="edit"
          type="text"
          onClick={() => onEdit?.(skillTree)}
          icon={<EditOutlined />}
        >
          编辑
        </Button>,
        <Dropdown key="more" menu={{ items: menuItems }} trigger={['click']}>
          <Button type="text" icon={<MoreOutlined />} />
        </Dropdown>,
      ]}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <Title level={5} className="!mb-0">
              {skillTree.name}
            </Title>
            <Badge
              count={`v${skillTree.version}`}
              style={{ backgroundColor: '#3b82f6' }}
            />
          </div>

          <Text type="secondary" className="text-sm line-clamp-2">
            {skillTree.description}
          </Text>

          <div className="mt-4 flex items-center gap-4">
            <Space size="small">
              <Badge status="processing" text={<Text type="secondary" className="text-xs">技能节点</Text>} />
              <Text strong>{skillCount}</Text>
            </Space>

            <Space size="small">
              <Badge status="success" text={<Text type="secondary" className="text-xs">学习路径</Text>} />
              <Text strong>{pathCount}</Text>
            </Space>
          </div>

          <div className="mt-3 text-xs text-gray-400">
            创建于 {new Date(skillTree.created_at).toLocaleDateString('zh-CN')}
          </div>
        </div>
      </div>
    </Card>
  )
}
