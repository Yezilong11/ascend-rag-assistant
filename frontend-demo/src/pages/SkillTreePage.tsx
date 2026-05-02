import { useEffect, useState } from 'react'
import { Card, Row, Col, Button, Empty, Modal, Form, Input, Typography, message, Spin, Tabs, Tag, Space } from 'antd'
import { PlusOutlined, ReloadOutlined } from '@ant-design/icons'
import { SkillTreeCard } from '../components/skilltree/SkillTreeCard'
import { SkillNodeCard } from '../components/skilltree/SkillNodeCard'
import { useSkillTreeStore } from '../stores/skillTreeStore'
import type { SkillTree } from '../types'

const { Text } = Typography
const { TextArea } = Input

export function SkillTreePage() {
  const {
    skillTrees,
    selectedSkillTree,
    isLoading,
    fetchSkillTrees,
    fetchSkillTreeDetail,
    createSkillTree,
    deleteSkillTree,
    setSelectedSkillTree,
  } = useSkillTreeStore()

  const [createModalOpen, setCreateModalOpen] = useState(false)
  const [form] = Form.useForm()

  useEffect(() => {
    fetchSkillTrees()
  }, [])

  const handleCreateSkillTree = async (values: { name: string; description: string }) => {
    const success = await createSkillTree(values.name, values.description)
    if (success) {
      message.success('技能树创建成功')
      setCreateModalOpen(false)
      form.resetFields()
    } else {
      message.error('创建失败，请重试')
    }
  }

  const handleViewSkillTree = (skillTree: SkillTree) => {
    setSelectedSkillTree(skillTree)
    fetchSkillTreeDetail(skillTree.id)
  }

  const handleDeleteSkillTree = async (skillTreeId: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个技能树吗？此操作不可恢复。',
      okText: '确认',
      cancelText: '取消',
      okButtonProps: { danger: true },
      onOk: async () => {
        const success = await deleteSkillTree(skillTreeId)
        if (success) {
          message.success('删除成功')
        }
      },
    })
  }

  if (isLoading && skillTrees.length === 0) {
    return (
      <div className="flex items-center justify-center h-96">
        <Spin size="large" />
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-800">🌳 技能树管理</h2>
        <Space>
          <Button
            icon={<ReloadOutlined />}
            onClick={() => fetchSkillTrees()}
          >
            刷新
          </Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setCreateModalOpen(true)}
          >
            创建技能树
          </Button>
        </Space>
      </div>

      {selectedSkillTree ? (
        <Card className="!rounded-xl !border-gray-200">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold">{selectedSkillTree.name}</h3>
              <p className="text-sm text-gray-500 mt-1">{selectedSkillTree.description}</p>
              <div className="mt-2">
                <Tag color="blue">v{selectedSkillTree.version}</Tag>
                <Tag color="green">{Object.keys(selectedSkillTree.skill_nodes).length} 技能</Tag>
                <Tag color="orange">{Object.keys(selectedSkillTree.learning_paths).length} 路径</Tag>
              </div>
            </div>
            <Button onClick={() => setSelectedSkillTree(null)}>返回列表</Button>
          </div>

          <Tabs
            items={[
              {
                key: 'skills',
                label: '技能节点',
                children: (
                  <Row gutter={[16, 16]}>
                    {Object.values(selectedSkillTree.skill_nodes).map((skill) => (
                      <Col key={skill.id} xs={24} sm={12} lg={8}>
                        <SkillNodeCard skill={skill} />
                      </Col>
                    ))}
                    {Object.keys(selectedSkillTree.skill_nodes).length === 0 && (
                      <Col span={24}>
                        <Empty description="暂无技能节点，请添加" />
                      </Col>
                    )}
                  </Row>
                ),
              },
              {
                key: 'paths',
                label: '学习路径',
                children: (
                  <div className="space-y-4">
                    {Object.values(selectedSkillTree.learning_paths).map((path) => (
                      <Card key={path.path_id} size="small" className="!rounded-lg">
                        <div className="flex items-center justify-between">
                          <div>
                            <Text strong>路径 {path.path_id.substring(0, 8)}</Text>
                            <p className="text-sm text-gray-500">
                              预估时间: {path.estimated_time}h | 难度: {path.difficulty}
                            </p>
                          </div>
                          <Tag color={
                            path.difficulty === 'beginner' ? 'green' :
                            path.difficulty === 'intermediate' ? 'blue' :
                            path.difficulty === 'advanced' ? 'orange' : 'red'
                          }>
                            {path.difficulty}
                          </Tag>
                        </div>
                        <div className="mt-3 flex flex-wrap gap-2">
                          {path.skill_ids.map((skillId) => {
                            const skill = selectedSkillTree.skill_nodes[skillId]
                            return skill ? (
                              <Tag key={skillId}>{skill.name}</Tag>
                            ) : null
                          })}
                        </div>
                      </Card>
                    ))}
                    {Object.keys(selectedSkillTree.learning_paths).length === 0 && (
                      <Empty description="暂无学习路径，请生成" />
                    )}
                  </div>
                ),
              },
            ]}
          />
        </Card>
      ) : (
        <>
          {skillTrees.length === 0 ? (
            <Card className="!rounded-xl !border-gray-200">
              <Empty
                description={
                  <div>
                    <p className="text-gray-500 mb-4">还没有创建任何技能树</p>
                    <Button
                      type="primary"
                      icon={<PlusOutlined />}
                      onClick={() => setCreateModalOpen(true)}
                    >
                      创建第一个技能树
                    </Button>
                  </div>
                }
              />
            </Card>
          ) : (
            <Row gutter={[16, 16]}>
              {skillTrees.map((skillTree) => (
                <Col key={skillTree.id} xs={24} sm={12} lg={8}>
                  <SkillTreeCard
                    skillTree={skillTree}
                    onView={handleViewSkillTree}
                    onDelete={handleDeleteSkillTree}
                  />
                </Col>
              ))}
            </Row>
          )}
        </>
      )}

      <Modal
        title="创建技能树"
        open={createModalOpen}
        onCancel={() => setCreateModalOpen(false)}
        footer={null}
        className="!rounded-xl"
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateSkillTree}
          className="mt-4"
        >
          <Form.Item
            name="name"
            label="技能树名称"
            rules={[{ required: true, message: '请输入技能树名称' }]}
          >
            <Input placeholder="请输入技能树名称" />
          </Form.Item>

          <Form.Item
            name="description"
            label="技能树描述"
            rules={[{ required: true, message: '请输入技能树描述' }]}
          >
            <TextArea rows={4} placeholder="请输入技能树描述" />
          </Form.Item>

          <Form.Item className="!mb-0">
            <Space className="w-full justify-end">
              <Button onClick={() => setCreateModalOpen(false)}>取消</Button>
              <Button type="primary" htmlType="submit" loading={isLoading}>
                创建
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
