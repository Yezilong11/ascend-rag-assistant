import { create } from 'zustand'
import type {
  Feed,
  Article,
  Category,
  Tag,
  RSSStats,
  SystemStatus,
  ArticleFilter,
} from '@/types/rss'
import { rssApi } from '@/services/rssApi'

interface RSSStore {
  feeds: Feed[]
  articles: Article[]
  categories: Category[]
  tags: Tag[]
  stats: RSSStats | null
  systemStatus: SystemStatus | null
  loading: boolean
  articleTotal: number

  fetchFeeds: () => Promise<void>
  addFeed: (feed: Partial<Feed>) => Promise<void>
  updateFeed: (id: number, feed: Partial<Feed>) => Promise<void>
  deleteFeed: (id: number) => Promise<void>
  crawlFeed: (id: number) => Promise<void>
  crawlAllFeeds: () => Promise<void>
  fetchArticles: (filter?: ArticleFilter) => Promise<void>
  fetchCategories: () => Promise<void>
  addCategory: (category: Partial<Category>) => Promise<void>
  fetchTags: () => Promise<void>
  addTag: (tag: Partial<Tag>) => Promise<void>
  fetchStats: () => Promise<void>
  fetchSystemStatus: () => Promise<void>
  checkHealth: () => Promise<void>
}

export const useRSSStore = create<RSSStore>((set) => ({
  feeds: [],
  articles: [],
  categories: [],
  tags: [],
  stats: null,
  systemStatus: null,
  loading: false,
  articleTotal: 0,

  fetchFeeds: async () => {
    set({ loading: true })
    try {
      const feeds = await rssApi.feeds.list()
      set({ feeds })
    } finally {
      set({ loading: false })
    }
  },

  addFeed: async (feed) => {
    const created = await rssApi.feeds.create(feed)
    set((state) => ({ feeds: [...state.feeds, created] }))
  },

  updateFeed: async (id, feed) => {
    const updated = await rssApi.feeds.update(id, feed)
    set((state) => ({
      feeds: state.feeds.map((f) => (f.id === id ? updated : f)),
    }))
  },

  deleteFeed: async (id) => {
    await rssApi.feeds.delete(id)
    set((state) => ({ feeds: state.feeds.filter((f) => f.id !== id) }))
  },

  crawlFeed: async (id) => {
    await rssApi.feeds.crawl(id)
  },

  crawlAllFeeds: async () => {
    await rssApi.feeds.crawlAll()
  },

  fetchArticles: async (filter) => {
    set({ loading: true })
    try {
      const result = await rssApi.articles.list(filter)
      set({ articles: result.data, articleTotal: result.total })
    } finally {
      set({ loading: false })
    }
  },

  fetchCategories: async () => {
    const categories = await rssApi.categories.list()
    set({ categories })
  },

  addCategory: async (category) => {
    const created = await rssApi.categories.create(category)
    set((state) => ({ categories: [...state.categories, created] }))
  },

  fetchTags: async () => {
    const tags = await rssApi.tags.list()
    set({ tags })
  },

  addTag: async (tag) => {
    const created = await rssApi.tags.create(tag)
    set((state) => ({ tags: [...state.tags, created] }))
  },

  fetchStats: async () => {
    const stats = await rssApi.system.getStats()
    set({ stats })
  },

  fetchSystemStatus: async () => {
    const systemStatus = await rssApi.system.getStatus()
    set({ systemStatus })
  },

  checkHealth: async () => {
    await rssApi.health.check()
  },
}))
