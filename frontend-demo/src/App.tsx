import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from './components/common/Layout'
import { ChatPage } from './pages/ChatPage'
import { SkillTreePage } from './pages/SkillTreePage'
import { KnowledgeBasePage } from './pages/KnowledgeBasePage'
import { SettingsPage } from './pages/SettingsPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/chat" replace />} />
          <Route path="chat" element={<ChatPage />} />
          <Route path="skill-tree" element={<SkillTreePage />} />
          <Route path="knowledge-base" element={<KnowledgeBasePage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
