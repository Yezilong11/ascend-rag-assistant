import { ragApiClient } from './api'
import type { RAGStatus, ModelLoadRequest, ChatResponse, KnowledgeBaseStats } from '@/types/rag'
import type { ApiResponse } from '@/types/api'

export const ragApi = {
  getStatus: async (): Promise<RAGStatus> => {
    const { data } = await ragApiClient.get<ApiResponse<RAGStatus>>('/status')
    if (!data.success || !data.data) throw new Error('获取RAG状态失败')
    return data.data
  },

  loadModel: async (request: ModelLoadRequest): Promise<void> => {
    const { data } = await ragApiClient.post<ApiResponse<{ model_key: string; status: string }>>(
      '/model/load',
      request,
    )
    if (!data.success) {
      throw new Error(data.success === false ? data.message : '模型加载失败')
    }
  },

  unloadModel: async (): Promise<void> => {
    const { data } = await ragApiClient.post<ApiResponse<null>>('/model/unload')
    if (!data.success) {
      throw new Error(data.success === false ? data.message : '模型卸载失败')
    }
  },

  chat: async (question: string): Promise<ChatResponse> => {
    const { data } = await ragApiClient.post<ApiResponse<ChatResponse>>('/chat', { question })
    if (!data.success || !data.data) throw new Error('问答请求失败')
    return data.data
  },

  chatStreamUrl: '/api/rag/chat/stream',

  ingest: async (file: File): Promise<void> => {
    const formData = new FormData()
    formData.append('file', file)
    const { data } = await ragApiClient.post<ApiResponse<null>>('/ingest', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    if (!data.success) {
      throw new Error(data.success === false ? data.message : '文件导入失败')
    }
  },

  autoIngest: async (): Promise<void> => {
    const { data } = await ragApiClient.post<ApiResponse<null>>('/knowledge-base/auto-ingest')
    if (!data.success) {
      throw new Error(data.success === false ? data.message : '自动导入失败')
    }
  },

  getKnowledgeBaseStats: async (): Promise<KnowledgeBaseStats> => {
    const { data } =
      await ragApiClient.get<ApiResponse<KnowledgeBaseStats>>('/knowledge-base/stats')
    if (!data.success || !data.data) throw new Error('获取知识库统计失败')
    return data.data
  },
}
