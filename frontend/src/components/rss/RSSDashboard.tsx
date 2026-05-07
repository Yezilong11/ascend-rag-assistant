import React from 'react'
import { Card, Row, Col, Statistic, Button, message } from 'antd'
import {
  GlobalOutlined,
  FileTextOutlined,
  PlusCircleOutlined,
  SyncOutlined,
  ClockCircleOutlined,
  EyeOutlined,
} from '@ant-design/icons'
import { useRSSStore } from '@/stores/rssStore'

const RSSDashboard: React.FC = () => {
  const { stats, crawlAllFeeds, fetchStats, fetchFeeds } = useRSSStore()

  const handleCrawlAll = async () => {
    try {
      await crawlAllFeeds()
      message.success('已触发全量抓取')
      void Promise.all([fetchStats(), fetchFeeds()])
    } catch (error) {
      message.error((error as Error).message)
    }
  }

  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card
            style={{
              background: 'rgba(0, 212, 255, 0.06)',
              border: '1px solid rgba(0, 212, 255, 0.15)',
            }}
          >
            <Statistic
              title="RSS源数量"
              value={stats?.feeds_count ?? 0}
              prefix={<GlobalOutlined style={{ color: 'var(--neon-blue)' }} />}
              valueStyle={{ color: 'var(--neon-blue)' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card
            style={{
              background: 'rgba(0, 255, 136, 0.06)',
              border: '1px solid rgba(0, 255, 136, 0.15)',
            }}
          >
            <Statistic
              title="文章总数"
              value={stats?.articles_count ?? 0}
              prefix={<FileTextOutlined style={{ color: 'var(--neon-green)' }} />}
              valueStyle={{ color: 'var(--neon-green)' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card
            style={{
              background: 'rgba(123, 47, 255, 0.06)',
              border: '1px solid rgba(123, 47, 255, 0.15)',
            }}
          >
            <Statistic
              title="今日新增"
              value={stats?.today_articles ?? 0}
              prefix={<ClockCircleOutlined style={{ color: 'var(--neon-purple)' }} />}
              valueStyle={{ color: 'var(--neon-purple)' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card
            style={{
              background: 'rgba(255, 184, 0, 0.06)',
              border: '1px solid rgba(255, 184, 0, 0.15)',
            }}
          >
            <Statistic
              title="未读数"
              value={stats?.unread_count ?? 0}
              prefix={<EyeOutlined style={{ color: 'var(--neon-amber)' }} />}
              valueStyle={{ color: 'var(--neon-amber)' }}
            />
          </Card>
        </Col>
      </Row>

      <div style={{ marginTop: 24, display: 'flex', gap: 12 }}>
        <Button
          type="primary"
          icon={<SyncOutlined />}
          onClick={() => void handleCrawlAll()}
          style={{
            background: 'var(--gradient-primary)',
            border: 'none',
            boxShadow: '0 0 10px rgba(0, 212, 255, 0.2)',
          }}
        >
          抓取所有源
        </Button>
        <Button
          icon={<PlusCircleOutlined />}
          onClick={() => {
            const tabEl = document.querySelector('[data-node-key="feeds"]') as HTMLElement
            tabEl?.click()
          }}
        >
          添加RSS源
        </Button>
      </div>
    </div>
  )
}

export default RSSDashboard
