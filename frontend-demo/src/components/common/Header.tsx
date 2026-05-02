import { Badge, Space, Typography, Dropdown, Avatar } from 'antd'
import {
  RobotOutlined,
  BellOutlined,
  UserOutlined,
  SettingOutlined,
  QuestionCircleOutlined,
} from '@ant-design/icons'

const { Title, Text } = Typography

export function Header() {
  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人中心',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '设置',
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      label: '退出登录',
    },
  ]

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20">
            <RobotOutlined className="text-white text-xl" />
          </div>
          <div>
            <Title level={4} className="!mb-0 !text-gray-800">
              昇腾AI竞赛智能助教
            </Title>
            <Text type="secondary" className="text-xs">
              基于RAG技术的全天候竞赛知识助手
            </Text>
          </div>
        </div>

        <Space size="middle">
          <Badge count={3} size="small">
            <BellOutlined className="text-xl text-gray-500 cursor-pointer hover:text-blue-500 transition-colors" />
          </Badge>

          <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
            <div className="flex items-center gap-2 cursor-pointer hover:bg-gray-100 px-3 py-1.5 rounded-lg transition-colors">
              <Avatar size="small" icon={<UserOutlined />} className="bg-blue-500" />
              <Text className="text-sm font-medium">姜美辰</Text>
            </div>
          </Dropdown>
        </Space>
      </div>
    </header>
  )
}
