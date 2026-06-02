import { memo } from 'react'
import { Handle, Position, type NodeProps } from '@xyflow/react'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'

export interface KnowledgeNodeData {
  id: string
  name: string
  difficulty: 'L1' | 'L2' | 'L3' | 'L4'
  mastery: number // 0-1
  description?: string
  onClick?: (nodeId: string) => void
}

const difficultyColors: Record<string, string> = {
  L1: 'border-green-500 bg-green-50 dark:bg-green-950',
  L2: 'border-blue-500 bg-blue-50 dark:bg-blue-950',
  L3: 'border-orange-500 bg-orange-50 dark:bg-orange-950',
  L4: 'border-red-500 bg-red-50 dark:bg-red-950',
}

const difficultyLabels: Record<string, string> = {
  L1: '入门',
  L2: '基础',
  L3: '进阶',
  L4: '竞赛',
}

function KnowledgeNode({ data, selected }: NodeProps & { data: KnowledgeNodeData }) {
  const colorClass = difficultyColors[data.difficulty] || difficultyColors.L1

  return (
    <div
      className={cn(
        'relative min-w-[120px] rounded-xl border-2 bg-white px-3 py-2 shadow-md transition-shadow',
        colorClass,
        selected && 'ring-2 ring-primary ring-offset-2'
      )}
      onClick={() => data.onClick?.(data.id)}
    >
      <Handle type="target" position={Position.Top} className="!bg-muted-foreground" />
      <div className="text-center">
        <div className="text-sm font-semibold leading-tight">{data.name}</div>
        <Badge
          variant="outline"
          className={cn('mt-1 text-[10px]', {
            'border-green-500 text-green-600': data.difficulty === 'L1',
            'border-blue-500 text-blue-600': data.difficulty === 'L2',
            'border-orange-500 text-orange-600': data.difficulty === 'L3',
            'border-red-500 text-red-600': data.difficulty === 'L4',
          })}
        >
          {difficultyLabels[data.difficulty] || data.difficulty}
        </Badge>
        {data.mastery !== undefined && (
          <div className="mt-1">
            <div className="h-1 w-full overflow-hidden rounded-full bg-gray-200">
              <div
                className="h-full rounded-full bg-primary transition-all"
                style={{ width: `${Math.round(data.mastery * 100)}%` }}
              />
            </div>
            <div className="mt-0.5 text-[10px] text-muted-foreground">
              {Math.round(data.mastery * 100)}%
            </div>
          </div>
        )}
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-muted-foreground" />
    </div>
  )
}

export default memo(KnowledgeNode)
