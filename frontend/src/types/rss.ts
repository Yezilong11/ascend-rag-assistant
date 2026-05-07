export interface Feed {
  id: number
  name: string
  url: string
  description?: string
  category_id?: number
  crawl_interval: number
  last_crawl?: string
  next_crawl?: string
  status: string
  error_message?: string
  category?: Category
}

export interface Category {
  id: number
  name: string
  icon?: string
  sort_order: number
}

export interface Tag {
  id: number
  name: string
  color?: string
}

export interface Article {
  id: number
  feed_id: number
  title: string
  link: string
  content: string
  content_hash?: string
  summary?: string
  author?: string
  published_at?: string
  crawled_at?: string
  read_status: number
  feed?: Feed
  tags?: Tag[]
}

export interface RSSStats {
  feeds_count: number
  articles_count: number
  today_articles: number
  unread_count: number
}

export interface SystemStatus {
  database: string
  uptime: number
  version: string
}

export interface ArticleFilter {
  feed_id?: number
  category_id?: number
  read_status?: number
  page?: number
  limit?: number
}

export interface ArticleListResponse {
  data: Article[]
  total: number
}

export interface AIConfig {
  host: string
  model: string
  timeout: number
  enabled: boolean
}

export interface BridgeIngestResult {
  success: boolean
  message: string
  article_id?: number
  chunks_count: number
}

export interface BridgeBatchResult {
  success: boolean
  total: number
  success_count: number
  failed_count: number
  errors: string[]
}
