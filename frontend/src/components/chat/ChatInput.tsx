import React, { useState } from 'react'
import { SendOutlined, StopOutlined, PlusOutlined, CloseOutlined, FilePdfOutlined, PictureOutlined } from '@ant-design/icons'

interface ChatInputProps {
  onSend: (message: string, attachments?: File[]) => void
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
  const [attachments, setAttachments] = useState<File[]>([])

  const handleFileSelect = () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.jpg,.jpeg,.png,.gif,.bmp,.pdf'
    input.multiple = true
    input.onchange = (e) => {
      const files = Array.from((e.target as HTMLInputElement).files ?? [])
      if (files.length > 0) {
        setAttachments((prev) => [...prev, ...files])
      }
    }
    input.click()
  }

  const removeAttachment = (index: number) => {
    setAttachments((prev) => prev.filter((_, i) => i !== index))
  }

  const handleSend = () => {
    if (!inputValue.trim() && attachments.length === 0) return
    onSend(inputValue, attachments.length > 0 ? attachments : undefined)
    setInputValue('')
    setAttachments([])
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
      {attachments.length > 0 && (
        <div style={{ display: 'flex', gap: 8, marginBottom: 8, flexWrap: 'wrap' }}>
          {attachments.map((file, index) => {
            const isPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')
            return (
              <div
                key={index}
                style={{
                  position: 'relative',
                  width: 64,
                  height: 64,
                  borderRadius: 'var(--radius-sm)',
                  overflow: 'hidden',
                  border: '1px solid var(--border-glass)',
                  background: isPdf ? 'rgba(255, 140, 0, 0.1)' : 'var(--bg-glass)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                {isPdf ? (
                  <div style={{ textAlign: 'center' }}>
                    <FilePdfOutlined style={{ fontSize: 24, color: '#ff8c00' }} />
                    <div style={{ fontSize: 8, color: 'var(--text-tertiary)', marginTop: 2, maxWidth: 56, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {file.name}
                    </div>
                  </div>
                ) : (
                  <img
                    src={URL.createObjectURL(file)}
                    alt={file.name}
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  />
                )}
                <button
                  onClick={() => removeAttachment(index)}
                  style={{
                    position: 'absolute',
                    top: 2,
                    right: 2,
                    width: 18,
                    height: 18,
                    borderRadius: '50%',
                    background: 'rgba(0,0,0,0.6)',
                    border: 'none',
                    color: '#fff',
                    fontSize: 10,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    padding: 0,
                  }}
                >
                  <CloseOutlined style={{ fontSize: 10 }} />
                </button>
              </div>
            )
          })}
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
        <button
          onClick={handleFileSelect}
          disabled={isLoading || !engineLoaded}
          style={{
            padding: '12px 14px',
            borderRadius: 'var(--radius-md)',
            background: 'var(--bg-glass)',
            border: '1px solid var(--border-glass)',
            color: attachments.length > 0 ? 'var(--neon-blue)' : 'var(--text-tertiary)',
            cursor: isLoading || !engineLoaded ? 'not-allowed' : 'pointer',
            fontSize: 18,
            transition: 'all var(--transition-normal)',
            display: 'flex',
            alignItems: 'center',
            fontWeight: 300,
          }}
          onMouseEnter={(e) => {
            if (engineLoaded && !isLoading) {
              e.currentTarget.style.borderColor = 'var(--neon-blue)'
              e.currentTarget.style.color = 'var(--neon-blue)'
            }
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = 'var(--border-glass)'
            e.currentTarget.style.color = attachments.length > 0 ? 'var(--neon-blue)' : 'var(--text-tertiary)'
          }}
          title="上传图片或PDF"
        >
          <PlusOutlined />
        </button>
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
