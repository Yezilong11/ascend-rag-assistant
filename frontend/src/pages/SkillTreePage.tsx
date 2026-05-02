import React, { useState } from 'react'
import { ApartmentOutlined, PlusOutlined } from '@ant-design/icons'
import { useSkillTreeStore } from '@/stores/skillTreeStore'
import SkillTreeList from '@/components/skilltree/SkillTreeList'
import SkillGraph from '@/components/skilltree/SkillGraph'
import SkillNodeCard from '@/components/skilltree/SkillNodeCard'
import type { SkillNode } from '@/types/skillTree'

const SkillTreePage: React.FC = () => {
  const skillTreeList = useSkillTreeStore((s) => s.skillTreeList)
  const currentSkillTree = useSkillTreeStore((s) => s.currentSkillTree)
  const isLoading = useSkillTreeStore((s) => s.isLoading)
  const setCurrentSkillTree = useSkillTreeStore((s) => s.setCurrentSkillTree)
  const [selectedNode, setSelectedNode] = useState<SkillNode | null>(null)

  const handleSelect = (_id: string) => {
    setCurrentSkillTree(null)
    setSelectedNode(null)
  }

  const hasNodes = currentSkillTree && Object.keys(currentSkillTree.skill_nodes).length > 0

  return (
    <div style={{ display: 'flex', gap: 20, height: 'calc(100vh - 112px)' }}>
      <div
        style={{
          width: 300,
          flexShrink: 0,
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: 16,
          }}
        >
          <h3
            style={{
              margin: 0,
              fontSize: 16,
              fontWeight: 700,
              background: 'var(--gradient-primary)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              display: 'flex',
              alignItems: 'center',
              gap: 8,
            }}
          >
            <ApartmentOutlined /> 技能树列表
          </h3>
          <button
            style={{
              padding: '4px 12px',
              borderRadius: 'var(--radius-sm)',
              background: 'var(--gradient-primary)',
              border: 'none',
              color: '#fff',
              fontSize: 12,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 4,
              boxShadow: '0 0 10px rgba(0, 212, 255, 0.2)',
            }}
          >
            <PlusOutlined /> 新建
          </button>
        </div>
        <div className="scrollbar-custom" style={{ flex: 1, overflowY: 'auto' }}>
          <SkillTreeList
            skillTreeList={skillTreeList}
            isLoading={isLoading}
            onSelect={handleSelect}
            selectedId={currentSkillTree?.id}
          />
        </div>
      </div>

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 16 }}>
        {currentSkillTree ? (
          <>
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
                  {currentSkillTree.name}
                </h3>
                <p
                  style={{
                    margin: 0,
                    color: 'var(--text-tertiary)',
                    fontSize: 13,
                  }}
                >
                  {currentSkillTree.description}
                </p>
              </div>
              <div style={{ display: 'flex', gap: 8 }}>
                <span className="neon-tag">
                  {Object.keys(currentSkillTree.skill_nodes).length} 个节点
                </span>
                <span className="neon-tag-green neon-tag">
                  完成率 {currentSkillTree.completion_rate.toFixed(1)}%
                </span>
              </div>
            </div>
            {hasNodes ? (
              <>
                <SkillGraph skillTree={currentSkillTree} onNodeClick={setSelectedNode} />
                {selectedNode && (
                  <div className="animate-slide-up">
                    <SkillNodeCard node={selectedNode} />
                  </div>
                )}
              </>
            ) : (
              <div
                className="glass-card-static"
                style={{
                  flex: 1,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--text-tertiary)',
                }}
              >
                <ApartmentOutlined
                  style={{
                    fontSize: 48,
                    marginBottom: 16,
                    color: 'var(--neon-blue)',
                    opacity: 0.3,
                  }}
                />
                <p style={{ fontSize: 14, marginBottom: 8 }}>技能树暂无节点数据</p>
                <p style={{ fontSize: 12 }}>请通过API添加技能节点后查看可视化图</p>
              </div>
            )}
          </>
        ) : (
          <div
            style={{
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--text-tertiary)',
            }}
          >
            <ApartmentOutlined
              style={{
                fontSize: 48,
                marginBottom: 16,
                color: 'var(--neon-blue)',
                opacity: 0.3,
              }}
            />
            <p style={{ fontSize: 14 }}>请从左侧选择一个技能树查看</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default SkillTreePage
