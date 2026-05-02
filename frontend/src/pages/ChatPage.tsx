import React from 'react'
import { ClearOutlined, BulbOutlined } from '@ant-design/icons'
import { useChat } from '@/hooks/useChat'
import ChatWindow from '@/components/chat/ChatWindow'
import ChatInput from '@/components/chat/ChatInput'
import WelcomeCard from '@/components/chat/WelcomeCard'
import { PREDEFINED_QUESTIONS } from '@/utils/constants'

const ChatPage: React.FC = () => {
  const {
    messages,
    isLoading,
    isStreaming,
    engineLoaded,
    sendMessage,
    stopStreaming,
    clearMessages,
  } = useChat()

  const handleQuestionClick = (question: string) => {
    sendMessage(question)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 112px)' }}>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 12,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div
            className={`glow-dot ${engineLoaded ? 'glow-dot-green' : 'glow-dot-red'}`}
            style={{ width: 6, height: 6 }}
          />
          <span
            style={{
              fontSize: 12,
              color: engineLoaded ? 'var(--neon-green)' : 'var(--neon-red)',
              fontWeight: 500,
            }}
          >
            {engineLoaded ? '引擎已启动' : '引擎未启动'}
          </span>
        </div>
        <button
          onClick={clearMessages}
          disabled={messages.length === 0}
          style={{
            background: 'transparent',
            border: '1px solid var(--border-glass)',
            borderRadius: 'var(--radius-sm)',
            color: messages.length > 0 ? 'var(--text-secondary)' : 'var(--text-tertiary)',
            padding: '4px 12px',
            fontSize: 12,
            cursor: messages.length > 0 ? 'pointer' : 'not-allowed',
            display: 'flex',
            alignItems: 'center',
            gap: 4,
            transition: 'all var(--transition-normal)',
          }}
          onMouseEnter={(e) => {
            if (messages.length > 0) {
              e.currentTarget.style.borderColor = 'var(--neon-blue)'
              e.currentTarget.style.color = 'var(--neon-blue)'
            }
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = 'var(--border-glass)'
            e.currentTarget.style.color =
              messages.length > 0 ? 'var(--text-secondary)' : 'var(--text-tertiary)'
          }}
        >
          <ClearOutlined /> 清空对话
        </button>
      </div>

      {messages.length === 0 && !isLoading && !isStreaming ? (
        <div style={{ flex: 1 }}>
          <WelcomeCard />
          <div style={{ maxWidth: 600, margin: '0 auto' }}>
            <div
              style={{
                marginBottom: 10,
                color: 'var(--text-tertiary)',
                fontSize: 12,
                display: 'flex',
                alignItems: 'center',
                gap: 6,
              }}
            >
              <BulbOutlined style={{ color: 'var(--neon-amber)' }} /> 推荐问题：
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {PREDEFINED_QUESTIONS.map((q) => (
                <button
                  key={q}
                  onClick={() => handleQuestionClick(q)}
                  disabled={!engineLoaded}
                  style={{
                    padding: '6px 14px',
                    borderRadius: 20,
                    background: 'var(--bg-glass)',
                    border: '1px solid var(--border-glass)',
                    color: engineLoaded ? 'var(--text-secondary)' : 'var(--text-tertiary)',
                    fontSize: 12,
                    cursor: engineLoaded ? 'pointer' : 'not-allowed',
                    transition: 'all var(--transition-normal)',
                    backdropFilter: 'blur(10px)',
                    WebkitBackdropFilter: 'blur(10px)',
                  }}
                  onMouseEnter={(e) => {
                    if (engineLoaded) {
                      e.currentTarget.style.borderColor = 'var(--neon-blue)'
                      e.currentTarget.style.color = 'var(--neon-blue)'
                      e.currentTarget.style.boxShadow = 'var(--shadow-glow-blue)'
                    }
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = 'var(--border-glass)'
                    e.currentTarget.style.color = engineLoaded
                      ? 'var(--text-secondary)'
                      : 'var(--text-tertiary)'
                    e.currentTarget.style.boxShadow = 'none'
                  }}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <ChatWindow />
      )}

      <ChatInput
        onSend={sendMessage}
        onStop={stopStreaming}
        isLoading={isLoading}
        isStreaming={isStreaming}
        engineLoaded={engineLoaded}
      />
    </div>
  )
}

export default ChatPage
