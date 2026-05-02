import axios, { AxiosInstance, AxiosError } from 'axios'
import type {
  ApiResponse,
  ChatRequest,
  ChatResponse,
  StreamChatResponse,
  SkillTree,
  CreateSkillTreeRequest,
  AddSkillRequest,
  EstablishRelationRequest,
  Document,
  UploadDocumentResponse,
  KnowledgeBaseStatus,
  Model,
  Reranker,
  SystemStatus,
} from '../types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const RAG_API_BASE_URL = import.meta.env.VITE_RAG_API_BASE_URL || 'http://localhost:8001'

class ApiService {
  private apiClient: AxiosInstance
  private ragClient: AxiosInstance

  constructor() {
    this.apiClient = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.ragClient = axios.create({
      baseURL: RAG_API_BASE_URL,
      timeout: 60000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    this.apiClient.interceptors.request.use(
      (config) => {
        console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`)
        return config
      },
      (error) => {
        console.error('[API Request Error]', error)
        return Promise.reject(error)
      }
    )

    this.apiClient.interceptors.response.use(
      (response) => {
        return response
      },
      (error: AxiosError) => {
        console.error('[API Response Error]', error.response?.data || error.message)
        return Promise.reject(error)
      }
    )
  }

  async getSystemStatus(): Promise<ApiResponse<SystemStatus>> {
    const response = await this.apiClient.get('/')
    return response.data
  }

  async getAvailableModels(): Promise<ApiResponse<Record<string, Model>>> {
    const response = await this.apiClient.get('/api/rag/models')
    return response.data
  }

  async getAvailableRerankers(): Promise<ApiResponse<Record<string, Reranker>>> {
    const response = await this.apiClient.get('/api/rag/rerankers')
    return response.data
  }

  async loadModel(modelKey: string): Promise<ApiResponse<{ success: boolean }>> {
    const response = await this.ragClient.post('/api/rag/model/load', { model_key: modelKey })
    return response.data
  }

  async chat(request: ChatRequest): Promise<ApiResponse<ChatResponse>> {
    const response = await this.ragClient.post<ApiResponse<ChatResponse>>('/api/rag/chat', request)
    return response.data
  }

  async chatStream(
    request: ChatRequest,
    onChunk: (chunk: StreamChatResponse) => void,
    onError: (error: Error) => void
  ): Promise<void> {
    try {
      const response = await fetch(`${RAG_API_BASE_URL}/api/rag/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('Response body is not readable')
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6)) as StreamChatResponse
              onChunk(data)
              if (data.done) {
                return
              }
            } catch (e) {
              console.error('Failed to parse SSE data:', e)
            }
          }
        }
      }
    } catch (error) {
      onError(error as Error)
    }
  }

  async getKnowledgeBaseStatus(): Promise<ApiResponse<KnowledgeBaseStatus>> {
    const response = await this.ragClient.get('/api/rag/status')
    return response.data
  }

  async uploadDocument(file: File): Promise<ApiResponse<UploadDocumentResponse>> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await this.ragClient.post<ApiResponse<UploadDocumentResponse>>(
      '/api/rag/ingest',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  }

  async listSkillTrees(): Promise<ApiResponse<SkillTree[]>> {
    const response = await this.apiClient.get<ApiResponse<SkillTree[]>>('/api/skill-tree/')
    return response.data
  }

  async getSkillTree(skillTreeId: string): Promise<ApiResponse<SkillTree>> {
    const response = await this.apiClient.get<ApiResponse<SkillTree>>(`/api/skill-tree/${skillTreeId}`)
    return response.data
  }

  async createSkillTree(request: CreateSkillTreeRequest): Promise<ApiResponse<SkillTree>> {
    const response = await this.apiClient.post<ApiResponse<SkillTree>>('/api/skill-tree/', request)
    return response.data
  }

  async deleteSkillTree(skillTreeId: string): Promise<ApiResponse<{ success: boolean }>> {
    const response = await this.apiClient.delete<ApiResponse<{ success: boolean }>>(
      `/api/skill-tree/${skillTreeId}`
    )
    return response.data
  }

  async addSkill(
    skillTreeId: string,
    request: AddSkillRequest
  ): Promise<ApiResponse<{ success: boolean }>> {
    const response = await this.apiClient.post<ApiResponse<{ success: boolean }>>(
      `/api/skill-tree/${skillTreeId}/skills`,
      request
    )
    return response.data
  }

  async establishSkillRelation(
    skillTreeId: string,
    request: EstablishRelationRequest
  ): Promise<ApiResponse<{ success: boolean }>> {
    const response = await this.apiClient.post<ApiResponse<{ success: boolean }>>(
      `/api/skill-tree/${skillTreeId}/skills/relation`,
      request
    )
    return response.data
  }

  async generateLearningPaths(
    skillTreeId: string
  ): Promise<ApiResponse<{ success: boolean }>> {
    const response = await this.apiClient.post<ApiResponse<{ success: boolean }>>(
      `/api/skill-tree/${skillTreeId}/paths/generate`
    )
    return response.data
  }

  async updateSkillCompletion(
    skillTreeId: string,
    skillId: string,
    completionRate: number
  ): Promise<ApiResponse<{ success: boolean }>> {
    const response = await this.apiClient.put<ApiResponse<{ success: boolean }>>(
      `/api/skill-tree/${skillTreeId}/skills/${skillId}/completion`,
      null,
      {
        params: { completion_rate: completionRate },
      }
    )
    return response.data
  }
}

export const apiService = new ApiService()
export default apiService
