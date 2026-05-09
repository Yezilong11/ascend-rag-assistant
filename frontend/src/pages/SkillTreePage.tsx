import React, { useEffect, useState } from 'react'
import { ApartmentOutlined, PlusOutlined } from '@ant-design/icons'
import { message, Modal } from 'antd'
import { useSkillTree } from '@/hooks/useSkillTree'
import SkillTreeList from '@/components/skilltree/SkillTreeList'
import SkillTreeDetail from '@/components/skilltree/SkillTreeDetail'
import type { AddSkillRequest, AddRelationRequest } from '@/types/skillTree'

const SkillTreePage: React.FC = () => {
  const {
    skillTreeList,
    currentSkillTree,
    isLoading,
    fetchList,
    fetchDetail,
    create,
    remove,
    addSkill,
    addRelation,
    generatePaths,
    updateCompletion,
    setCurrentSkillTree,
  } = useSkillTree()

  const [createModalOpen, setCreateModalOpen] = useState(false)
  const [createName, setCreateName] = useState('')
  const [createDesc, setCreateDesc] = useState('')

  useEffect(() => {
    void fetchList()
  }, [fetchList])

  const handleSelect = (id: string) => {
    void fetchDetail(id)
  }

  const handleCreate = async () => {
    if (!createName.trim() || !createDesc.trim()) {
      message.warning('请填写名称和描述')
      return
    }
    try {
      await create({ name: createName.trim(), description: createDesc.trim() })
      setCreateModalOpen(false)
      setCreateName('')
      setCreateDesc('')
      message.success('技能树创建成功')
    } catch (error) {
      message.error((error as Error).message)
    }
  }

  const handleDelete = async () => {
    if (!currentSkillTree) return
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除技能树「${currentSkillTree.name}」吗？此操作不可撤销。`,
      okText: '删除',
      cancelText: '取消',
      okButtonProps: { danger: true },
      onOk: async () => {
        try {
          await remove(currentSkillTree.id)
          setCurrentSkillTree(null)
          message.success('技能树删除成功')
        } catch (error) {
          message.error((error as Error).message)
        }
      },
    })
  }

  const handleAddSkill = async (request: AddSkillRequest) => {
    if (!currentSkillTree) return
    try {
      await addSkill(currentSkillTree.id, request)
      message.success('技能添加成功')
    } catch (error) {
      message.error((error as Error).message)
      throw error
    }
  }

  const handleAddRelation = async (request: AddRelationRequest) => {
    if (!currentSkillTree) return
    try {
      await addRelation(currentSkillTree.id, request)
      message.success('技能关系建立成功')
    } catch (error) {
      message.error((error as Error).message)
      throw error
    }
  }

  const handleGeneratePaths = async () => {
    if (!currentSkillTree) return
    try {
      await generatePaths(currentSkillTree.id)
      message.success('学习路径生成成功')
    } catch (error) {
      message.error((error as Error).message)
    }
  }

  const handleUpdateCompletion = async (skillId: string, rate: number) => {
    if (!currentSkillTree) return
    try {
      await updateCompletion(currentSkillTree.id, skillId, rate)
    } catch (error) {
      message.error((error as Error).message)
    }
  }

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
            onClick={() => setCreateModalOpen(true)}
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
          <SkillTreeDetail
            skillTree={currentSkillTree}
            isLoading={isLoading}
            onAddSkill={handleAddSkill}
            onAddRelation={handleAddRelation}
            onDelete={handleDelete}
            onGeneratePaths={handleGeneratePaths}
            onUpdateCompletion={handleUpdateCompletion}
          />
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

      <Modal
        title={
          <span
            style={{
              background: 'var(--gradient-primary)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              fontWeight: 700,
            }}
          >
            创建技能树
          </span>
        }
        open={createModalOpen}
        onCancel={() => setCreateModalOpen(false)}
        onOk={handleCreate}
        okText="创建"
        cancelText="取消"
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginTop: 16 }}>
          <div>
            <div style={{ color: 'var(--text-secondary)', fontSize: 12, marginBottom: 6 }}>
              技能树名称
            </div>
            <input
              value={createName}
              onChange={(e) => setCreateName(e.target.value)}
              placeholder="请输入技能树名称"
              style={{
                width: '100%',
                padding: '8px 12px',
                borderRadius: 'var(--radius-sm)',
                background: 'var(--bg-glass)',
                border: '1px solid var(--border-glass)',
                color: 'var(--text-primary)',
                fontSize: 14,
                outline: 'none',
              }}
            />
          </div>
          <div>
            <div style={{ color: 'var(--text-secondary)', fontSize: 12, marginBottom: 6 }}>
              技能树描述
            </div>
            <textarea
              value={createDesc}
              onChange={(e) => setCreateDesc(e.target.value)}
              placeholder="请输入技能树描述"
              rows={3}
              style={{
                width: '100%',
                padding: '8px 12px',
                borderRadius: 'var(--radius-sm)',
                background: 'var(--bg-glass)',
                border: '1px solid var(--border-glass)',
                color: 'var(--text-primary)',
                fontSize: 14,
                outline: 'none',
                resize: 'none',
                fontFamily: 'inherit',
              }}
            />
          </div>
        </div>
      </Modal>
    </div>
  )
}

export default SkillTreePage
