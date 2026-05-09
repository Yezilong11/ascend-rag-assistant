import React, { useCallback, useMemo, useRef, useState } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Handle,
  Position,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import type { SkillTree, SkillNode, SkillType } from '@/types/skillTree'
import { SKILL_LEVEL_MAP, SKILL_TYPE_MAP } from '@/utils/constants'
import type { Node, Edge, NodeProps } from '@xyflow/react'

const STORAGE_KEY_PREFIX = 'skill-graph-positions-'

const EDGE_COLOR = 'rgba(200, 210, 230, 0.35)'

const levelColorMap: Record<string, string> = {
  beginner: '#00ff88',
  intermediate: '#00d4ff',
  advanced: '#ffb800',
  expert: '#ff2d78',
}

const levelGlowMap: Record<string, string> = {
  beginner: '0 0 12px rgba(0, 255, 136, 0.35), 0 0 28px rgba(0, 255, 136, 0.12)',
  intermediate: '0 0 12px rgba(0, 212, 255, 0.35), 0 0 28px rgba(0, 212, 255, 0.12)',
  advanced: '0 0 12px rgba(255, 184, 0, 0.35), 0 0 28px rgba(255, 184, 0, 0.12)',
  expert: '0 0 12px rgba(255, 45, 120, 0.35), 0 0 28px rgba(255, 45, 120, 0.12)',
}

const levelHoverGlow: Record<string, string> = {
  beginner: '0 0 20px rgba(0, 255, 136, 0.5), 0 0 44px rgba(0, 255, 136, 0.2), 0 0 64px rgba(0, 255, 136, 0.08)',
  intermediate: '0 0 20px rgba(0, 212, 255, 0.5), 0 0 44px rgba(0, 212, 255, 0.2), 0 0 64px rgba(0, 212, 255, 0.08)',
  advanced: '0 0 20px rgba(255, 184, 0, 0.5), 0 0 44px rgba(255, 184, 0, 0.2), 0 0 64px rgba(255, 184, 0, 0.08)',
  expert: '0 0 20px rgba(255, 45, 120, 0.5), 0 0 44px rgba(255, 45, 120, 0.2), 0 0 64px rgba(255, 45, 120, 0.08)',
}

const levelAuraGradient: Record<string, string> = {
  beginner: 'radial-gradient(circle, rgba(0, 255, 136, 0.15) 0%, rgba(0, 255, 136, 0.03) 50%, transparent 70%)',
  intermediate: 'radial-gradient(circle, rgba(0, 212, 255, 0.15) 0%, rgba(0, 212, 255, 0.03) 50%, transparent 70%)',
  advanced: 'radial-gradient(circle, rgba(255, 184, 0, 0.15) 0%, rgba(255, 184, 0, 0.03) 50%, transparent 70%)',
  expert: 'radial-gradient(circle, rgba(255, 45, 120, 0.15) 0%, rgba(255, 45, 120, 0.03) 50%, transparent 70%)',
}

