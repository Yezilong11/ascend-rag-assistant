import React, { useState, useCallback } from 'react'
import { Button, message } from 'antd'
import { ImportOutlined, CheckCircleOutlined } from '@ant-design/icons'
import { rssApi } from '@/services/rssApi'

interface IngestToKBButtonProps {
  articleId: number
  size?: 'small' | 'middle' | 'large'
  type?: 'link' | 'default' | 'primary' | 'dashed' | 'text'
  shortText?: boolean
}

const IngestToKBButton: React.FC<IngestToKBButtonProps> = ({
  articleId,
  size = 'middle',
  type = 'default',
  shortText = false,
}) => {
  const [loading, setLoading] = useState(false)
  const [ingested, setIngested] = useState(false)

  const handleIngest = useCallback(async () => {
    setLoading(true)
    try {
      const result = await rssApi.bridge.ingestArticle(articleId)
      setIngested(true)
      message.success(`导入成功，生成 ${result.chunks_count} 个分块`)
    } catch (error) {
      message.error((error as Error).message)
    } finally {
      setLoading(false)
    }
  }, [articleId])

  if (ingested) {
    return (
      <Button
        type={type}
        size={size}
        icon={<CheckCircleOutlined />}
        disabled
        style={{ whiteSpace: 'nowrap' }}
        title={shortText ? '已导入知识库' : undefined}
      >
        {shortText ? '已导入' : '已导入知识库'}
      </Button>
    )
  }

  return (
    <Button
      type={type}
      size={size}
      icon={<ImportOutlined />}
      loading={loading}
      onClick={() => void handleIngest()}
      style={{ whiteSpace: 'nowrap' }}
      title={shortText ? '导入知识库' : undefined}
    >
      {shortText ? '导入' : '导入知识库'}
    </Button>
  )
}

export default IngestToKBButton
