import { ragApiClient } from './api'
import type { KnowledgeBaseStats } from '@/types/rag'
import type { ApiResponse } from '@/types/api'

export const knowledgeBaseApi = {
  getStats: async (): Promise<KnowledgeBaseStats> => {
    const { data } =
      await ragApiClient.get<ApiResponse<KnowledgeBaseStats>>('/knowledge-base/stats')
    if (!data.success || !data.data) throw new Error('获取知识库统计失败')
    return data.data
  },

  autoIngest: async (): Promise<void> => {
    const { data } = await ragApiClient.post<ApiResponse<null>>('/knowledge-base/auto-ingest')
    if (!data.success) {
      throw new Error(data.success === false ? data.message : '自动导入失败')
    }
  },

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
}
