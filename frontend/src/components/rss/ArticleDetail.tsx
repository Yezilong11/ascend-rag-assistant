import React from 'react'
import { Tag, Divider } from 'antd'
import { UserOutlined, ClockCircleOutlined, LinkOutlined, GlobalOutlined } from '@ant-design/icons'
import IngestToKBButton from './IngestToKBButton'
import type { Article } from '@/types/rss'

interface ArticleDetailProps {
  article: Article
}

const ArticleDetail: React.FC<ArticleDetailProps> = ({ article }) => {
  return (
    <div>
      <h2
        style={{
          margin: '0 0 12px',
          fontSize: 18,
          fontWeight: 700,
          color: 'var(--text-primary)',
        }}
      >
        {article.title}
      </h2>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, color: 'var(--text-secondary)', fontSize: 13, marginBottom: 12 }}>
        {article.feed && (
          <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <GlobalOutlined /> {article.feed.name}
          </span>
        )}
        {article.author && (
          <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <UserOutlined /> {article.author}
          </span>
        )}
        {article.published_at && (
          <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <ClockCircleOutlined /> {new Date(article.published_at).toLocaleString()}
          </span>
        )}
        {article.link && (
          <a
            href={article.link}
            target="_blank"
            rel="noopener noreferrer"
            style={{ display: 'flex', alignItems: 'center', gap: 4, color: 'var(--neon-blue)' }}
          >
            <LinkOutlined /> 原文链接
          </a>
        )}
      </div>

      {article.tags && article.tags.length > 0 && (
        <div style={{ marginBottom: 12, display: 'flex', gap: 4 }}>
          {article.tags.map((tag) => (
            <Tag key={tag.id} color={tag.color}>{tag.name}</Tag>
          ))}
        </div>
      )}

      {article.summary && (
        <>
          <div
            style={{
              padding: 12,
              borderRadius: 8,
              background: 'rgba(0, 212, 255, 0.06)',
              border: '1px solid rgba(0, 212, 255, 0.15)',
              marginBottom: 16,
              fontSize: 13,
              color: 'var(--text-secondary)',
            }}
          >
            <div style={{ fontWeight: 600, marginBottom: 4, color: 'var(--neon-blue)', fontSize: 12 }}>
              AI 摘要
            </div>
            {article.summary}
          </div>
        </>
      )}

      <Divider style={{ margin: '12px 0' }} />

      <div
        style={{
          fontSize: 14,
          lineHeight: 1.8,
          color: 'var(--text-primary)',
          maxHeight: 400,
          overflowY: 'auto',
        }}
        dangerouslySetInnerHTML={{ __html: article.content }}
      />

      <Divider style={{ margin: '16px 0' }} />

      <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
        <IngestToKBButton articleId={article.id} />
      </div>
    </div>
  )
}

export default ArticleDetail
