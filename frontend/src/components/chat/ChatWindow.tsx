import React, { useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useChatStore } from '@/stores/chatStore'
import MessageBubble from './MessageBubble'
import ThinkingIndicator from './ThinkingIndicator'
import SourcePanel from './SourcePanel'

const ChatWindow: React.FC = () => {
  const messages = useChatStore((s) => s.messages)
  const isStreaming = useChatStore((s) => s.isStreaming)
  const isLoading = useChatStore((s) => s.isLoading)
  const currentStreamingContent = useChatStore((s) => s.currentStreamingContent)
  const currentSources = useChatStore((s) => s.currentSources)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, currentStreamingContent])

  return (
    <div
      ref={scrollRef}
      className="scrollbar-custom"
      style={{
        flex: 1,
        overflowY: 'auto',
        padding: '16px 0',
      }}
    >
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
      {isLoading && <ThinkingIndicator />}
      {isStreaming && currentStreamingContent && (
        <div style={{ marginBottom: 20 }} className="animate-fade-in">
          <div
            style={{
              display: 'flex',
              gap: 10,
              maxWidth: '80%',
            }}
          >
            <div
              style={{
                width: 32,
                height: 32,
                borderRadius: 10,
                background: 'var(--gradient-primary)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 16,
                boxShadow: '0 0 12px rgba(0, 212, 255, 0.2)',
                flexShrink: 0,
              }}
            >
              🤖
            </div>
            <div>
              <div
                style={{
                  padding: '12px 18px',
                  borderRadius: '16px 16px 16px 4px',
                  background: 'var(--bg-glass)',
                  border: '1px solid var(--border-glass)',
                  backdropFilter: 'blur(10px)',
                  WebkitBackdropFilter: 'blur(10px)',
                  color: 'var(--text-primary)',
                  lineHeight: 1.6,
                  fontSize: 14,
                }}
              >
                <div className="markdown-body">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {currentStreamingContent}
                  </ReactMarkdown>
                </div>
                <span className="cursor-blink">▊</span>
              </div>
              {!isStreaming && currentSources.length > 0 && (
                <SourcePanel sources={currentSources} />
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ChatWindow
