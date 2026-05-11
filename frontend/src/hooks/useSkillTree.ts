import { useCallback } from 'react'
import { useSkillTreeStore } from '@/stores/skillTreeStore'
import { skillTreeApi } from '@/services/skillTreeApi'
import type {
  CreateSkillTreeRequest,
  AddSkillRequest,
  AddRelationRequest,
  AddResourceRequest,
} from '@/types/skillTree'

export function useSkillTree() {
  const skillTreeList = useSkillTreeStore((s) => s.skillTreeList)
  const currentSkillTree = useSkillTreeStore((s) => s.currentSkillTree)
  const selectedSkillNode = useSkillTreeStore((s) => s.selectedSkillNode)
  const learningPaths = useSkillTreeStore((s) => s.learningPaths)
  const isLoading = useSkillTreeStore((s) => s.isLoading)

  const setSkillTreeList = useSkillTreeStore((s) => s.setSkillTreeList)
  const setCurrentSkillTree = useSkillTreeStore((s) => s.setCurrentSkillTree)
  const setSelectedSkillNode = useSkillTreeStore((s) => s.setSelectedSkillNode)
  const setLearningPaths = useSkillTreeStore((s) => s.setLearningPaths)
  const setLoading = useSkillTreeStore((s) => s.setLoading)
  const removeSkillTreeFromList = useSkillTreeStore((s) => s.removeSkillTreeFromList)

  const fetchList = useCallback(async () => {
    setLoading(true)
    try {
      const list = await skillTreeApi.list()
      setSkillTreeList(list)
    } finally {
      setLoading(false)
    }
  }, [setSkillTreeList, setLoading])

  const fetchDetail = useCallback(
    async (id: string) => {
      setLoading(true)
      try {
        const tree = await skillTreeApi.get(id)
        setCurrentSkillTree(tree)
        setLearningPaths(Object.values(tree.learning_paths))
      } finally {
        setLoading(false)
      }
    },
    [setCurrentSkillTree, setLearningPaths, setLoading],
  )

  const create = useCallback(
    async (request: CreateSkillTreeRequest) => {
      const tree = await skillTreeApi.create(request)
      await fetchList()
      return tree
    },
    [fetchList],
  )

  const remove = useCallback(
    async (id: string) => {
      await skillTreeApi.delete(id)
      removeSkillTreeFromList(id)
    },
    [removeSkillTreeFromList],
  )

  const addSkill = useCallback(
    async (skillTreeId: string, request: AddSkillRequest) => {
      const skill = await skillTreeApi.addSkill(skillTreeId, request)
      await fetchDetail(skillTreeId)
      return skill
    },
    [fetchDetail],
  )

  const addRelation = useCallback(
    async (skillTreeId: string, request: AddRelationRequest) => {
      await skillTreeApi.addRelation(skillTreeId, request)
      await fetchDetail(skillTreeId)
    },
    [fetchDetail],
  )

  const addResource = useCallback(
    async (skillTreeId: string, skillId: string, request: AddResourceRequest) => {
      await skillTreeApi.addResource(skillTreeId, skillId, request)
      await fetchDetail(skillTreeId)
    },
    [fetchDetail],
  )

  const updateCompletion = useCallback(
    async (skillTreeId: string, skillId: string, rate: number) => {
      await skillTreeApi.updateCompletion(skillTreeId, skillId, rate)
      try {
        const tree = await skillTreeApi.get(skillTreeId)
        setCurrentSkillTree(tree)
        setLearningPaths(Object.values(tree.learning_paths))
      } catch {}
    },
    [setCurrentSkillTree, setLearningPaths],
  )

  const generatePaths = useCallback(
    async (skillTreeId: string) => {
      const paths = await skillTreeApi.generatePaths(skillTreeId)
      await fetchDetail(skillTreeId)
      return paths
    },
    [fetchDetail],
  )

  return {
    skillTreeList,
    currentSkillTree,
    selectedSkillNode,
    learningPaths,
    isLoading,
    fetchList,
    fetchDetail,
    create,
    remove,
    addSkill,
    addRelation,
    addResource,
    updateCompletion,
    generatePaths,
    setSelectedSkillNode,
    setCurrentSkillTree,
  }
}
