import React, { useState, useEffect, useCallback } from 'react'
import { Table, Tag, Select, Button, Space, Modal } from 'antd'
import { EyeOutlined } from '@ant-design/icons'
import { useRSSStore } from '@/stores/rssStore'
import ArticleDetail from './ArticleDetail'
import IngestToKBButton from './IngestToKBButton'
import type { Article, ArticleFilter } from '@/types/rss'

const readStatusMap: Record<number, { color: string; text: string }> = {
  0: { color: 'blue', text: '未读' },
  1: { color: 'green', text: '已读' },
}

const ArticleList: React.FC = () => {
  const { articles, feeds, articleTotal, loading, fetchArticles, fetchFeeds } = useRSSStore()
  const [filter, setFilter] = useState<ArticleFilter>({ page: 1, limit: 10 })
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null)

  useEffect(() => {
    void fetchFeeds()
  }, [fetchFeeds])

  useEffect(() => {
    void fetchArticles(filter)
  }, [filter, fetchArticles])

  const handleFilterChange = useCallback(
    (key: keyof ArticleFilter, value: number | undefined) => {
      setFilter((prev) => ({ ...prev, [key]: value, page: 1 }))
    },
    [],
  )

  const handlePageChange = useCallback((page: number, pageSize: number) => {
    setFilter((prev) => ({ ...prev, page, limit: pageSize }))
  }, [])

  const handleViewDetail = useCallback((article: Article) => {
    setSelectedArticle(article)
  }, [])

  const columns = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      render: (text: string, record: Article) => (
        <a onClick={() => handleViewDetail(record)} style={{ color: 'var(--neon-blue)' }}>
          {text}
        </a>
      ),
    },
    {
      title: '来源',
      dataIndex: ['feed', 'name'],
      key: 'feed',
      width: 150,
      ellipsis: true,
    },
    {
      title: '作者',
      dataIndex: 'author',
      key: 'author',
      width: 120,
      ellipsis: true,
      render: (text: string) => text || '-',
    },
    {
      title: '发布时间',
      dataIndex: 'published_at',
      key: 'published_at',
      width: 170,
      render: (text: string) => (text ? new Date(text).toLocaleString() : '-'),
    },
    {
      title: '状态',
      dataIndex: 'read_status',
      key: 'read_status',
      width: 80,
      render: (status: number) => {
        const s = readStatusMap[status] ?? { color: 'default', text: '未知' }
        return <Tag color={s.color}>{s.text}</Tag>
      },
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_: unknown, record: Article) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record)}
          >
            查看
          </Button>
          <IngestToKBButton articleId={record.id} size="small" type="link" />
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', gap: 12, alignItems: 'center' }}>
        <Select
          placeholder="按源筛选"
          allowClear
          style={{ width: 200 }}
          onChange={(value) => handleFilterChange('feed_id', value)}
          options={feeds.map((f) => ({ label: f.name, value: f.id }))}
        />
        <Select
          placeholder="阅读状态"
          allowClear
          style={{ width: 140 }}
          onChange={(value) => handleFilterChange('read_status', value)}
          options={[
            { label: '未读', value: 0 },
            { label: '已读', value: 1 },
          ]}
        />
      </div>

      <Table
        columns={columns}
        dataSource={articles}
        rowKey="id"
        loading={loading}
        pagination={{
          current: filter.page,
          pageSize: filter.limit,
          total: articleTotal,
          onChange: handlePageChange,
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 篇`,
        }}
        style={{ background: 'transparent' }}
      />

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
            文章详情
          </span>
        }
        open={!!selectedArticle}
        onCancel={() => setSelectedArticle(null)}
        footer={null}
        width={720}
        destroyOnClose
      >
        {selectedArticle && <ArticleDetail article={selectedArticle} />}
      </Modal>
    </div>
  )
}

export default ArticleList