const TechnicalIcon: React.FC<{ color: string; size?: number }> = ({ color, size = 24 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 15a3 3 0 100-6 3 3 0 000 6z" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 01-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
)

const TheoreticalIcon: React.FC<{ color: string; size?: number }> = ({ color, size = 24 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M4 19.5A2.5 2.5 0 016.5 17H20" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M8 7h8M8 11h5" stroke={color} strokeWidth="1.5" strokeLinecap="round" />
  </svg>
)

const PracticalIcon: React.FC<{ color: string; size?: number }> = ({ color, size = 24 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
)

const CompetitionIcon: React.FC<{ color: string; size?: number }> = ({ color, size = 24 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M6 9H4.5a1.5 1.5 0 010-3H6" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M18 9h1.5a1.5 1.5 0 000-3H18" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M4 22h16" stroke={color} strokeWidth="1.5" strokeLinecap="round" />
    <path d="M10 22V18.28a4 4 0 01-3.96-3.47A8 8 0 016 12V4a2 2 0 012-2h8a2 2 0 012 2v8a8 8 0 01-.04 2.81A4 4 0 0114 18.28V22" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M12 2v8l-2-1-2 1V2" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
)

const skillTypeIconMap: Record<SkillType, React.FC<{ color: string; size?: number }>> = {
  technical: TechnicalIcon,
  theoretical: TheoreticalIcon,
  practical: PracticalIcon,
  competition: CompetitionIcon,
}

function loadPositions(treeId: string): Record<string, { x: number; y: number }> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_PREFIX + treeId)
    if (raw) return JSON.parse(raw)
  } catch {}
  return {}
}

function savePositions(treeId: string, positions: Record<string, { x: number; y: number }>) {
  try {
    localStorage.setItem(STORAGE_KEY_PREFIX + treeId, JSON.stringify(positions))
  } catch {}
}

interface SkillNodeData {
  label: string
  level: string
  levelLabel: string
  color: string
  skillType: SkillType
  skillTypeLabel: string
  completionRate: number
}

type SkillNodeType = Node<SkillNodeData, 'skill'>

const SkillNodeComponent: React.FC<NodeProps<SkillNodeType>> = ({ data }) => {
  const [hovered, setHovered] = useState(false)
  const color = data.color
  const glow = hovered
    ? levelHoverGlow[data.level] ?? levelHoverGlow.intermediate!
    : levelGlowMap[data.level] ?? levelGlowMap.intermediate!
  const aura = levelAuraGradient[data.level] ?? levelAuraGradient.intermediate!
  const IconComponent = skillTypeIconMap[data.skillType] ?? TechnicalIcon

  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        cursor: 'pointer',
        position: 'relative',
        transition: 'transform 0.2s ease',
        transform: hovered ? 'scale(1.1)' : 'scale(1)',
      }}
    >
      <Handle
        type="target"
        position={Position.Top}
        style={{
          background: 'rgba(200, 210, 230, 0.25)',
          border: 'none',
          width: 5,
          height: 5,
          left: '50%',
          transform: 'translateX(-50%)',
          top: -2,
        }}
      />
      <div
        style={{
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: 56,
          height: 56,
        }}
      >
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background: aura,
            borderRadius: '50%',
            filter: hovered ? 'blur(6px)' : 'blur(4px)',
            transition: 'filter 0.3s ease',
          }}
        />
        <div
          style={{
            position: 'relative',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: glow,
            borderRadius: '50%',
            transition: 'box-shadow 0.3s ease',
          }}
        >
          <IconComponent color={color} size={32} />
        </div>
      </div>
      <div
        style={{
          marginTop: 6,
          textAlign: 'center',
          maxWidth: 100,
        }}
      >
        <div
          style={{
            fontWeight: 600,
            fontSize: 11,
            color: '#fff',
            textShadow: '0 1px 4px rgba(0,0,0,0.6)',
            lineHeight: 1.3,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {data.label}
        </div>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 4,
            marginTop: 1,
          }}
        >
          <span
            style={{
              color,
              fontSize: 9,
              fontWeight: 500,
              opacity: 0.8,
            }}
          >
            {data.levelLabel}
          </span>
          <span
            style={{
              width: 2,
              height: 2,
              borderRadius: '50%',
              background: 'rgba(200, 210, 230, 0.3)',
              display: 'inline-block',
            }}
          />
          <span
            style={{
              color: 'rgba(200, 210, 230, 0.45)',
              fontSize: 9,
            }}
          >
            {data.skillTypeLabel}
          </span>
        </div>
        {data.completionRate > 0 && (
          <div
            style={{
              marginTop: 3,
              width: '100%',
              height: 2,
              borderRadius: 1,
              background: 'rgba(200, 210, 230, 0.1)',
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                height: '100%',
                borderRadius: 1,
                background: data.completionRate >= 100 ? color : 'var(--gradient-primary)',
                width: `${data.completionRate}%`,
                transition: 'width 0.3s ease',
              }}
            />
          </div>
        )}
      </div>
      <Handle
        type="source"
        position={Position.Bottom}
        style={{
          background: 'rgba(200, 210, 230, 0.25)',
          border: 'none',
          width: 5,
          height: 5,
          left: '50%',
          transform: 'translateX(-50%)',
          bottom: -2,
        }}
      />
    </div>
  )
}

const nodeTypes = { skill: SkillNodeComponent }

interface SkillGraphProps {
  skillTree: SkillTree
  onNodeClick?: (node: SkillNode) => void
}

