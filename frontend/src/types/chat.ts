export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
  timestamp: number
}

export interface Source {
  content: string
  source: string
}

export interface ChatState {
  messages: Message[]
  isLoading: boolean
  currentStreamingContent: string
}
