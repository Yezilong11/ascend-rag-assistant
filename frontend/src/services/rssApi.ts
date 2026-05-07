import { rssApiClient } from './api'
import type {
  Feed,
  Category,
  Tag,
  Article,
  RSSStats,
  SystemStatus,
  ArticleFilter,
  ArticleListResponse,
  AIConfig,
  BridgeIngestResult,
  BridgeBatchResult,
} from '@/types/rss'
import type { ApiResponse } from '@/types/api'

export const rssApi = {
  feeds: {
    // 代理路由：Go 服务直接返回裸数据，无需 ApiResponse 解包
    list: async (): Promise<Feed[]> => {
      const { data } = await rssApiClient.get<Feed[]>('/feeds')
      return data
    },

    get: async (id: number): Promise<Feed> => {
      const { data } = await rssApiClient.get<Feed>(`/feeds/${id}`)
      return data
    },

    create: async (feed: Partial<Feed>): Promise<Feed> => {
      const { data } = await rssApiClient.post<Feed>('/feeds', feed)
      return data
    },

    update: async (id: number, feed: Partial<Feed>): Promise<Feed> => {
      const { data } = await rssApiClient.put<Feed>(`/feeds/${id}`, feed)
      return data
    },

    delete: async (id: number): Promise<void> => {
      await rssApiClient.delete(`/feeds/${id}`)
    },

    crawl: async (id: number): Promise<void> => {
      await rssApiClient.post(`/feeds/${id}/crawl`)
    },

    crawlAll: async (): Promise<void> => {
      await rssApiClient.post('/feeds/crawl-all')
    },
  },

  articles: {
    // 代理路由：Go 服务直接返回裸数据，无需 ApiResponse 解包
    list: async (filter?: ArticleFilter): Promise<ArticleListResponse> => {
      const { data } = await rssApiClient.get<ArticleListResponse>('/articles', {
        params: filter,
      })
      return data
    },

    get: async (id: number): Promise<Article> => {
      const { data } = await rssApiClient.get<Article>(`/articles/${id}`)
      return data
    },

    markRead: async (id: number): Promise<void> => {
      await rssApiClient.put(`/articles/${id}/read`)
    },

    markAllRead: async (feedId?: number): Promise<void> => {
      await rssApiClient.put('/articles/read-all', null, {
        params: feedId ? { feed_id: feedId } : undefined,
      })
    },

    delete: async (id: number): Promise<void> => {
      await rssApiClient.delete(`/articles/${id}`)
    },
  },

  categories: {
    // 代理路由：Go 服务直接返回裸数据，无需 ApiResponse 解包
    list: async (): Promise<Category[]> => {
      const { data } = await rssApiClient.get<Category[]>('/categories')
      return data
    },

    create: async (category: Partial<Category>): Promise<Category> => {
      const { data } = await rssApiClient.post<Category>('/categories', category)
      return data
    },

    update: async (id: number, category: Partial<Category>): Promise<Category> => {
      const { data } = await rssApiClient.put<Category>(`/categories/${id}`, category)
      return data
    },

    delete: async (id: number): Promise<void> => {
      await rssApiClient.delete(`/categories/${id}`)
    },

    reorder: async (ids: number[]): Promise<void> => {
      await rssApiClient.put('/categories/reorder', { ids })
    },
  },

  tags: {
    // 代理路由：Go 服务直接返回裸数据，无需 ApiResponse 解包
    list: async (): Promise<Tag[]> => {
      const { data } = await rssApiClient.get<Tag[]>('/tags')
      return data
    },

    create: async (tag: Partial<Tag>): Promise<Tag> => {
      const { data } = await rssApiClient.post<Tag>('/tags', tag)
      return data
    },

    delete: async (id: number): Promise<void> => {
      await rssApiClient.delete(`/tags/${id}`)
    },
  },

  ai: {
    // AI config 代理路由：Go 服务直接返回裸数据
    getConfig: async (): Promise<AIConfig> => {
      const { data } = await rssApiClient.get<AIConfig>('/ai/config')
      return data
    },

    updateConfig: async (config: Partial<AIConfig>): Promise<AIConfig> => {
      const { data } = await rssApiClient.put<AIConfig>('/ai/config', config)
      return data
    },

    // 修复路径：/ai/test-connection → /ai/test（与 Python 后端 routes.py 一致）
    testConnection: async (): Promise<boolean> => {
      const { data } = await rssApiClient.post<{ connected: boolean }>('/ai/test')
      return data.connected
    },

    // 修复路径：/ai/analyze/${articleId} → /articles/${articleId}/analyze（与 Python 后端 routes.py 一致）
    analyzeArticle: async (articleId: number): Promise<void> => {
      await rssApiClient.post(`/articles/${articleId}/analyze`)
    },

    // 修复路径：/ai/analyze-all → /articles/analyze-all（与 Python 后端 routes.py 一致）
    analyzeAll: async (): Promise<void> => {
      await rssApiClient.post('/articles/analyze-all')
    },
  },

  system: {
    // 代理路由：Go 服务直接返回裸数据，无需 ApiResponse 解包
    getStats: async (): Promise<RSSStats> => {
      const { data } = await rssApiClient.get<RSSStats>('/system/stats')
      return data
    },

    getStatus: async (): Promise<SystemStatus> => {
      const { data } = await rssApiClient.get<SystemStatus>('/system/status')
      return data
    },
  },

  bridge: {
    // Bridge 路由：Python 后端手动包装为 { success, data } 格式，需要 ApiResponse 解包

    // 修复路径：/bridge/ingest/article/ → /bridge/ingest-article/（与 Python 后端 routes.py 一致）
    ingestArticle: async (articleId: number): Promise<BridgeIngestResult> => {
      const { data } = await rssApiClient.post<ApiResponse<BridgeIngestResult>>(
        `/bridge/ingest-article/${articleId}`,
      )
      if (!data.success || !data.data) throw new Error('导入文章到知识库失败')
      return data.data
    },

    // 修复路径：/bridge/ingest/feed/ → /bridge/ingest-feed/（与 Python 后端 routes.py 一致）
    ingestFeed: async (feedId: number): Promise<BridgeBatchResult> => {
      const { data } = await rssApiClient.post<ApiResponse<BridgeBatchResult>>(
        `/bridge/ingest-feed/${feedId}`,
      )
      if (!data.success || !data.data) throw new Error('导入RSS源文章到知识库失败')
      return data.data
    },

    // 修复路径：/bridge/ingest/unread → /bridge/ingest-all-unread（与 Python 后端 routes.py 一致）
    ingestAllUnread: async (): Promise<BridgeBatchResult> => {
      const { data } = await rssApiClient.post<ApiResponse<BridgeBatchResult>>(
        '/bridge/ingest-all-unread',
      )
      if (!data.success || !data.data) throw new Error('导入未读文章到知识库失败')
      return data.data
    },

    getStatus: async (): Promise<{ bridge_enabled: boolean; last_ingest?: string }> => {
      const { data } = await rssApiClient.get<
        ApiResponse<{ bridge_enabled: boolean; last_ingest?: string }>
      >('/bridge/status')
      if (!data.success || !data.data) throw new Error('获取Bridge状态失败')
      return data.data
    },
  },

  health: {
    // Health 路由：Python 后端手动包装为 { success, data } 格式，需要 ApiResponse 解包
    check: async (): Promise<{ status: string; timestamp: string }> => {
      const { data } = await rssApiClient.get<ApiResponse<{ status: string; timestamp: string }>>(
        '/health',
      )
      if (!data.success || !data.data) throw new Error('健康检查失败')
      return data.data
    },
  },
}
