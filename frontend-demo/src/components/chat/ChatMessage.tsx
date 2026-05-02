import { Card, Typography, Space } from 'antd'
import { UserOutlined, RobotOutlined, DeleteOutlined } from '@ant-design/icons'
import type { Message } from '../../types'

const { Text } = Typography

interface ChatMessageProps {
  message: Message
  onDelete?: (messageId: string) => void
}

export function ChatMessage({ message, onDelete }: ChatMessageProps) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in`}>
      <div
        className={`max-w-[80%] rounded-2xl p-4 shadow-md transition-all hover:shadow-lg ${
          isUser
            ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-br-md'
            : 'bg-white border border-gray-200 text-gray-800 rounded-bl-md'
        }`}
      >
        <div className="flex items-center gap-2 mb-2">
          <div
            className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${
              isUser ? 'bg-white/20' : 'bg-blue-100'
            }`}
          >
            {isUser ? <UserOutlined /> : <RobotOutlined />}
          </div>
          <Text
            strong
            className={`text-sm ${isUser ? 'text-white/90' : 'text-blue-600'}`}
          >
            {isUser ? '你' : '助教'}
          </Text>
          {!isUser && onDelete && (
            <DeleteOutlined
              className="ml-auto text-gray-400 hover:text-red-500 cursor-pointer transition-colors"
              onClick={() => onDelete(message.id)}
            />
          )}
        </div>

        <div
          className={`leading-relaxed ${
            isUser ? 'text-white' : 'text-gray-700'
          }`}
          style={{ wordBreak: 'break-word' }}
        >
          {message.content}
          {message.content === '' && (
            <span className="inline-block w-2 h-4 bg-blue-500 animate-pulse ml-1" />
          )}
        </div>

        {message.sources && message.sources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-200/30">
            <Text
              className={`text-xs ${isUser ? 'text-white/70' : 'text-gray-500'}`}
            >
              参考来源：
            </Text>
            <div className="mt-2 space-y-1">
              {message.sources.map((source, index) => (
                <div
                  key={index}
                  className={`text-xs p-2 rounded ${
                    isUser ? 'bg-white/10 text-white/80' : 'bg-gray-50 text-gray-600'
                  }`}
                >
                  <div className="font-mono truncate">{source.source}</div>
                  <div className="truncate mt-1 opacity-70">
                    {source.content.substring(0, 100)}...
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
