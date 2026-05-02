import { NavLink, useLocation } from 'react-router-dom'
import { Layout as AntLayout, Menu } from 'antd'
import {
  MessageOutlined,
  ApartmentOutlined,
  DatabaseOutlined,
  SettingOutlined,
} from '@ant-design/icons'

const { Sider } = AntLayout

const menuItems = [
  {
    key: '/chat',
    icon: <MessageOutlined />,
    label: <NavLink to="/chat">智能问答</NavLink>,
  },
  {
    key: '/skill-tree',
    icon: <ApartmentOutlined />,
    label: <NavLink to="/skill-tree">技能树</NavLink>,
  },
  {
    key: '/knowledge-base',
    icon: <DatabaseOutlined />,
    label: <NavLink to="/knowledge-base">知识库</NavLink>,
  },
  {
    key: '/settings',
    icon: <SettingOutlined />,
    label: <NavLink to="/settings">设置</NavLink>,
  },
]

export function Sidebar() {
  const location = useLocation()

  return (
    <Sider
      width={220}
      className="bg-white border-r border-gray-200"
      style={{
        position: 'fixed',
        left: 0,
        top: 72,
        bottom: 0,
        overflow: 'auto',
      }}
    >
      <Menu
        mode="inline"
        selectedKeys={[location.pathname]}
        items={menuItems}
        className="!border-none !mt-4"
      />
    </Sider>
  )
}
