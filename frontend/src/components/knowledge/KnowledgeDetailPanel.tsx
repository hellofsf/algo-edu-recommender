import { X, BookOpen, ArrowRight, CheckCircle2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { learningApi } from '@/api/learning'
import { useAuthStore } from '@/stores/authStore'


export interface KnowledgeNodeDetail {
  id: string
  name: string
  description?: string
  category?: string
  difficulty: 'L1' | 'L2' | 'L3' | 'L4'
  mastery: number // 0-1
  prerequisites?: Array<{ id: string; name: string }>
  relatedNodes?: Array<{ id: string; name: string }>
}

interface KnowledgeDetailPanelProps {
  node: KnowledgeNodeDetail | null
  onClose: () => void
  onStartLearning?: (nodeId: string) => void
}

const difficultyLabels: Record<string, string> = {
  L1: '入门',
  L2: '基础',
  L3: '进阶',
  L4: '竞赛',
}

const difficultyVariants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
  L1: 'default',
  L2: 'secondary',
  L3: 'outline',
  L4: 'destructive',
}

export function KnowledgeDetailPanel({ node, onClose, onStartLearning }: KnowledgeDetailPanelProps) {
  const { isAuthenticated } = useAuthStore()

  if (!node) return null

  const handleStartLearning = async () => {
    if (!isAuthenticated) return
    try {
      await learningApi.recordLearning({ node_id: node.id })
      onStartLearning?.(node.id)
    } catch (err) {
      console.error('Failed to start learning:', err)
    }
  }

  const handleMarkMastered = async () => {
    if (!isAuthenticated) return
    try {
      await learningApi.recordLearning({ node_id: node.id, duration_seconds: 0 })
      onStartLearning?.(node.id)
    } catch (err) {
      console.error('Failed to mark mastered:', err)
    }
  }

  return (
    <Card className="absolute right-4 top-4 z-10 w-80 shadow-xl">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-base font-semibold">{node.name}</CardTitle>
        <Button variant="ghost" size="icon" onClick={onClose} className="h-7 w-7">
          <X className="h-4 w-4" />
        </Button>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex flex-wrap gap-2">
          <Badge variant={difficultyVariants[node.difficulty]}>
            {difficultyLabels[node.difficulty] || node.difficulty}
          </Badge>
          {node.category && (
            <Badge variant="outline">{node.category}</Badge>
          )}
        </div>

        {node.description && (
          <p className="text-sm text-muted-foreground">{node.description}</p>
        )}

        {node.mastery !== undefined && (
          <div>
            <div className="mb-1 flex items-center justify-between text-xs">
              <span className="text-muted-foreground">掌握度</span>
              <span className="font-medium">{Math.round(node.mastery * 100)}%</span>
            </div>
            <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
              <div
                className="h-full rounded-full bg-primary transition-all"
                style={{ width: `${Math.round(node.mastery * 100)}%` }}
              />
            </div>
          </div>
        )}

        {node.prerequisites && node.prerequisites.length > 0 && (
          <div>
            <div className="mb-1.5 text-xs font-medium text-muted-foreground">前置知识</div>
            <div className="space-y-1">
              {node.prerequisites.map((p) => (
                <div key={p.id} className="flex items-center gap-1.5 text-xs">
                  <ArrowRight className="h-3 w-3 text-muted-foreground" />
                  <span>{p.name}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {node.relatedNodes && node.relatedNodes.length > 0 && (
          <div>
            <div className="mb-1.5 text-xs font-medium text-muted-foreground">相关链接</div>
            <div className="space-y-1">
              {node.relatedNodes.map((r) => (
                <div key={r.id} className="flex items-center gap-1.5 text-xs">
                  <BookOpen className="h-3 w-3 text-muted-foreground" />
                  <span>{r.name}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex gap-2 pt-1">
          <Button
            size="sm"
            className="flex-1"
            onClick={handleStartLearning}
            disabled={!isAuthenticated}
          >
            <BookOpen className="mr-1 h-3.5 w-3.5" />
            开始学习
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={handleMarkMastered}
            disabled={!isAuthenticated}
          >
            <CheckCircle2 className="mr-1 h-3.5 w-3.5" />
            标记掌握
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

export default KnowledgeDetailPanel
