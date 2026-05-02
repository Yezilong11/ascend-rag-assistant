import { Outlet } from 'react-router-dom'
import { Layout as AntLayout } from 'antd'
import { Header } from './Header'
import { Sidebar } from './Sidebar'

const { Content } = AntLayout

export function Layout() {
  return (
    <AntLayout className="min-h-screen bg-gray-50">
      <Header />
      <AntLayout>
        <Sidebar />
        <Content className="p-6">
          <div className="max-w-6xl mx-auto">
            <Outlet />
          </div>
        </Content>
      </AntLayout>
    </AntLayout>
  )
}
