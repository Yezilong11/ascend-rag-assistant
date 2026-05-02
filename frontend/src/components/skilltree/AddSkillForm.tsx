import React, { useState } from 'react'
import { Form, Input, Select, InputNumber, Button, Modal } from 'antd'
import type { AddSkillRequest, SkillLevel, SkillType } from '@/types/skillTree'

interface AddSkillFormProps {
  open: boolean
  onClose: () => void
  onSubmit: (values: AddSkillRequest) => Promise<void>
}

const levelOptions: { value: SkillLevel; label: string }[] = [
  { value: 'beginner', label: '入门' },
  { value: 'intermediate', label: '进阶' },
  { value: 'advanced', label: '高级' },
  { value: 'expert', label: '专家' },
]

const typeOptions: { value: SkillType; label: string }[] = [
  { value: 'technical', label: '技术' },
  { value: 'theoretical', label: '理论' },
  { value: 'practical', label: '实践' },
  { value: 'competition', label: '竞赛' },
]

const AddSkillForm: React.FC<AddSkillFormProps> = ({ open, onClose, onSubmit }) => {
  const [form] = Form.useForm<AddSkillRequest>()
  const [loading, setLoading] = useState(false)

  const handleFinish = async (values: AddSkillRequest) => {
    setLoading(true)
    try {
      await onSubmit(values)
      form.resetFields()
      onClose()
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal title="添加技能" open={open} onCancel={onClose} footer={null} destroyOnClose>
      <Form
        form={form}
        layout="vertical"
        onFinish={handleFinish}
        initialValues={{ learning_time: 0 }}
      >
        <Form.Item
          name="name"
          label="技能名称"
          rules={[{ required: true, message: '请输入技能名称' }]}
        >
          <Input placeholder="请输入技能名称" />
        </Form.Item>
        <Form.Item
          name="description"
          label="技能描述"
          rules={[{ required: true, message: '请输入技能描述' }]}
        >
          <Input.TextArea rows={3} placeholder="请输入技能描述" />
        </Form.Item>
        <Form.Item
          name="level"
          label="难度等级"
          rules={[{ required: true, message: '请选择难度等级' }]}
        >
          <Select options={levelOptions} placeholder="请选择难度等级" />
        </Form.Item>
        <Form.Item
          name="skill_type"
          label="技能类型"
          rules={[{ required: true, message: '请选择技能类型' }]}
        >
          <Select options={typeOptions} placeholder="请选择技能类型" />
        </Form.Item>
        <Form.Item name="learning_time" label="预估学习时间（小时）">
          <InputNumber min={0} style={{ width: '100%' }} />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block>
            添加
          </Button>
        </Form.Item>
      </Form>
    </Modal>
  )
}

export default AddSkillForm
