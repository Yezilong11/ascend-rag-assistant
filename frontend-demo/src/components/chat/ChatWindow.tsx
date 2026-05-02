import { useRef, useEffect } from 'react'
import { Empty, Spin } from 'antd'
import { LoadingOutlined } from '@ant-design/icons'
import { ChatMessage } from './ChatMessage'
import type { Message } from '../../types'

interface ChatWindowProps {
  messages: Message[]
  isLoading?: boolean
  isStreaming?: boolean
  onDeleteMessage?: (messageId: string) => void
}

export function ChatWindow({
  messages,
  isLoading = false,
  isStreaming = false,
  onDeleteMessage,
}: ChatWindowProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight
    }
  }, [messages, isStreaming])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Spin indicator={<LoadingOutlined spin className="text-4xl text-blue-500" />} />
      </div>
    )
  }

  if (messages.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-96">
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description={
            <div className="text-gray-500">
              <p className="text-lg font-medium mb-2">👋 你好！我是昇腾AI竞赛智能助教</p>
              <p className="text-sm">
                我已经预置了近百场大学生竞赛的官方资料，<br />
                你可以随时向我提问。试试点击下方常见问题，或者在输入框输入你的问题吧！
              </p>
            </div>
          }
        />

        <div className="mt-8">
          <div className="text-center mb-4 text-sm text-gray-500 font-medium">
            💡 常见问题示例
          </div>
          <div className="flex flex-wrap gap-2 justify-center">
            {[
              '如何报名西门子杯？',
              '挑战杯的参赛流程是什么？',
              '大唐杯比赛内容是什么？',
              'RoboMaster机甲大师赛参赛条件？',
              '中国国际大学生创新大赛评分标准？',
            ].map((question, index) => (
              <button
                key={index}
                className="px-4 py-2 text-sm bg-white border border-gray-200 rounded-full
                  text-gray-600 hover:border-blue-400 hover:text-blue-600
                  transition-all duration-200 hover:shadow-md"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div
      ref={containerRef}
      className="chat-container overflow-y-auto px-4"
      style={{ maxHeight: 'calc(100vh - 320px)', minHeight: '400px' }}
    >
      {messages.map((message) => (
        <ChatMessage
          key={message.id}
          message={message}
          onDelete={onDeleteMessage}
        />
      ))}

      {isStreaming && (
        <div className="flex justify-start animate-fade-in">
          <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-md p-4 shadow-md">
            <div className="flex items-center gap-2 text-gray-500">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '160ms' }} />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '320ms' }} />
              </div>
              <span className="text-sm">思考中...</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