const SkillGraph: React.FC<SkillGraphProps> = ({ skillTree, onNodeClick }) => {
  const savedPositionsRef = useRef(loadPositions(skillTree.id))
  const lastSavedRef = useRef<Record<string, { x: number; y: number }>>({})

  const initialNodes: Node[] = useMemo(() => {
    const nodeList = Object.values(skillTree.skill_nodes)
    const saved = loadPositions(skillTree.id)
    savedPositionsRef.current = saved
    return nodeList.map((skill, index) => {
      const savedPos = saved[skill.id]
      const position = savedPos ?? { x: (index % 5) * 250, y: Math.floor(index / 5) * 150 }
      return {
        id: skill.id,
        type: 'skill',
        position,
        data: {
          label: skill.name,
          level: skill.level,
          levelLabel: SKILL_LEVEL_MAP[skill.level],
          color: levelColorMap[skill.level] ?? '#00d4ff',
          skillType: skill.type,
          skillTypeLabel: SKILL_TYPE_MAP[skill.type] ?? skill.type,
          completionRate: skill.completion_rate,
        },
      }
    })
  }, [skillTree.skill_nodes, skillTree.id])

  const initialEdges: Edge[] = useMemo(() => {
    const edgeList: Edge[] = []
    const skillNodes = Object.values(skillTree.skill_nodes)

    for (const skill of skillNodes) {
      for (const childId of skill.child_ids) {
        edgeList.push({
          id: `${skill.id}-${childId}`,
          source: skill.id,
          target: childId,
          animated: true,
          style: { stroke: EDGE_COLOR, strokeWidth: 1.5 },
        })
      }
    }

    return edgeList
  }, [skillTree.skill_nodes])

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)

  React.useEffect(() => {
    setNodes(initialNodes)
  }, [initialNodes, setNodes])

  React.useEffect(() => {
    setEdges(initialEdges)
  }, [initialEdges, setEdges])

  const handleNodesChange = useCallback(
    (changes: Parameters<typeof onNodesChange>[0]) => {
      onNodesChange(changes)

      const hasPositionChange = changes.some(
        (c) => c.type === 'position' && c.position,
      )
      if (hasPositionChange) {
        setNodes((currentNodes) => {
          const positions: Record<string, { x: number; y: number }> = {}
          for (const node of currentNodes) {
            positions[node.id] = { x: node.position.x, y: node.position.y }
          }
          const key = JSON.stringify(positions)
          const lastKey = JSON.stringify(lastSavedRef.current)
          if (key !== lastKey) {
            lastSavedRef.current = positions
            savePositions(skillTree.id, positions)
          }
          return currentNodes
        })
      }
    },
    [onNodesChange, setNodes, skillTree.id],
  )

  const handleNodeClick = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      const skillNode = skillTree.skill_nodes[node.id]
      if (skillNode && onNodeClick) {
        onNodeClick(skillNode)
      }
    },
    [skillTree.skill_nodes, onNodeClick],
  )

  const miniMapNodeColor = useCallback(
    (node: Node) => {
      const skillNode = skillTree.skill_nodes[node.id]
      if (skillNode) {
        return levelColorMap[skillNode.level] ?? '#00d4ff'
      }
      return '#00d4ff'
    },
    [skillTree.skill_nodes],
  )

  return (
    <div
      style={{
        width: '100%',
        height: 500,
        borderRadius: 'var(--radius-md)',
        overflow: 'hidden',
        border: '1px solid var(--border-glass)',
        position: 'relative',
        background: 'linear-gradient(160deg, #0a0e1a 0%, #111827 40%, #141030 100%)',
      }}
    >
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={handleNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        nodeTypes={nodeTypes}
        fitView
        proOptions={{ hideAttribution: true }}
        style={{ background: 'transparent' }}
      >
        <Background
          color="rgba(200, 210, 230, 0.04)"
          gap={24}
          size={1}
        />
        <Controls
          style={{
            background: 'rgba(17, 24, 39, 0.92)',
            border: '1px solid rgba(200, 210, 230, 0.12)',
            borderRadius: 'var(--radius-sm)',
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.5)',
            backdropFilter: 'blur(12px)',
            WebkitBackdropFilter: 'blur(12px)',
          }}
        />
        <MiniMap
          style={{
            background: 'rgba(17, 24, 39, 0.92)',
            border: '1px solid rgba(200, 210, 230, 0.12)',
            borderRadius: 'var(--radius-sm)',
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.5)',
            backdropFilter: 'blur(12px)',
            WebkitBackdropFilter: 'blur(12px)',
          }}
          maskColor="rgba(10, 14, 26, 0.65)"
          nodeColor={miniMapNodeColor}
          nodeStrokeWidth={2}
          nodeBorderRadius={4}
          pannable
          zoomable
        />
      </ReactFlow>
    </div>
  )
}

export default SkillGraph
