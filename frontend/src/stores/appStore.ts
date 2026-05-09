import { create } from 'zustand'
import type { RAGStatus } from '@/types/rag'

interface AppStore {
  sidebarCollapsed: boolean
  ragStatus: RAGStatus | null
  isModelLoading: boolean
  vlmEnabled: boolean

  setSidebarCollapsed: (collapsed: boolean) => void
  toggleSidebar: () => void
  setRagStatus: (status: RAGStatus | null) => void
  setModelLoading: (loading: boolean) => void
  setVlmEnabled: (enabled: boolean) => void
}

const initialState: RAGStatus = {
  engine_loaded: false,
  model_key: '',
  model_name: '',
  reranker_enabled: false,
  reranker_model: '',
  knowledge_base_ready: false,
  available_models: {},
  available_rerankers: {},
}

export const useAppStore = create<AppStore>((set) => ({
  sidebarCollapsed: false,
  ragStatus: initialState,
  isModelLoading: false,
  vlmEnabled: false,

  setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),

  toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

  setRagStatus: (status) => set({ ragStatus: status }),

  setModelLoading: (loading) => set({ isModelLoading: loading }),

  setVlmEnabled: (enabled) => set({ vlmEnabled: enabled }),
}))
