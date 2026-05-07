import React, { useEffect, useState, useCallback } from 'react'
import { Card, Form, Input, InputNumber, Switch, Button, message, Divider, Descriptions } from 'antd'
import {
  RobotOutlined,
  ApiOutlined,
  ThunderboltOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons'
import { rssApi } from '@/services/rssApi'
import type { AIConfig, SystemStatus } from '@/types/rss'

const RSSSettings: React.FC = () => {
  const [aiConfig, setAiConfig] = useState<AIConfig | null>(null)
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [form] = Form.useForm()
  const [testing, setTesting] = useState(false)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    const load = async () => {
      try {
        const [config, status] = await Promise.all([
          rssApi.ai.getConfig(),
          rssApi.system.getStatus(),
        ])
        setAiConfig(config)
        setSystemStatus(status)
        form.setFieldsValue(config)
      } catch (error) {
        message.error((error as Error).message)
      }
    }
    void load()
  }, [form])

  const handleTestConnection = useCallback(async () => {
    setTesting(true)
    try {
      const connected = await rssApi.ai.testConnection()
      if (connected) {
        message.success('AI连接测试成功')
      } else {
        message.warning('AI连接测试失败')
      }
    } catch (error) {
      message.error((error as Error).message)
    } finally {
      setTesting(false)
    }
  }, [])

  const handleSave = useCallback(async () => {
    setSaving(true)
    try {
      const values = await form.validateFields()
      const updated = await rssApi.ai.updateConfig(values)
      setAiConfig(updated)
      message.success('AI配置保存成功')
    } catch (error) {
      if (error instanceof Error) {
        message.error(error.message)
      }
    } finally {
      setSaving(false)
    }
  }, [form])

  return (
    <div style={{ display: 'flex', gap: 20 }}>
      <div style={{ flex: 1 }}>
        <Card
          title={
            <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <RobotOutlined style={{ color: 'var(--neon-blue)' }} /> AI 配置
            </span>
          }
          style={{
            background: 'rgba(17, 24, 39, 0.45)',
            border: '1px solid var(--border-glass)',
          }}
        >
          <Form form={form} layout="vertical">
            <Form.Item name="enabled" label="启用AI" valuePropName="checked">
              <Switch />
            </Form.Item>
            <Form.Item
              name="host"
              label="AI 服务地址"
              rules={[{ required: true, message: '请输入AI服务地址' }]}
            >
              <Input placeholder="如 http://localhost:11434" />
            </Form.Item>
            <Form.Item
              name="model"
              label="模型名称"
              rules={[{ required: true, message: '请输入模型名称' }]}
            >
              <Input placeholder="如 qwen2.5:7b" />
            </Form.Item>
            <Form.Item name="timeout" label="超时时间（秒）">
              <InputNumber min={10} max={300} style={{ width: '100%' }} />
            </Form.Item>
            <div style={{ display: 'flex', gap: 12 }}>
              <Button
                type="primary"
                icon={<CheckCircleOutlined />}
                loading={saving}
                onClick={() => void handleSave()}
                style={{
                  background: 'var(--gradient-primary)',
                  border: 'none',
                }}
              >
                保存配置
              </Button>
              <Button
                icon={<ThunderboltOutlined />}
                loading={testing}
                onClick={() => void handleTestConnection()}
              >
                测试连接
              </Button>
            </div>
          </Form>
        </Card>
      </div>

      <div style={{ flex: 1 }}>
        <Card
          title={
            <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <ApiOutlined style={{ color: 'var(--neon-green)' }} /> 系统状态
            </span>
          }
          style={{
            background: 'rgba(17, 24, 39, 0.45)',
            border: '1px solid var(--border-glass)',
          }}
        >
          {systemStatus && (
            <Descriptions column={1} size="small">
              <Descriptions.Item label="数据库">{systemStatus.database}</Descriptions.Item>
              <Descriptions.Item label="运行时间">
                {Math.floor(systemStatus.uptime / 3600)}小时
                {Math.floor((systemStatus.uptime % 3600) / 60)}分
              </Descriptions.Item>
              <Descriptions.Item label="版本">{systemStatus.version}</Descriptions.Item>
            </Descriptions>
          )}
        </Card>
      </div>
    </div>
  )
}

export default RSSSettings
