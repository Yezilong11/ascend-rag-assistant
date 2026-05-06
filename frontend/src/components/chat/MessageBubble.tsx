import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { UserOutlined } from '@ant-design/icons'
import type { Message } from '@/types/chat'
import SourcePanel from './SourcePanel'

interface MessageBubbleProps {
  message: Message
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user'

  return (
    <div
      className="animate-slide-up"
      style={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        marginBottom: 20,
      }}
    >
      <div
        style={{
          display: 'flex',
          gap: 10,
          maxWidth: '80%',
          flexDirection: isUser ? 'row-reverse' : 'row',
        }}
      >
        <div
          style={{
            width: 32,
            height: 32,
            borderRadius: 10,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: isUser ? 'var(--gradient-secondary)' : 'var(--gradient-primary)',
            color: '#fff',
            flexShrink: 0,
            fontSize: 14,
            boxShadow: isUser
              ? '0 0 12px rgba(255, 45, 120, 0.2)'
              : '0 0 12px rgba(0, 212, 255, 0.2)',
          }}
        >
          {isUser ? <UserOutlined /> : '🤖'}
        </div>
        <div>
          <div
            style={{
              padding: '12px 18px',
              borderRadius: isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
              background: isUser
                ? 'linear-gradient(135deg, rgba(123, 47, 255, 0.2) 0%, rgba(255, 45, 120, 0.15) 100%)'
                : 'var(--bg-glass)',
              border: isUser
                ? '1px solid rgba(123, 47, 255, 0.2)'
                : '1px solid var(--border-glass)',
              color: 'var(--text-primary)',
              backdropFilter: 'blur(10px)',
              WebkitBackdropFilter: 'blur(10px)',
              lineHeight: 1.6,
              fontSize: 14,
            }}
          >
            {isUser ? (
              message.content
            ) : (
              <div className="markdown-body">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
              </div>
            )}
          </div>
          {message.sources && message.sources.length > 0 && (
            <SourcePanel sources={message.sources} />
          )}
        </div>
      </div>
    </div>
  )
}

export default MessageBubble
