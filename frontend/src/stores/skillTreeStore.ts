import { create } from 'zustand'
import type { SkillTree, SkillTreeSummary, SkillNode, LearningPath } from '@/types/skillTree'

interface SkillTreeStore {
  skillTreeList: SkillTreeSummary[]
  currentSkillTree: SkillTree | null
  selectedSkillNode: SkillNode | null
  learningPaths: LearningPath[]
  isLoading: boolean

  setSkillTreeList: (list: SkillTreeSummary[]) => void
  setCurrentSkillTree: (tree: SkillTree | null) => void
  setSelectedSkillNode: (node: SkillNode | null) => void
  setLearningPaths: (paths: LearningPath[]) => void
  setLoading: (loading: boolean) => void
  removeSkillTreeFromList: (id: string) => void
  updateSkillTreeInList: (updated: SkillTreeSummary) => void
}

export const useSkillTreeStore = create<SkillTreeStore>((set) => ({
  skillTreeList: [],
  currentSkillTree: null,
  selectedSkillNode: null,
  learningPaths: [],
  isLoading: false,

  setSkillTreeList: (list) => set({ skillTreeList: list }),

  setCurrentSkillTree: (tree) => set({ currentSkillTree: tree }),

  setSelectedSkillNode: (node) => set({ selectedSkillNode: node }),

  setLearningPaths: (paths) => set({ learningPaths: paths }),

  setLoading: (loading) => set({ isLoading: loading }),

  removeSkillTreeFromList: (id) =>
    set((state) => ({
      skillTreeList: state.skillTreeList.filter((t) => t.id !== id),
      currentSkillTree: state.currentSkillTree?.id === id ? null : state.currentSkillTree,
    })),

  updateSkillTreeInList: (updated) =>
    set((state) => ({
      skillTreeList: state.skillTreeList.map((t) => (t.id === updated.id ? updated : t)),
    })),
}))
