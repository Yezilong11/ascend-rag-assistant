import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ConfigProvider, theme } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import AppLayout from '@/components/layout/AppLayout'
import ChatPage from '@/pages/ChatPage'
import SkillTreePage from '@/pages/SkillTreePage'
import SettingsPage from '@/pages/SettingsPage'
import RSSPage from '@/pages/RSSPage'

const antTheme = {
  algorithm: theme.darkAlgorithm,
  token: {
    colorPrimary: '#00d4ff',
    colorBgContainer: 'rgba(17, 24, 39, 0.65)',
    colorBgElevated: 'rgba(30, 36, 64, 0.85)',
    colorBgLayout: 'transparent',
    colorBorder: 'rgba(0, 212, 255, 0.12)',
    colorText: '#e2e8f0',
    colorTextSecondary: '#94a3b8',
    colorTextTertiary: '#64748b',
    borderRadius: 8,
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  },
  components: {
    Button: {
      colorPrimary: '#00d4ff',
      algorithm: true,
    },
    Input: {
      colorBgContainer: 'rgba(17, 24, 39, 0.65)',
      colorBorder: 'rgba(0, 212, 255, 0.12)',
    },
    Select: {
      colorBgContainer: 'rgba(17, 24, 39, 0.65)',
      colorBorder: 'rgba(0, 212, 255, 0.12)',
    },
    Message: {
      colorBgElevated: 'rgba(30, 36, 64, 0.95)',
    },
  },
}

const App: React.FC = () => {
  return (
    <ConfigProvider locale={zhCN} theme={antTheme}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<AppLayout />}>
            <Route index element={<Navigate to="/chat" replace />} />
            <Route path="chat" element={<ChatPage />} />
            <Route path="skill-tree" element={<SkillTreePage />} />
            <Route path="rss" element={<RSSPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  )
}

export default App
