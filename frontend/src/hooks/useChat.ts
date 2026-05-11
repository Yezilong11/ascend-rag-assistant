import { useCallback, useRef } from 'react'
import { useChatStore } from '@/stores/chatStore'
import { useAppStore } from '@/stores/appStore'
import { ragApi } from '@/services/ragApi'
import { multimodalApi } from '@/services/multimodalApi'
import { parseSSEStream } from '@/utils/sse'
import type { Source } from '@/types/chat'

export function useSSE() {
  const abortControllerRef = useRef<AbortController | null>(null)

  const addMessage = useChatStore((s) => s.addMessage)
  const setStreaming = useChatStore((s) => s.setStreaming)
  const appendStreamToken = useChatStore((s) => s.appendStreamToken)
  const setCurrentSources = useChatStore((s) => s.setCurrentSources)
  const finalizeStream = useChatStore((s) => s.finalizeStream)
  const setLoading = useChatStore((s) => s.setLoading)

  const connect = useCallback(
    async (question: string) => {
      abortControllerRef.current = new AbortController()

      const userMessage = {
        id: crypto.randomUUID(),
        role: 'user' as const,
        content: question,
        timestamp: Date.now(),
      }
      addMessage(userMessage)
      setLoading(true)
      setStreaming(true)

      try {
        const response = await fetch(ragApi.chatStreamUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question }),
          signal: abortControllerRef.current.signal,
        })

        if (!response.ok) {
          throw new Error(`HTTP error: ${response.status}`)
        }

        const reader = response.body?.getReader()
        if (!reader) throw new Error('No reader available')

        setLoading(false)

        parseSSEStream(reader, {
          onToken: (token) => appendStreamToken(token),
          onSources: (sources) => setCurrentSources(sources as Source[]),
          onDone: () => finalizeStream(),
          onError: (error) => {
            console.error('SSE error:', error)
            finalizeStream()
          },
        })
      } catch (error) {
        setLoading(false)
        setStreaming(false)
        if ((error as Error).name !== 'AbortError') {
          const errorMessage = {
            id: crypto.randomUUID(),
            role: 'assistant' as const,
            content: `抱歉，请求处理失败：${(error as Error).message}`,
            timestamp: Date.now(),
          }
          addMessage(errorMessage)
        }
      }
    },
    [addMessage, setStreaming, appendStreamToken, setCurrentSources, finalizeStream, setLoading],
  )

  const disconnect = useCallback(() => {
    abortControllerRef.current?.abort()
    abortControllerRef.current = null
    finalizeStream()
  }, [finalizeStream])

  return { connect, disconnect }
}

export function useChat() {
  const messages = useChatStore((s) => s.messages)
  const isLoading = useChatStore((s) => s.isLoading)
  const isStreaming = useChatStore((s) => s.isStreaming)
  const currentStreamingContent = useChatStore((s) => s.currentStreamingContent)
  const currentSources = useChatStore((s) => s.currentSources)
  const clearMessages = useChatStore((s) => s.clearMessages)
  const engineLoaded = useAppStore((s) => s.ragStatus?.engine_loaded ?? false)

  const { connect, disconnect } = useSSE()

  const connectWithAttachments = useCallback(
    async (question: string, attachments: File[]) => {
      const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp']
      const pdfExtensions = ['pdf']
      
      const imageFiles = attachments.filter(file => {
        const ext = file.name.split('.').pop()?.toLowerCase() || ''
        return imageExtensions.includes(ext)
      })
      
      const pdfFiles = attachments.filter(file => {
        const ext = file.name.split('.').pop()?.toLowerCase() || ''
        return pdfExtensions.includes(ext)
      })
      
      const contextParts: string[] = []
      
      try {
        if (imageFiles.length > 0) {
          const result = await multimodalApi.ingestImage(imageFiles, 'unknown', false)
          if (result.success_count > 0) {
            contextParts.push(`${result.success_count} 张图片已导入多模态知识库`)
          }
        }
        
        if (pdfFiles.length > 0) {
          for (const pdfFile of pdfFiles) {
            await ragApi.ingest(pdfFile)
          }
          contextParts.push(`${pdfFiles.length} 个PDF文档已导入知识库`)
        }
        
        const context = contextParts.length > 0
          ? `\n\n[用户附加了：${contextParts.join('；')}，已导入知识库]`
          : ''
        connect(question + context)
      } catch (error) {
        connect(question + '\n\n[文件上传失败，仅基于文本回答]')
      }
    },
    [connect],
  )

  const sendMessage = useCallback(
    (question: string, attachments?: File[]) => {
      if ((!question.trim() && (!attachments || attachments.length === 0)) || isLoading || isStreaming) return
      if (!engineLoaded) return
      if (attachments && attachments.length > 0) {
        void connectWithAttachments(question.trim(), attachments)
      } else {
        void connect(question.trim())
      }
    },
    [isLoading, isStreaming, engineLoaded, connect, connectWithAttachments],
  )

  const stopStreaming = useCallback(() => {
    disconnect()
  }, [disconnect])

  return {
    messages,
    isLoading,
    isStreaming,
    currentStreamingContent,
    currentSources,
    engineLoaded,
    sendMessage,
    stopStreaming,
    clearMessages,
  }
}
