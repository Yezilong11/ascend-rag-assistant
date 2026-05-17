import React, { useState, useCallback } from 'react'
import { Button, Modal, Form, Input, message, Empty, Tag } from 'antd'
import { PlusOutlined, TagsOutlined } from '@ant-design/icons'
import { useRSSStore } from '@/stores/rssStore'
import { rssApi } from '@/services/rssApi'

const RSSTags: React.FC = () => {
  const { tags, fetchTags } = useRSSStore()
  const [modalOpen, setModalOpen] = useState(false)
  const [form] = Form.useForm()

  const handleAdd = useCallback(() => {
    form.resetFields()
    setModalOpen(true)
  }, [form])

  const handleDelete = useCallback(
    async (id: number, name: string) => {
      Modal.confirm({
        title: '确认删除',
        content: `确定要删除标签「${name}」吗？`,
        okText: '删除',
        cancelText: '取消',
        okButtonProps: { danger: true },
        onOk: async () => {
          try {
            await rssApi.tags.delete(id)
            message.success('删除成功')
            await fetchTags()
          } catch (error) {
            message.error((error as Error).message)
          }
        },
      })
    },
    [fetchTags],
  )

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      await rssApi.tags.create(values)
      message.success('标签创建成功')
      setModalOpen(false)
      await fetchTags()
    } catch (error) {
      if (error instanceof Error) {
        message.error(error.message)
      }
    }
  }

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
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
          <TagsOutlined /> 标签管理
        </h3>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleAdd}
          style={{
            background: 'var(--gradient-primary)',
            border: 'none',
            boxShadow: '0 0 10px rgba(0, 212, 255, 0.2)',
          }}
        >
          添加标签
        </Button>
      </div>

      {tags.length === 0 ? (
        <Empty description="暂无标签" />
      ) : (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          {tags.map((tag) => (
            <Tag
              key={tag.id}
              color={tag.color}
              closable
              onClose={() => void handleDelete(tag.id, tag.name)}
              style={{ fontSize: 13, padding: '4px 10px' }}
            >
              {tag.name}
            </Tag>
          ))}
        </div>
      )}

      <Modal
        title="添加标签"
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => void handleSubmit()}
        okText="添加"
        cancelText="取消"
        destroyOnClose
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item
            name="name"
            label="名称"
            rules={[{ required: true, message: '请输入标签名称' }]}
          >
            <Input placeholder="请输入标签名称" />
          </Form.Item>
          <Form.Item name="color" label="颜色">
            <Input placeholder="颜色值（可选，如 #1890ff）" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default RSSTags
