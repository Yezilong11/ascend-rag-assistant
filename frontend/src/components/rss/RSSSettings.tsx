import React, { useEffect, useState, useCallback } from 'react'
import { Card, Button, message, Descriptions, Tag, Alert, Space } from 'antd'
import {
  RobotOutlined,
  ApiOutlined,
  ThunderboltOutlined,
  ExclamationCircleOutlined,
  LinkOutlined,
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { rssApi } from '@/services/rssApi'
import type { AIConfig, SystemStatus } from '@/types/rss'

const RSSSettings: React.FC = () => {
  const [aiConfig, setAiConfig] = useState<AIConfig | null>(null)
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [testing, setTesting] = useState(false)

  const navigate = useNavigate()

  useEffect(() => {
    const load = async () => {
      try {
        const [config, status] = await Promise.all([
          rssApi.ai.getConfig(),
          rssApi.system.getStatus(),
        ])
        setAiConfig(config)
        setSystemStatus(status)
      } catch (error) {
        message.error((error as Error).message)
      }
    }
    void load()
  }, [])

  const handleTestAvailability = useCallback(async () => {
    setTesting(true)
    try {
      const available = await rssApi.ai.testConnection()
      if (available) {
        message.success('本地模型可用')
      } else {
        message.warning('本地模型不可用，请先在智能问答页面加载模型')
      }
    } catch (error) {
      message.error((error as Error).message)
    } finally {
      setTesting(false)
    }
  }, [])

  return (
    <div style={{ display: 'flex', gap: 20 }}>
      <div style={{ flex: 1 }}>
        <Card
          title={
            <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <RobotOutlined style={{ color: 'var(--neon-blue)' }} /> AI 分析配置
            </span>
          }
          style={{
            background: 'rgba(17, 24, 39, 0.45)',
            border: '1px solid var(--border-glass)',
          }}
        >
          {aiConfig && (
            <>
              <Descriptions column={1} size="small" bordered>
                <Descriptions.Item label="当前模型">
                  {aiConfig.model_name || '-'}
                </Descriptions.Item>
                <Descriptions.Item label="模型标识">
                  <Tag>{aiConfig.model_key || '-'}</Tag>
                </Descriptions.Item>
                <Descriptions.Item label="引擎状态">
                  {aiConfig.engine_loaded ? (
                    <Tag color="success">已加载</Tag>
                  ) : (
                    <Tag color="error">未加载</Tag>
                  )}
                </Descriptions.Item>
              </Descriptions>

              {!aiConfig.engine_loaded && (
                <Alert
                  style={{ marginTop: 16 }}
                  type="warning"
                  icon={<ExclamationCircleOutlined />}
                  showIcon
                  message="RAG引擎未加载"
                  description="AI分析功能需要先加载本地模型。请前往智能问答页面加载模型后再使用。"
                  action={
                    <Button
                      size="small"
                      type="link"
                      icon={<LinkOutlined />}
                      onClick={() => navigate('/')}
                    >
                      前往加载
                    </Button>
                  }
                />
              )}

              {aiConfig.available_models && Object.keys(aiConfig.available_models).length > 0 && (
                <div style={{ marginTop: 16 }}>
                  <div style={{ color: 'var(--text-secondary)', fontSize: 12, marginBottom: 8 }}>
                    可用模型
                  </div>
                  <Space wrap>
                    {Object.entries(aiConfig.available_models).map(([key, info]) => (
                      <Tag
                        key={key}
                        color={key === aiConfig.model_key ? 'processing' : 'default'}
                      >
                        {info.name} - {info.description}
                      </Tag>
                    ))}
                  </Space>
                </div>
              )}

              <div style={{ marginTop: 16 }}>
                <Button
                  icon={<ThunderboltOutlined />}
                  loading={testing}
                  onClick={() => void handleTestAvailability()}
                >
                  测试可用性
                </Button>
              </div>
            </>
          )}
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
