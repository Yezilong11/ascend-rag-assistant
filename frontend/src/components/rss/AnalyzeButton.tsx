import React, { useState, useCallback } from 'react'
import { Button, message } from 'antd'
import { RobotOutlined, CheckCircleOutlined } from '@ant-design/icons'
import { rssApi } from '@/services/rssApi'

interface AnalyzeButtonProps {
  articleId: number
  size?: 'small' | 'middle' | 'large'
  type?: 'link' | 'default' | 'primary' | 'dashed' | 'text'
  onAnalyzed?: (result: { summary: string; keywords: string; sentiment: string }) => void
}

const AnalyzeButton: React.FC<AnalyzeButtonProps> = ({ articleId, size = 'middle', type = 'default', onAnalyzed }) => {
  const [loading, setLoading] = useState(false)
  const [analyzed, setAnalyzed] = useState(false)

  const handleAnalyze = useCallback(async () => {
    setLoading(true)
    try {
      const result = await rssApi.ai.analyzeArticle(articleId)
      setAnalyzed(true)
      message.success('AI分析完成')
      onAnalyzed?.(result)
    } catch (error) {
      const msg = (error as Error).message
      if (msg.includes('503') || msg.includes('RAG引擎未加载')) {
        message.error('RAG引擎未加载，请先在智能问答页面加载模型')
      } else {
        message.error(`分析失败: ${msg}`)
      }
    } finally {
      setLoading(false)
    }
  }, [articleId, onAnalyzed])

  if (analyzed) {
    return (
      <Button type={type} size={size} icon={<CheckCircleOutlined />} disabled>
        已分析
      </Button>
    )
  }

  return (
    <Button
      type={type}
      size={size}
      icon={<RobotOutlined />}
      loading={loading}
      onClick={() => void handleAnalyze()}
    >
      AI分析
    </Button>
  )
}

export default AnalyzeButton
