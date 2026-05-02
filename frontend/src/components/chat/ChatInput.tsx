import React, { useState } from 'react'
import { SendOutlined, StopOutlined } from '@ant-design/icons'

interface ChatInputProps {
  onSend: (message: string) => void
  onStop: () => void
  isLoading: boolean
  isStreaming: boolean
  engineLoaded: boolean
}

const ChatInput: React.FC<ChatInputProps> = ({
  onSend,
  onStop,
  isLoading,
  isStreaming,
  engineLoaded,
}) => {
  const [inputValue, setInputValue] = useState('')

  const handleSend = () => {
    if (!inputValue.trim()) return
    onSend(inputValue)
    setInputValue('')
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div style={{ padding: '16px 0 0' }}>
      {!engineLoaded && (
        <div
          style={{
            padding: '8px 14px',
            borderRadius: 'var(--radius-sm)',
            background: 'rgba(255, 184, 0, 0.08)',
            border: '1px solid rgba(255, 184, 0, 0.2)',
            color: 'var(--neon-amber)',
            fontSize: 12,
            marginBottom: 12,
            display: 'flex',
            alignItems: 'center',
            gap: 6,
          }}
        >
          ⚠️ AI引擎未启动，请先在设置页面加载模型
        </div>
      )}
      <div
        style={{
          display: 'flex',
          gap: 8,
          alignItems: 'flex-end',
        }}
      >
        <div
          style={{
            flex: 1,
            position: 'relative',
          }}
        >
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={engineLoaded ? '输入您的问题...' : '请先启动AI引擎'}
            disabled={isLoading || !engineLoaded}
            rows={1}
            style={{
              width: '100%',
              padding: '12px 18px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--bg-glass)',
              border: '1px solid var(--border-glass)',
              color: 'var(--text-primary)',
              fontSize: 14,
              outline: 'none',
              resize: 'none',
              fontFamily: 'inherit',
              lineHeight: 1.5,
              backdropFilter: 'blur(10px)',
              WebkitBackdropFilter: 'blur(10px)',
              transition: 'all var(--transition-normal)',
              minHeight: 48,
              maxHeight: 120,
            }}
            onFocus={(e) => {
              e.currentTarget.style.borderColor = 'var(--neon-blue)'
              e.currentTarget.style.boxShadow =
                '0 0 0 2px rgba(0, 212, 255, 0.1), var(--shadow-glow-blue)'
            }}
            onBlur={(e) => {
              e.currentTarget.style.borderColor = 'var(--border-glass)'
              e.currentTarget.style.boxShadow = 'none'
            }}
          />
        </div>
        {isStreaming ? (
          <button
            onClick={onStop}
            style={{
              padding: '12px 20px',
              borderRadius: 'var(--radius-md)',
              background: 'rgba(255, 51, 102, 0.15)',
              border: '1px solid rgba(255, 51, 102, 0.3)',
              color: 'var(--neon-red)',
              cursor: 'pointer',
              fontSize: 14,
              fontWeight: 500,
              transition: 'all var(--transition-normal)',
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              whiteSpace: 'nowrap',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.boxShadow = 'var(--shadow-glow-pink)'
              e.currentTarget.style.background = 'rgba(255, 51, 102, 0.25)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.boxShadow = 'none'
              e.currentTarget.style.background = 'rgba(255, 51, 102, 0.15)'
            }}
          >
            <StopOutlined /> 停止
          </button>
        ) : (
          <button
            onClick={handleSend}
            disabled={!inputValue.trim() || isLoading || !engineLoaded}
            style={{
              padding: '12px 24px',
              borderRadius: 'var(--radius-md)',
              background:
                inputValue.trim() && engineLoaded
                  ? 'var(--gradient-primary)'
                  : 'var(--bg-tertiary)',
              border: 'none',
              color: inputValue.trim() && engineLoaded ? '#fff' : 'var(--text-tertiary)',
              cursor: inputValue.trim() && engineLoaded ? 'pointer' : 'not-allowed',
              fontSize: 14,
              fontWeight: 600,
              transition: 'all var(--transition-normal)',
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              whiteSpace: 'nowrap',
              boxShadow:
                inputValue.trim() && engineLoaded ? '0 4px 15px rgba(0, 212, 255, 0.25)' : 'none',
            }}
            onMouseEnter={(e) => {
              if (inputValue.trim() && engineLoaded) {
                e.currentTarget.style.boxShadow = '0 6px 25px rgba(0, 212, 255, 0.4)'
                e.currentTarget.style.transform = 'translateY(-1px)'
              }
            }}
            onMouseLeave={(e) => {
              if (inputValue.trim() && engineLoaded) {
                e.currentTarget.style.boxShadow = '0 4px 15px rgba(0, 212, 255, 0.25)'
                e.currentTarget.style.transform = 'translateY(0)'
              }
            }}
          >
            <SendOutlined /> 发送
          </button>
        )}
      </div>
    </div>
  )
}

export default ChatInput
