export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export const RAG_STATUS_POLL_INTERVAL = 2000

export const MAX_FILE_SIZE = 50 * 1024 * 1024

export const SKILL_LEVEL_MAP: Record<string, string> = {
  beginner: '入门',
  intermediate: '进阶',
  advanced: '高级',
  expert: '专家',
}

export const SKILL_TYPE_MAP: Record<string, string> = {
  technical: '技术',
  theoretical: '理论',
  practical: '实践',
  competition: '竞赛',
}

export const RELATION_TYPE_MAP: Record<string, string> = {
  prerequisite: '前置',
  related: '相关',
  advanced: '进阶',
}

export const PREDEFINED_QUESTIONS = [
  '如何报名西门子杯竞赛？',
  '竞赛的评分标准是什么？',
  '需要掌握哪些技术栈？',
  '竞赛有哪些注意事项？',
]
