import React, { useState } from 'react'
import { Form, Select, Button, Modal } from 'antd'
import type { AddRelationRequest, RelationType } from '@/types/skillTree'
import type { SkillNode } from '@/types/skillTree'

interface RelationFormProps {
  open: boolean
  onClose: () => void
  onSubmit: (values: AddRelationRequest) => Promise<void>
  skillNodes: SkillNode[]
}

const relationTypeOptions: { value: RelationType; label: string }[] = [
  { value: 'prerequisite', label: '前置' },
  { value: 'related', label: '相关' },
  { value: 'advanced', label: '进阶' },
]

const RelationForm: React.FC<RelationFormProps> = ({ open, onClose, onSubmit, skillNodes }) => {
  const [form] = Form.useForm<AddRelationRequest>()
  const [loading, setLoading] = useState(false)

  const skillOptions = skillNodes.map((node) => ({
    value: node.id,
    label: node.name,
  }))

  const handleFinish = async (values: AddRelationRequest) => {
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
    <Modal title="建立技能关系" open={open} onCancel={onClose} footer={null} destroyOnClose>
      <Form form={form} layout="vertical" onFinish={handleFinish}>
        <Form.Item
          name="source_skill_id"
          label="源技能（前置）"
          rules={[{ required: true, message: '请选择源技能' }]}
        >
          <Select options={skillOptions} placeholder="请选择源技能" showSearch />
        </Form.Item>
        <Form.Item
          name="target_skill_id"
          label="目标技能（后续）"
          rules={[{ required: true, message: '请选择目标技能' }]}
        >
          <Select options={skillOptions} placeholder="请选择目标技能" showSearch />
        </Form.Item>
        <Form.Item
          name="relation_type"
          label="关系类型"
          rules={[{ required: true, message: '请选择关系类型' }]}
        >
          <Select options={relationTypeOptions} placeholder="请选择关系类型" />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block>
            建立关系
          </Button>
        </Form.Item>
      </Form>
    </Modal>
  )
}

export default RelationForm
