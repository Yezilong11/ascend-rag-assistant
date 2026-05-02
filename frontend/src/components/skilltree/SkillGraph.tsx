import React, { useCallback, useMemo } from 'react'
import { ReactFlow, Background, Controls, MiniMap } from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import type { SkillTree, SkillNode } from '@/types/skillTree'
import { SKILL_LEVEL_MAP } from '@/utils/constants'
import type { Node, Edge } from '@xyflow/react'

const levelColorMap: Record<string, string> = {
  beginner: '#00ff88',
  intermediate: '#00d4ff',
  advanced: '#ffb800',
  expert: '#ff2d78',
}

const levelGlowMap: Record<string, string> = {
  beginner: '0 0 12px rgba(0, 255, 136, 0.4)',
  intermediate: '0 0 12px rgba(0, 212, 255, 0.4)',
  advanced: '0 0 12px rgba(255, 184, 0, 0.4)',
  expert: '0 0 12px rgba(255, 45, 120, 0.4)',
}

interface SkillGraphProps {
  skillTree: SkillTree
  onNodeClick?: (node: SkillNode) => void
}

const SkillGraph: React.FC<SkillGraphProps> = ({ skillTree, onNodeClick }) => {
  const nodes: Node[] = useMemo(() => {
    const nodeList = Object.values(skillTree.skill_nodes)
    return nodeList.map((skill, index) => {
      const color = levelColorMap[skill.level] ?? '#00d4ff'
      const glow = levelGlowMap[skill.level] ?? levelGlowMap.intermediate!
      return {
        id: skill.id,
        position: { x: (index % 5) * 250, y: Math.floor(index / 5) * 150 },
        data: {
          label: (
            <div style={{ textAlign: 'center', fontSize: 12 }}>
              <div style={{ fontWeight: 700, fontSize: 13 }}>{skill.name}</div>
              <div style={{ color: 'rgba(255,255,255,0.7)', fontSize: 10 }}>
                {SKILL_LEVEL_MAP[skill.level]}
              </div>
            </div>
          ),
        },
        style: {
          background: `linear-gradient(135deg, ${color}22 0%, ${color}11 100%)`,
          color: '#fff',
          border: `1px solid ${color}66`,
          borderRadius: 10,
          fontSize: 12,
          width: 150,
          padding: '6px 10px',
          boxShadow: glow,
        },
      }
    })
  }, [skillTree.skill_nodes])

  const edges: Edge[] = useMemo(() => {
    const edgeList: Edge[] = []
    const skillNodes = Object.values(skillTree.skill_nodes)

    for (const skill of skillNodes) {
      for (const childId of skill.child_ids) {
        edgeList.push({
          id: `${skill.id}-${childId}`,
          source: skill.id,
          target: childId,
          animated: true,
          style: { stroke: '#00d4ff', strokeWidth: 1.5 },
        })
      }
    }

    return edgeList
  }, [skillTree.skill_nodes])

  const handleNodeClick = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      const skillNode = skillTree.skill_nodes[node.id]
      if (skillNode && onNodeClick) {
        onNodeClick(skillNode)
      }
    },
    [skillTree.skill_nodes, onNodeClick],
  )

  return (
    <div
      style={{
        width: '100%',
        height: 500,
        borderRadius: 'var(--radius-md)',
        overflow: 'hidden',
        border: '1px solid var(--border-glass)',
      }}
    >
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodeClick={handleNodeClick}
        fitView
        style={{ background: 'var(--bg-secondary)' }}
      >
        <Background color="rgba(0, 212, 255, 0.06)" gap={20} size={1} />
        <Controls
          style={{
            background: 'var(--bg-glass)',
            border: '1px solid var(--border-glass)',
            borderRadius: 'var(--radius-sm)',
          }}
        />
        <MiniMap
          style={{
            background: 'var(--bg-glass)',
            border: '1px solid var(--border-glass)',
            borderRadius: 'var(--radius-sm)',
          }}
          maskColor="rgba(0, 0, 0, 0.6)"
        />
      </ReactFlow>
    </div>
  )
}

export default SkillGraph
