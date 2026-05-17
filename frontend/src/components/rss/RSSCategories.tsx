import React, { useState, useCallback } from 'react'
import { Card, Button, List, Modal, Form, Input, message, Empty, Tag } from 'antd'
import {
  PlusOutlined,
  DeleteOutlined,
  EditOutlined,
  FolderOutlined,
} from '@ant-design/icons'
import { useRSSStore } from '@/stores/rssStore'
import { rssApi } from '@/services/rssApi'
import type { Category } from '@/types/rss'

const RSSCategories: React.FC = () => {
  const { categories, fetchCategories } = useRSSStore()
  const [modalOpen, setModalOpen] = useState(false)
  const [editItem, setEditItem] = useState<Category | null>(null)
  const [form] = Form.useForm()

  const handleAdd = useCallback(() => {
    setEditItem(null)
    form.resetFields()
    setModalOpen(true)
  }, [form])

  const handleEdit = useCallback(
    (item: Category) => {
      setEditItem(item)
      form.setFieldsValue({ name: item.name, icon: item.icon, sort_order: item.sort_order })
      setModalOpen(true)
    },
    [form],
  )

  const handleDelete = useCallback(
    async (id: number, name: string) => {
      Modal.confirm({
        title: '确认删除',
        content: `确定要删除分类「${name}」吗？`,
        okText: '删除',
        cancelText: '取消',
        okButtonProps: { danger: true },
        onOk: async () => {
          try {
            await rssApi.categories.delete(id)
            message.success('删除成功')
            await fetchCategories()
          } catch (error) {
            message.error((error as Error).message)
          }
        },
      })
    },
    [fetchCategories],
  )

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      if (editItem) {
        await rssApi.categories.update(editItem.id, values)
        message.success('更新成功')
      } else {
        await rssApi.categories.create(values)
        message.success('创建成功')
      }
      setModalOpen(false)
      await fetchCategories()
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
          <FolderOutlined /> 分类管理
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
          添加分类
        </Button>
      </div>

      {categories.length === 0 ? (
        <Empty description="暂无分类" />
      ) : (
        <List
          grid={{ gutter: 16, column: 3 }}
          dataSource={categories}
          renderItem={(item) => (
            <List.Item>
              <Card
                size="small"
                style={{
                  background: 'rgba(17, 24, 39, 0.45)',
                  border: '1px solid var(--border-glass)',
                }}
                actions={[
                  <EditOutlined key="edit" onClick={() => handleEdit(item)} />,
                  <DeleteOutlined
                    key="delete"
                    onClick={() => void handleDelete(item.id, item.name)}
                  />,
                ]}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  {item.icon && <span>{item.icon}</span>}
                  <span style={{ fontWeight: 600 }}>{item.name}</span>
                  <Tag style={{ marginLeft: 'auto' }}>排序: {item.sort_order}</Tag>
                </div>
              </Card>
            </List.Item>
          )}
        />
      )}

      <Modal
        title={editItem ? '编辑分类' : '添加分类'}
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={() => void handleSubmit()}
        okText={editItem ? '保存' : '添加'}
        cancelText="取消"
        destroyOnClose
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item
            name="name"
            label="名称"
            rules={[{ required: true, message: '请输入分类名称' }]}
          >
            <Input placeholder="请输入分类名称" />
          </Form.Item>
          <Form.Item name="icon" label="图标">
            <Input placeholder="图标（可选）" />
          </Form.Item>
          <Form.Item name="sort_order" label="排序" initialValue={0}>
            <Input type="number" placeholder="排序值" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default RSSCategories
