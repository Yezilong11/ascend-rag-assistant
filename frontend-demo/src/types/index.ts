export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data?: T
}

export interface PaginatedResponse<T> {
  code: number
  message: string
  data: {
    items: T[]
    total: number
    page: number
    page_size: number
  }
}

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  sources?: Source[]
  timestamp: number
}

export interface Source {
  content: string
  source: string
  score?: number
}

export interface ChatRequest {
  question: string
  model_key?: string
  use_reranker?: boolean
  session_id?: string
}

export interface ChatResponse {
  answer: string
  sources: Source[]
  session_id: string
}

export interface StreamChatResponse {
  token: string
  done: boolean
  sources?: Source[]
}

export interface SkillTree {
  id: string
  name: string
  description: string
  version: string
  created_at: string
  updated_at: string
  root_nodes: string[]
  skill_nodes: Record<string, SkillNode>
  learning_paths: Record<string, LearningPath>
}

export interface SkillNode {
  id: string
  name: string
  description: string
  level: SkillLevel
  skill_type: SkillType
  parent_ids: string[]
  child_ids: string[]
  related_ids: string[]
  resources: LearningResource[]
  prerequisites: SkillRelation[]
  learning_time: number
  completion_rate: number
}

export type SkillLevel = 'beginner' | 'intermediate' | 'advanced' | 'expert'

export type SkillType = 'technical' | 'theoretical' | 'practical' | 'competition'

export interface SkillRelation {
  source_skill_id: string
  target_skill_id: string
  relation_type: 'prerequisite' | 'related' | 'advanced'
  weight: number
}

export interface LearningPath {
  path_id: string
  skill_ids: string[]
  estimated_time: number
  difficulty: SkillLevel
}

export interface LearningResource {
  id: string
  title: string
  url?: string
  description?: string
  type: 'video' | 'article' | 'course' | 'documentation'
}

export interface CreateSkillTreeRequest {
  name: string
  description: string
}

export interface AddSkillRequest {
  name: string
  description: string
  level: SkillLevel
  skill_type: SkillType
  learning_time: number
}

export interface EstablishRelationRequest {
  source_skill_id: string
  target_skill_id: string
  relation_type: 'prerequisite' | 'related' | 'advanced'
}

export interface Document {
  id: string
  file_name: string
  file_type: 'pdf' | 'txt' | 'md'
  doc_type: DocType
  uploaded_at: string
  size: number
  chunk_count?: number
}

export type DocType =
  | 'registration'
  | 'tech_doc'
  | 'rules'
  | 'history'
  | 'scoring'
  | 'faq'
  | 'unknown'

export interface UploadDocumentResponse {
  success: boolean
  file_name: string
  chunk_count: number
  message: string
}

export interface KnowledgeBaseStatus {
  total_documents: number
  total_chunks: number
  last_updated: string
  embedding_model: string
}

export interface Model {
  key: string
  name: string
  description: string
  repo_id: string
  size?: string
}

export interface Reranker {
  key: string
  name: string
  description: string
  repo_id: string
  size: string
}

export interface ModelConfig {
  model_key: string
  model_dir: string
  use_reranker: boolean
  reranker_key: string
  reranker_top_k: number
  initial_retrieval_k: number
}

export interface AppSettings {
  theme: 'light' | 'dark' | 'auto'
  language: 'zh-CN' | 'en-US'
  model_config: ModelConfig
  api_base_url: string
  rag_api_base_url: string
}

export interface SystemStatus {
  api_connected: boolean
  rag_connected: boolean
  knowledge_base_ready: boolean
  model_loaded: boolean
  loaded_model?: string
}
