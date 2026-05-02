export type SkillLevel = 'beginner' | 'intermediate' | 'advanced' | 'expert'
export type SkillType = 'technical' | 'theoretical' | 'practical' | 'competition'
export type RelationType = 'prerequisite' | 'related' | 'advanced'

export interface SkillNode {
  id: string
  name: string
  description: string
  level: SkillLevel
  type: SkillType
  parent_ids: string[]
  child_ids: string[]
  related_ids: string[]
  resources: Record<string, unknown>[]
  learning_time: number
  completion_rate: number
}

export interface LearningPath {
  path_id: string
  skill_ids: string[]
  estimated_time: number
  difficulty: SkillLevel
}

export interface SkillTree {
  id: string
  name: string
  description: string
  version: string
  root_nodes: string[]
  skill_nodes: Record<string, SkillNode>
  learning_paths: Record<string, LearningPath>
  completion_rate: number
}

export interface SkillTreeSummary {
  id: string
  name: string
  description: string
  version: string
  skill_count: number
  completion_rate: number
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
  learning_time?: number
}

export interface AddRelationRequest {
  source_skill_id: string
  target_skill_id: string
  relation_type: RelationType
}

export interface AddResourceRequest {
  name: string
  url?: string
  type?: string
  description?: string
}

export interface GeneratedPathSummary {
  path_id: string
  skill_count: number
  estimated_time: number
  difficulty: SkillLevel
}
