import { create } from 'zustand'
import type { RAGStatus } from '@/types/rag'

interface AppStore {
  sidebarCollapsed: boolean
  theme: 'light' | 'dark'
  ragStatus: RAGStatus | null
  isModelLoading: boolean

  setSidebarCollapsed: (collapsed: boolean) => void
  toggleSidebar: () => void
  setTheme: (theme: 'light' | 'dark') => void
  setRagStatus: (status: RAGStatus | null) => void
  setModelLoading: (loading: boolean) => void
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
  theme: 'light',
  ragStatus: initialState,
  isModelLoading: false,

  setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),

  toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

  setTheme: (theme) => set({ theme }),

  setRagStatus: (status) => set({ ragStatus: status }),

  setModelLoading: (loading) => set({ isModelLoading: loading }),
}))
