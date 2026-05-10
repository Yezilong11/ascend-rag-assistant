export interface RAGStatus {
  engine_loaded: boolean
  model_key: string
  model_name: string
  reranker_enabled: boolean
  reranker_model: string
  knowledge_base_ready: boolean
  available_models: Record<string, ModelInfo>
  available_rerankers: Record<string, RerankerInfo>
}

export interface ModelInfo {
  name: string
  description: string
}

export interface RerankerInfo {
  name: string
  description: string
  size: string
}

export interface ModelLoadRequest {
  model_key: string
  model_dir?: string
  use_reranker?: boolean
  reranker_model?: string
  reranker_top_k?: number
  initial_retrieval_k?: number
}

export interface ChatRequest {
  question: string
}

export interface ChatResponse {
  answer: string
  sources: SourceData[]
}

export interface SourceData {
  content: string
  source: string
}

export interface KnowledgeBaseStats {
  document_count: number
  chunk_count: number
  image_chunk_count: number
  status: string
}
