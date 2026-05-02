import { create } from 'zustand'
import type { AppSettings, ModelConfig, SystemStatus } from '../types'
import { apiService } from '../services/api'

interface AppState {
  settings: AppSettings
  systemStatus: SystemStatus
  isInitialized: boolean

  setSettings: (settings: Partial<AppSettings>) => void
  setSystemStatus: (status: SystemStatus) => void
  setInitialized: (isInitialized: boolean) => void

  loadSettings: () => void
  saveSettings: (settings: Partial<AppSettings>) => void
  checkSystemStatus: () => Promise<void>
  initApp: () => Promise<void>
}

const DEFAULT_SETTINGS: AppSettings = {
  theme: 'light',
  language: 'zh-CN',
  model_config: {
    model_key: 'qwen2-1.5b',
    model_dir: './models',
    use_reranker: true,
    reranker_key: 'bge-reranker-v2-m3',
    reranker_top_k: 3,
    initial_retrieval_k: 10,
  },
  api_base_url: 'http://localhost:8000',
  rag_api_base_url: 'http://localhost:8001',
}

export const useAppStore = create<AppState>((set, get) => ({
  settings: DEFAULT_SETTINGS,
  systemStatus: {
    api_connected: false,
    rag_connected: false,
    knowledge_base_ready: false,
    model_loaded: false,
  },
  isInitialized: false,

  setSettings: (newSettings) =>
    set((state) => ({
      settings: { ...state.settings, ...newSettings },
    })),

  setSystemStatus: (status) => set({ systemStatus: status }),

  setInitialized: (isInitialized) => set({ isInitialized }),

  loadSettings: () => {
    const savedSettings = localStorage.getItem('app_settings')
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings)
        set((state) => ({
          settings: { ...state.settings, ...parsed },
        }))
      } catch (error) {
        console.error('Failed to parse saved settings:', error)
      }
    }
  },

  saveSettings: (newSettings) => {
    const currentSettings = get().settings
    const updatedSettings = { ...currentSettings, ...newSettings }
    localStorage.setItem('app_settings', JSON.stringify(updatedSettings))
    set({ settings: updatedSettings })
  },

  checkSystemStatus: async () => {
    try {
      const response = await apiService.getSystemStatus()
      if (response.code === 0 && response.data) {
        set({ systemStatus: response.data })
      }
    } catch (error) {
      console.error('Failed to check system status:', error)
      set({
        systemStatus: {
          api_connected: false,
          rag_connected: false,
          knowledge_base_ready: false,
          model_loaded: false,
        },
      })
    }
  },

  initApp: async () => {
    set({ isInitialized: false })
    get().loadSettings()
    await get().checkSystemStatus()
    set({ isInitialized: true })
  },
}))
