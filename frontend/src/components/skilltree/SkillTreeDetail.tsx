import React, { useState } from 'react'
import {
  ApartmentOutlined,
  PlusOutlined,
  DeleteOutlined,
  RocketOutlined,
  LinkOutlined,
} from '@ant-design/icons'
import type { SkillTree, AddSkillRequest, AddRelationRequest, SkillNode } from '@/types/skillTree'
import SkillGraph from './SkillGraph'
import SkillNodeCard from './SkillNodeCard'
import LearningPathList from './LearningPathList'
import AddSkillForm from './AddSkillForm'
import RelationForm from './RelationForm'

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
  const [activeTab, setActiveTab] = useState<'graph' | 'skills' | 'paths'>('graph')

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

  const skillNodeList = Object.values(skillTree.skill_nodes)

  const tabs = [
    { key: 'graph' as const, label: '可视化', icon: <ApartmentOutlined /> },
    { key: 'skills' as const, label: `技能 (${skillNodeList.length})`, icon: <PlusOutlined /> },
    { key: 'paths' as const, label: '学习路径', icon: <RocketOutlined /> },
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div
        className="glass-card-static"
        style={{
          padding: '16px 20px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <div>
          <h3
            style={{
              margin: '0 0 4px',
              fontSize: 18,
              fontWeight: 700,
              color: 'var(--text-primary)',
            }}
          >
            {skillTree.name}
          </h3>
          <p style={{ margin: 0, color: 'var(--text-tertiary)', fontSize: 13 }}>
            {skillTree.description}
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <span className="neon-tag">{Object.keys(skillTree.skill_nodes).length} 个节点</span>
          <span className="neon-tag-green neon-tag">
            完成率 {skillTree.completion_rate.toFixed(1)}%
          </span>
        </div>
      </div>

      <div
        style={{
          display: 'flex',
          gap: 8,
          alignItems: 'center',
        }}
      >
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            style={{
              padding: '6px 16px',
              borderRadius: 'var(--radius-sm)',
              background: activeTab === tab.key ? 'rgba(0, 212, 255, 0.1)' : 'var(--bg-glass)',
              border:
                activeTab === tab.key
                  ? '1px solid rgba(0, 212, 255, 0.3)'
                  : '1px solid var(--border-glass)',
              color: activeTab === tab.key ? 'var(--neon-blue)' : 'var(--text-secondary)',
              cursor: 'pointer',
              fontSize: 13,
              fontWeight: activeTab === tab.key ? 600 : 400,
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              transition: 'all var(--transition-normal)',
            }}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
        <div style={{ flex: 1 }} />
        <button
          onClick={() => setAddSkillOpen(true)}
          className="neon-button"
          style={{
            padding: '6px 14px',
            fontSize: 12,
            display: 'flex',
            alignItems: 'center',
            gap: 4,
            cursor: 'pointer',
          }}
        >
          <PlusOutlined /> 添加技能
        </button>
        <button
          onClick={() => setRelationOpen(true)}
          className="neon-button"
          style={{
            padding: '6px 14px',
            fontSize: 12,
            display: 'flex',
            alignItems: 'center',
            gap: 4,
            cursor: 'pointer',
          }}
        >
          <LinkOutlined /> 建立关系
        </button>
        <button
          onClick={() => void onGeneratePaths()}
          className="neon-button"
          style={{
            padding: '6px 14px',
            fontSize: 12,
            display: 'flex',
            alignItems: 'center',
            gap: 4,
            cursor: 'pointer',
          }}
        >
          <RocketOutlined /> 生成路径
        </button>
        <button
          onClick={onDelete}
          style={{
            padding: '6px 14px',
            borderRadius: 'var(--radius-sm)',
            background: 'rgba(255, 51, 102, 0.08)',
            border: '1px solid rgba(255, 51, 102, 0.2)',
            color: 'var(--neon-red)',
            cursor: 'pointer',
            fontSize: 12,
            display: 'flex',
            alignItems: 'center',
            gap: 4,
            transition: 'all var(--transition-normal)',
          }}
        >
          <DeleteOutlined /> 删除
        </button>
      </div>

      <div style={{ flex: 1 }}>
        {activeTab === 'graph' && <SkillGraph skillTree={skillTree} onNodeClick={onNodeClick} />}
        {activeTab === 'skills' && (
          <div
            className="scrollbar-custom"
            style={{ maxHeight: 'calc(100vh - 280px)', overflowY: 'auto' }}
          >
            {skillNodeList.length > 0 ? (
              skillNodeList.map((node) => (
                <SkillNodeCard key={node.id} node={node} onClick={onNodeClick} />
              ))
            ) : (
              <div style={{ textAlign: 'center', padding: 40, color: 'var(--text-tertiary)' }}>
                暂无技能节点，请添加
              </div>
            )}
          </div>
        )}
        {activeTab === 'paths' && (
          <div className="glass-card-static" style={{ padding: 16 }}>
            <LearningPathList paths={skillTree.learning_paths} skillNodes={skillTree.skill_nodes} />
          </div>
        )}
      </div>

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
