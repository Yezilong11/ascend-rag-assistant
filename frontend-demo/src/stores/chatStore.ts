import { create } from 'zustand'
import type { Message, Model, Source } from '../types'
import { apiService } from '../services/api'

interface ChatState {
  messages: Message[]
  isLoading: boolean
  isStreaming: boolean
  error: string | null
  sessionId: string | null
  availableModels: Record<string, Model>
  currentModelKey: string
  sources: Source[]

  setMessages: (messages: Message[]) => void
  addMessage: (message: Message) => void
  updateLastMessage: (content: string, sources?: Source[]) => void
  clearMessages: () => void
  setLoading: (isLoading: boolean) => void
  setStreaming: (isStreaming: boolean) => void
  setError: (error: string | null) => void
  setSessionId: (sessionId: string) => void
  setAvailableModels: (models: Record<string, Model>) => void
  setCurrentModelKey: (modelKey: string) => void

  sendMessage: (content: string) => Promise<void>
  loadModels: () => Promise<void>
  initChat: () => Promise<void>
}

const generateId = () => Math.random().toString(36).substring(2, 15)

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isLoading: false,
  isStreaming: false,
  error: null,
  sessionId: null,
  availableModels: {},
  currentModelKey: 'qwen2-1.5b',
  sources: [],

  setMessages: (messages) => set({ messages }),

  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),

  updateLastMessage: (content, sources) =>
    set((state) => {
      const messages = [...state.messages]
      const lastMessage = messages[messages.length - 1]
      if (lastMessage && lastMessage.role === 'assistant') {
        messages[messages.length - 1] = {
          ...lastMessage,
          content: lastMessage.content + content,
          sources: sources || lastMessage.sources,
        }
      }
      return { messages }
    }),

  clearMessages: () => set({ messages: [], sources: [] }),

  setLoading: (isLoading) => set({ isLoading }),

  setStreaming: (isStreaming) => set({ isStreaming }),

  setError: (error) => set({ error }),

  setSessionId: (sessionId) => set({ sessionId }),

  setAvailableModels: (models) => set({ availableModels: models }),

  setCurrentModelKey: (modelKey) => set({ currentModelKey: modelKey }),

  sendMessage: async (content) => {
    const { addMessage, updateLastMessage, setError, setStreaming, currentModelKey, sessionId } = get()

    const userMessage: Message = {
      id: generateId(),
      role: 'user',
      content,
      timestamp: Date.now(),
    }

    addMessage(userMessage)
    setStreaming(true)
    setError(null)

    const assistantMessage: Message = {
      id: generateId(),
      role: 'assistant',
      content: '',
      timestamp: Date.now(),
    }

    addMessage(assistantMessage)

    try {
      await apiService.chatStream(
        {
          question: content,
          model_key: currentModelKey,
          session_id: sessionId || undefined,
        },
        (chunk) => {
          if (chunk.done) {
            setStreaming(false)
          } else {
            updateLastMessage(chunk.token, chunk.sources)
          }
        },
        (error) => {
          setError(error.message)
          setStreaming(false)
        }
      )
    } catch (error) {
      setError((error as Error).message)
      setStreaming(false)
    }
  },

  loadModels: async () => {
    try {
      const response = await apiService.getAvailableModels()
      if (response.code === 0 && response.data) {
        set({ availableModels: response.data })
      }
    } catch (error) {
      console.error('Failed to load models:', error)
    }
  },

  initChat: async () => {
    set({ isLoading: true })
    try {
      await get().loadModels()
    } catch (error) {
      set({ error: (error as Error).message })
    } finally {
      set({ isLoading: false })
    }
  },
}))
