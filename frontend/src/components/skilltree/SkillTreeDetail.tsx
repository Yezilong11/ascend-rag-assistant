import React, { useState } from 'react'
import { Card, Descriptions, Button, Tag, Spin, Typography, Tabs } from 'antd'
import { DeleteOutlined, PlusOutlined, ApartmentOutlined, RocketOutlined } from '@ant-design/icons'
import type { SkillTree } from '@/types/skillTree'
import SkillGraph from './SkillGraph'
import SkillNodeCard from './SkillNodeCard'
import LearningPathList from './LearningPathList'
import AddSkillForm from './AddSkillForm'
import RelationForm from './RelationForm'
import type { AddSkillRequest, AddRelationRequest, SkillNode } from '@/types/skillTree'

interface SkillTreeDetailProps {
  skillTree: SkillTree
  isLoading: boolean
  onAddSkill: (request: AddSkillRequest) => Promise<void>
  onAddRelation: (request: AddRelationRequest) => Promise<void>
  onDelete: () => void
  onGeneratePaths: () => void
  onNodeClick?: (node: SkillNode) => void
}

const SkillTreeDetail: React.FC<SkillTreeDetailProps> = ({
  skillTree,
  isLoading,
  onAddSkill,
  onAddRelation,
  onDelete,
  onGeneratePaths,
  onNodeClick,
}) => {
  const [addSkillOpen, setAddSkillOpen] = useState(false)
  const [relationOpen, setRelationOpen] = useState(false)

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: 40 }}>
        <Spin />
      </div>
    )
  }

  const skillNodeList = Object.values(skillTree.skill_nodes)

  const tabItems = [
    {
      key: 'graph',
      label: (
        <span>
          <ApartmentOutlined /> 可视化
        </span>
      ),
      children: <SkillGraph skillTree={skillTree} onNodeClick={onNodeClick} />,
    },
    {
      key: 'skills',
      label: `技能列表 (${skillNodeList.length})`,
      children: (
        <div>
          {skillNodeList.map((node) => (
            <SkillNodeCard key={node.id} node={node} onClick={onNodeClick} />
          ))}
        </div>
      ),
    },
    {
      key: 'paths',
      label: '学习路径',
      children: (
        <LearningPathList paths={skillTree.learning_paths} skillNodes={skillTree.skill_nodes} />
      ),
    },
  ]

  return (
    <div>
      <Card
        title={
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography.Title level={4} style={{ margin: 0 }}>
              {skillTree.name}
            </Typography.Title>
            <div style={{ display: 'flex', gap: 8 }}>
              <Button icon={<PlusOutlined />} onClick={() => setAddSkillOpen(true)}>
                添加技能
              </Button>
              <Button icon={<ApartmentOutlined />} onClick={() => setRelationOpen(true)}>
                建立关系
              </Button>
              <Button icon={<RocketOutlined />} onClick={onGeneratePaths}>
                生成路径
              </Button>
              <Button icon={<DeleteOutlined />} danger onClick={onDelete}>
                删除
              </Button>
            </div>
          </div>
        }
      >
        <Descriptions column={3} size="small" style={{ marginBottom: 16 }}>
          <Descriptions.Item label="描述">{skillTree.description}</Descriptions.Item>
          <Descriptions.Item label="版本">{skillTree.version}</Descriptions.Item>
          <Descriptions.Item label="完成率">
            <Tag color="blue">{skillTree.completion_rate.toFixed(1)}%</Tag>
          </Descriptions.Item>
        </Descriptions>
        <Tabs items={tabItems} />
      </Card>

      <AddSkillForm
        open={addSkillOpen}
        onClose={() => setAddSkillOpen(false)}
        onSubmit={onAddSkill}
      />
      <RelationForm
        open={relationOpen}
        onClose={() => setRelationOpen(false)}
        onSubmit={onAddRelation}
        skillNodes={skillNodeList}
      />
    </div>
  )
}

export default SkillTreeDetail
