import React, { useEffect } from 'react'
import { Tabs } from 'antd'
import {
  DashboardOutlined,
  GlobalOutlined,
  FileTextOutlined,
  FolderOutlined,
  TagsOutlined,
  SettingOutlined,
} from '@ant-design/icons'
import { useRSSStore } from '@/stores/rssStore'
import RSSDashboard from '@/components/rss/RSSDashboard'
import FeedManager from '@/components/rss/FeedManager'
import ArticleList from '@/components/rss/ArticleList'
import RSSCategories from '@/components/rss/RSSCategories'
import RSSTags from '@/components/rss/RSSTags'
import RSSSettings from '@/components/rss/RSSSettings'

const RSSPage: React.FC = () => {
  const { fetchFeeds, fetchCategories, fetchTags, fetchStats } = useRSSStore()

  useEffect(() => {
    void Promise.all([fetchFeeds(), fetchCategories(), fetchTags(), fetchStats()])
  }, [fetchFeeds, fetchCategories, fetchTags, fetchStats])

  const tabItems = [
    {
      key: 'dashboard',
      label: '仪表盘',
      icon: <DashboardOutlined />,
      children: <RSSDashboard />,
    },
    {
      key: 'feeds',
      label: 'RSS源',
      icon: <GlobalOutlined />,
      children: <FeedManager />,
    },
    {
      key: 'articles',
      label: '文章',
      icon: <FileTextOutlined />,
      children: <ArticleList />,
    },
    {
      key: 'categories',
      label: '分类',
      icon: <FolderOutlined />,
      children: <RSSCategories />,
    },
    {
      key: 'tags',
      label: '标签',
      icon: <TagsOutlined />,
      children: <RSSTags />,
    },
    {
      key: 'settings',
      label: '设置',
      icon: <SettingOutlined />,
      children: <RSSSettings />,
    },
  ]

  return (
    <div style={{ height: 'calc(100vh - 112px)', overflowY: 'auto' }}>
      <Tabs
        defaultActiveKey="dashboard"
        items={tabItems}
        style={{ padding: '0 16px' }}
      />
    </div>
  )
}

export default RSSPage
