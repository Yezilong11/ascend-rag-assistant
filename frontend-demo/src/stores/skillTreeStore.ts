import { create } from 'zustand'
import type { SkillTree, SkillNode, LearningPath, SkillLevel, SkillType } from '../types'
import { apiService } from '../services/api'

interface SkillTreeState {
  skillTrees: SkillTree[]
  selectedSkillTree: SkillTree | null
  isLoading: boolean
  error: string | null

  setSkillTrees: (skillTrees: SkillTree[]) => void
  setSelectedSkillTree: (skillTree: SkillTree | null) => void
  setLoading: (isLoading: boolean) => void
  setError: (error: string | null) => void

  fetchSkillTrees: () => Promise<void>
  fetchSkillTreeDetail: (skillTreeId: string) => Promise<void>
  createSkillTree: (name: string, description: string) => Promise<boolean>
  deleteSkillTree: (skillTreeId: string) => Promise<boolean>
  addSkill: (
    skillTreeId: string,
    name: string,
    description: string,
    level: SkillLevel,
    skillType: SkillType,
    learningTime: number
  ) => Promise<boolean>
  establishRelation: (
    skillTreeId: string,
    sourceSkillId: string,
    targetSkillId: string,
    relationType: 'prerequisite' | 'related' | 'advanced'
  ) => Promise<boolean>
  generateLearningPaths: (skillTreeId: string) => Promise<boolean>
  updateSkillCompletion: (
    skillTreeId: string,
    skillId: string,
    completionRate: number
  ) => Promise<boolean>
}

export const useSkillTreeStore = create<SkillTreeState>((set, get) => ({
  skillTrees: [],
  selectedSkillTree: null,
  isLoading: false,
  error: null,

  setSkillTrees: (skillTrees) => set({ skillTrees }),

  setSelectedSkillTree: (skillTree) => set({ selectedSkillTree: skillTree }),

  setLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error }),

  fetchSkillTrees: async () => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiService.listSkillTrees()
      if (response.code === 0 && response.data) {
        set({ skillTrees: response.data })
      } else {
        set({ error: response.message || 'Failed to fetch skill trees' })
      }
    } catch (error) {
      set({ error: (error as Error).message })
    } finally {
      set({ isLoading: false })
    }
  },

  fetchSkillTreeDetail: async (skillTreeId) => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiService.getSkillTree(skillTreeId)
      if (response.code === 0 && response.data) {
        set({ selectedSkillTree: response.data })
      } else {
        set({ error: response.message || 'Failed to fetch skill tree detail' })
      }
    } catch (error) {
      set({ error: (error as Error).message })
    } finally {
      set({ isLoading: false })
    }
  },

  createSkillTree: async (name, description) => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiService.createSkillTree({ name, description })
      if (response.code === 0) {
        await get().fetchSkillTrees()
        return true
      } else {
        set({ error: response.message || 'Failed to create skill tree' })
        return false
      }
    } catch (error) {
      set({ error: (error as Error).message })
      return false
    } finally {
      set({ isLoading: false })
    }
  },

  deleteSkillTree: async (skillTreeId) => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiService.deleteSkillTree(skillTreeId)
      if (response.code === 0) {
        set({ selectedSkillTree: null })
        await get().fetchSkillTrees()
        return true
      } else {
        set({ error: response.message || 'Failed to delete skill tree' })
        return false
      }
    } catch (error) {
      set({ error: (error as Error).message })
      return false
    } finally {
      set({ isLoading: false })
    }
  },

  addSkill: async (skillTreeId, name, description, level, skillType, learningTime) => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiService.addSkill(skillTreeId, {
        name,
        description,
        level,
        skill_type: skillType,
        learning_time: learningTime,
      })
      if (response.code === 0) {
        await get().fetchSkillTreeDetail(skillTreeId)
        return true
      } else {
        set({ error: response.message || 'Failed to add skill' })
        return false
      }
    } catch (error) {
      set({ error: (error as Error).message })
      return false
    } finally {
      set({ isLoading: false })
    }
  },

  establishRelation: async (skillTreeId, sourceSkillId, targetSkillId, relationType) => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiService.establishSkillRelation(skillTreeId, {
        source_skill_id: sourceSkillId,
        target_skill_id: targetSkillId,
        relation_type: relationType,
      })
      if (response.code === 0) {
        await get().fetchSkillTreeDetail(skillTreeId)
        return true
      } else {
        set({ error: response.message || 'Failed to establish relation' })
        return false
      }
    } catch (error) {
      set({ error: (error as Error).message })
      return false
    } finally {
      set({ isLoading: false })
    }
  },

  generateLearningPaths: async (skillTreeId) => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiService.generateLearningPaths(skillTreeId)
      if (response.code === 0) {
        await get().fetchSkillTreeDetail(skillTreeId)
        return true
      } else {
        set({ error: response.message || 'Failed to generate learning paths' })
        return false
      }
    } catch (error) {
      set({ error: (error as Error).message })
      return false
    } finally {
      set({ isLoading: false })
    }
  },

  updateSkillCompletion: async (skillTreeId, skillId, completionRate) => {
    try {
      const response = await apiService.updateSkillCompletion(skillTreeId, skillId, completionRate)
      if (response.code === 0) {
        await get().fetchSkillTreeDetail(skillTreeId)
        return true
      } else {
        set({ error: response.message || 'Failed to update skill completion' })
        return false
      }
    } catch (error) {
      set({ error: (error as Error).message })
      return false
    }
  },
}))
