import React, { useEffect } from 'react'
import { Modal, Form, Input, InputNumber, Select, message } from 'antd'
import { useRSSStore } from '@/stores/rssStore'
import { rssApi } from '@/services/rssApi'
import type { Feed } from '@/types/rss'

interface AddFeedModalProps {
  open: boolean
  onClose: () => void
  onSuccess: () => void
  editFeed?: Feed | null
}

const AddFeedModal: React.FC<AddFeedModalProps> = ({ open, onClose, onSuccess, editFeed }) => {
  const [form] = Form.useForm()
  const { categories, fetchCategories } = useRSSStore()

  useEffect(() => {
    if (open) {
      void fetchCategories()
    }
  }, [open, fetchCategories])

  useEffect(() => {
    if (open && editFeed) {
      form.setFieldsValue({
        name: editFeed.name,
        url: editFeed.url,
        description: editFeed.description,
        category_id: editFeed.category_id,
        crawl_interval: editFeed.crawl_interval,
      })
    } else if (open) {
      form.resetFields()
    }
  }, [open, editFeed, form])

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      if (editFeed) {
        await rssApi.feeds.update(editFeed.id, values)
        message.success('RSS源更新成功')
      } else {
        await rssApi.feeds.create(values)
        message.success('RSS源添加成功')
      }
      onSuccess()
    } catch (error) {
      if (error instanceof Error) {
        message.error(error.message)
      }
    }
  }

  return (
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
          {editFeed ? '编辑RSS源' : '添加RSS源'}
        </span>
      }
      open={open}
      onCancel={onClose}
      onOk={() => void handleSubmit()}
      okText={editFeed ? '保存' : '添加'}
      cancelText="取消"
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
        style={{ marginTop: 16 }}
        initialValues={{ crawl_interval: 30 }}
      >
        <Form.Item
          name="name"
          label="名称"
          rules={[{ required: true, message: '请输入RSS源名称' }]}
        >
          <Input placeholder="请输入RSS源名称" />
        </Form.Item>

        <Form.Item
          name="url"
          label="URL"
          rules={[
            { required: true, message: '请输入RSS源URL' },
            { type: 'url', message: '请输入有效的URL' },
          ]}
        >
          <Input placeholder="请输入RSS源URL" />
        </Form.Item>

        <Form.Item name="description" label="描述">
          <Input.TextArea placeholder="请输入描述（可选）" rows={2} />
        </Form.Item>

        <Form.Item name="category_id" label="分类">
          <Select
            placeholder="选择分类（可选）"
            allowClear
            options={categories.map((c) => ({ label: c.name, value: c.id }))}
          />
        </Form.Item>

        <Form.Item
          name="crawl_interval"
          label="抓取间隔（分钟）"
          rules={[{ required: true, message: '请输入抓取间隔' }]}
        >
          <InputNumber min={5} max={1440} style={{ width: '100%' }} />
        </Form.Item>
      </Form>
    </Modal>
  )
}

export default AddFeedModal
