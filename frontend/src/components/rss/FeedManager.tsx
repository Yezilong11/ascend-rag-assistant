import React, { useState, useEffect, useCallback } from 'react'
import { Card, Button, Tag, Modal, message, Row, Col, Empty, Spin } from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  SyncOutlined,
  DeleteOutlined,
  GlobalOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons'
import { useRSSStore } from '@/stores/rssStore'
import AddFeedModal from './AddFeedModal'
import type { Feed } from '@/types/rss'

const statusMap: Record<string, { color: string; text: string; icon: React.ReactNode }> = {
  active: { color: 'green', text: '活跃', icon: <CheckCircleOutlined /> },
  idle: { color: 'blue', text: '空闲', icon: <ClockCircleOutlined /> },
  crawling: { color: 'processing', text: '抓取中', icon: <SyncOutlined spin /> },
  error: { color: 'red', text: '错误', icon: <CloseCircleOutlined /> },
  disabled: { color: 'default', text: '已禁用', icon: <ExclamationCircleOutlined /> },
}

const FeedManager: React.FC = () => {
  const { feeds, categories, loading, fetchFeeds, crawlFeed, deleteFeed, updateFeed } =
    useRSSStore()
  const [addModalOpen, setAddModalOpen] = useState(false)
  const [editFeed, setEditFeed] = useState<Feed | null>(null)
  const [crawlingIds, setCrawlingIds] = useState<Set<number>>(new Set())

  useEffect(() => {
    void fetchFeeds()
  }, [fetchFeeds])

  const handleCrawl = useCallback(async (id: number) => {
    setCrawlingIds((prev) => new Set(prev).add(id))
    try {
      await crawlFeed(id)
      message.success('抓取已触发')
      await fetchFeeds()
    } catch (error) {
      message.error((error as Error).message)
    } finally {
      setCrawlingIds((prev) => {
        const next = new Set(prev)
        next.delete(id)
        return next
      })
    }
  }, [crawlFeed, fetchFeeds])

  const handleDelete = useCallback(async (id: number, name: string) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除RSS源「${name}」吗？`,
      okText: '删除',
      cancelText: '取消',
      okButtonProps: { danger: true },
      onOk: async () => {
        try {
          await deleteFeed(id)
          message.success('删除成功')
        } catch (error) {
          message.error((error as Error).message)
        }
      },
    })
  }, [deleteFeed])

  const handleEdit = useCallback((feed: Feed) => {
    setEditFeed(feed)
    setAddModalOpen(true)
  }, [])

  const handleModalClose = useCallback(() => {
    setAddModalOpen(false)
    setEditFeed(null)
  }, [])

  const handleModalSuccess = useCallback(async () => {
    setAddModalOpen(false)
    setEditFeed(null)
    await fetchFeeds()
  }, [fetchFeeds])

  const getCategoryName = useCallback(
    (categoryId?: number) => {
      if (!categoryId) return null
      const cat = categories.find((c) => c.id === categoryId)
      return cat?.name
    },
    [categories],
  )

  if (loading && feeds.length === 0) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: 60 }}>
        <Spin size="large" />
      </div>
    )
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
          <GlobalOutlined /> RSS源管理
        </h3>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setAddModalOpen(true)}
          style={{
            background: 'var(--gradient-primary)',
            border: 'none',
            boxShadow: '0 0 10px rgba(0, 212, 255, 0.2)',
          }}
        >
          添加源
        </Button>
      </div>

      {feeds.length === 0 ? (
        <Empty description="暂无RSS源，点击上方按钮添加" />
      ) : (
        <Row gutter={[16, 16]}>
          {feeds.map((feed) => {
            const status = statusMap[feed.status] ?? statusMap.idle
            return (
              <Col key={feed.id} span={8}>
                <Card
                  size="small"
                  style={{
                    background: 'rgba(17, 24, 39, 0.45)',
                    border: '1px solid var(--border-glass)',
                  }}
                  title={
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <GlobalOutlined style={{ color: 'var(--neon-blue)' }} />
                      <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {feed.name}
                      </span>
                      <Tag color={status.color} icon={status.icon} style={{ marginLeft: 'auto' }}>
                        {status.text}
                      </Tag>
                    </div>
                  }
                  actions={[
                    <EditOutlined key="edit" onClick={() => handleEdit(feed)} />,
                    <SyncOutlined
                      key="crawl"
                      spin={crawlingIds.has(feed.id)}
                      onClick={() => void handleCrawl(feed.id)}
                    />,
                    <DeleteOutlined
                      key="delete"
                      onClick={() => void handleDelete(feed.id, feed.name)}
                    />,
                  ]}
                >
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: 13 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--text-secondary)' }}>
                      <GlobalOutlined style={{ fontSize: 12 }} />
                      <span
                        style={{
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                        }}
                      >
                        {feed.url}
                      </span>
                    </div>
                    {feed.description && (
                      <div style={{ color: 'var(--text-tertiary)', fontSize: 12 }}>
                        {feed.description}
                      </div>
                    )}
                    <div style={{ display: 'flex', gap: 12, color: 'var(--text-tertiary)', fontSize: 12 }}>
                      <span>间隔: {feed.crawl_interval}分钟</span>
                      {feed.last_crawl && (
                        <span>上次: {new Date(feed.last_crawl).toLocaleString()}</span>
                      )}
                    </div>
                    {feed.error_message && (
                      <div style={{ color: '#ff4d4f', fontSize: 12 }}>{feed.error_message}</div>
                    )}
                    {getCategoryName(feed.category_id) && (
                      <Tag style={{ alignSelf: 'flex-start' }}>
                        {getCategoryName(feed.category_id)}
                      </Tag>
                    )}
                  </div>
                </Card>
              </Col>
            )
          })}
        </Row>
      )}

      <AddFeedModal
        open={addModalOpen}
        onClose={handleModalClose}
        onSuccess={handleModalSuccess}
        editFeed={editFeed}
      />
    </div>
  )
}

export default FeedManager
