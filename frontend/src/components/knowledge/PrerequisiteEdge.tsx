import { memo } from 'react'
import { getBezierPath, type EdgeProps } from '@xyflow/react'
import { cn } from '@/lib/utils'

export interface PrerequisiteEdgeData {
  relation?: 'required' | 'optional'
  weight?: number
}

const relationColors: Record<string, string> = {
  required: '#6366f1', // indigo-500
  optional: '#94a3b8', // slate-400
}

function PrerequisiteEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  selected,
}: EdgeProps & { data?: PrerequisiteEdgeData }) {
  const relation = data?.relation || 'required'
  const color = relationColors[relation] || relationColors.required
  const isDashed = relation === 'optional'

  const [edgePath] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  })

  return (
    <>
      <path
        id={id}
        className={cn('fill-none', isDashed && 'stroke-dasharray-4 4')}
        stroke={color}
        strokeWidth={selected ? 2.5 : 1.5}
        markerEnd={`url(#arrowhead-${relation})`}
        d={edgePath}
      />
      {/* Arrowhead markers */}
      <defs>
        <marker
          id={`arrowhead-${relation}`}
          markerWidth="8"
          markerHeight="8"
          refX="6"
          refY="3"
          orient="auto"
        >
          <path d="M0,0 L0,6 L8,3 z" fill={color} />
        </marker>
      </defs>
    </>
  )
}

export default memo(PrerequisiteEdge)
