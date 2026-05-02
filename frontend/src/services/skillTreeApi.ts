import { skillTreeApiClient } from './api'
import type {
  SkillTree,
  SkillTreeSummary,
  SkillNode,
  LearningPath,
  CreateSkillTreeRequest,
  AddSkillRequest,
  AddRelationRequest,
  AddResourceRequest,
  GeneratedPathSummary,
} from '@/types/skillTree'
import type { ApiResponse } from '@/types/api'

export const skillTreeApi = {
  list: async (): Promise<SkillTreeSummary[]> => {
    const { data } = await skillTreeApiClient.get<ApiResponse<SkillTreeSummary[]>>('/')
    if (!data.success || !data.data) throw new Error('获取技能树列表失败')
    return data.data
  },

  get: async (skillTreeId: string): Promise<SkillTree> => {
    const { data } = await skillTreeApiClient.get<ApiResponse<SkillTree>>(`/${skillTreeId}`)
    if (!data.success || !data.data) throw new Error('获取技能树详情失败')
    return data.data
  },

  create: async (request: CreateSkillTreeRequest): Promise<SkillTree> => {
    const { data } = await skillTreeApiClient.post<ApiResponse<SkillTree>>('/', request)
    if (!data.success || !data.data) throw new Error('创建技能树失败')
    return data.data
  },

  delete: async (skillTreeId: string): Promise<void> => {
    const { data } = await skillTreeApiClient.delete<ApiResponse<null>>(`/${skillTreeId}`)
    if (!data.success) {
      throw new Error(data.success === false ? data.message : '删除技能树失败')
    }
  },

  addSkill: async (skillTreeId: string, request: AddSkillRequest): Promise<SkillNode> => {
    const { data } = await skillTreeApiClient.post<ApiResponse<SkillNode>>(
      `/${skillTreeId}/skills`,
      request,
    )
    if (!data.success || !data.data) throw new Error('添加技能失败')
    return data.data
  },

  addRelation: async (skillTreeId: string, request: AddRelationRequest): Promise<void> => {
    const { data } = await skillTreeApiClient.post<ApiResponse<null>>(
      `/${skillTreeId}/skills/relation`,
      request,
    )
    if (!data.success) {
      throw new Error(data.success === false ? data.message : '建立技能关系失败')
    }
  },

  addResource: async (
    skillTreeId: string,
    skillId: string,
    request: AddResourceRequest,
  ): Promise<void> => {
    const { data } = await skillTreeApiClient.post<ApiResponse<null>>(
      `/${skillTreeId}/skills/${skillId}/resources`,
      request,
    )
    if (!data.success) {
      throw new Error(data.success === false ? data.message : '添加学习资源失败')
    }
  },

  updateCompletion: async (
    skillTreeId: string,
    skillId: string,
    completionRate: number,
  ): Promise<void> => {
    const { data } = await skillTreeApiClient.put<ApiResponse<null>>(
      `/${skillTreeId}/skills/${skillId}/completion`,
      null,
      { params: { completion_rate: completionRate } },
    )
    if (!data.success) {
      throw new Error(data.success === false ? data.message : '更新完成率失败')
    }
  },

  generatePaths: async (skillTreeId: string): Promise<GeneratedPathSummary[]> => {
    const { data } = await skillTreeApiClient.post<ApiResponse<GeneratedPathSummary[]>>(
      `/${skillTreeId}/paths/generate`,
    )
    if (!data.success || !data.data) throw new Error('生成学习路径失败')
    return data.data
  },

  getLearningPaths: async (skillTreeId: string): Promise<LearningPath[]> => {
    const detail = await skillTreeApi.get(skillTreeId)
    return Object.values(detail.learning_paths)
  },
}
