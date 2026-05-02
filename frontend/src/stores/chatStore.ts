import { create } from 'zustand'
import type { Message, Source } from '@/types/chat'

interface ChatStore {
  messages: Message[]
  isLoading: boolean
  isStreaming: boolean
  currentStreamingContent: string
  currentSources: Source[]

  addMessage: (message: Message) => void
  setLoading: (loading: boolean) => void
  setStreaming: (streaming: boolean) => void
  appendStreamToken: (token: string) => void
  setCurrentSources: (sources: Source[]) => void
  finalizeStream: () => void
  clearMessages: () => void
}

export const useChatStore = create<ChatStore>((set) => ({
  messages: [],
  isLoading: false,
  isStreaming: false,
  currentStreamingContent: '',
  currentSources: [],

  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),

  setLoading: (loading) => set({ isLoading: loading }),

  setStreaming: (streaming) =>
    set({
      isStreaming: streaming,
      currentStreamingContent: streaming ? '' : undefined,
      currentSources: streaming ? [] : undefined,
    }),

  appendStreamToken: (token) =>
    set((state) => ({
      currentStreamingContent: state.currentStreamingContent + token,
    })),

  setCurrentSources: (sources) => set({ currentSources: sources }),

  finalizeStream: () =>
    set((state) => {
      if (!state.currentStreamingContent) return { isStreaming: false }
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: state.currentStreamingContent,
        sources: state.currentSources.length > 0 ? state.currentSources : undefined,
        timestamp: Date.now(),
      }
      return {
        messages: [...state.messages, assistantMessage],
        isStreaming: false,
        currentStreamingContent: '',
        currentSources: [],
      }
    }),

  clearMessages: () =>
    set({
      messages: [],
      currentStreamingContent: '',
      currentSources: [],
    }),
}))
