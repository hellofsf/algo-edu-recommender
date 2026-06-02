import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { reviewApi } from '@/api/review'
import { useAuthStore } from '@/stores/authStore'
import { cn } from '@/lib/utils'

interface ReviewItem {
  id: string
  node_id: string
  name: string
  description?: string
  category?: string
  last_reviewed?: string
  memory_strength?: number // 0-1
  next_review?: string
  difficulty?: 'L1' | 'L2' | 'L3' | 'L4'
}

interface ReviewCardProps {
  item: ReviewItem
  onComplete?: (itemId: string, quality: number) => void
  onSkip?: (itemId: string) => void
}

const QUALITY_OPTIONS = [
  { value: 0, label: '完全忘记', color: 'bg-red-500 hover:bg-red-600', textColor: 'text-white' },
  { value: 1, label: '忘了', color: 'bg-orange-500 hover:bg-orange-600', textColor: 'text-white' },
  { value: 2, label: '模糊', color: 'bg-yellow-500 hover:bg-yellow-600', textColor: 'text-white' },
  { value: 3, label: '记住了', color: 'bg-lime-500 hover:bg-lime-600', textColor: 'text-white' },
  { value: 4, label: '很熟', color: 'bg-green-500 hover:bg-green-600', textColor: 'text-white' },
  { value: 5, label: '滚瓜烂熟', color: 'bg-emerald-600 hover:bg-emerald-700', textColor: 'text-white' },
]

function formatDate(dateStr?: string): string {
  if (!dateStr) return '未复习过'
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN')
}

function formatNextReview(dateStr?: string): string {
  if (!dateStr) return '尽快复习'
  const date = new Date(dateStr)
  const now = new Date()
  const diff = date.getTime() - now.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  if (days <= 0) return '今天到期'
  if (days === 1) return '明天到期'
  return `${days}天后到期`
}

export function ReviewCard({ item, onComplete, onSkip }: ReviewCardProps) {
  const [selectedQuality, setSelectedQuality] = useState<number | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const { isAuthenticated } = useAuthStore()

  const handleSubmit = async () => {
    if (selectedQuality === null || !isAuthenticated) return
    setSubmitting(true)
    try {
      await reviewApi.submitReview({ node_id: item.node_id, quality: selectedQuality })
      onComplete?.(item.id, selectedQuality)
    } catch (err) {
      console.error('Failed to submit review:', err)
    } finally {
      setSubmitting(false)
    }
  }

  const handleSkip = () => {
    onSkip?.(item.id)
  }

  return (
    <Card className="w-full">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-base">{item.name}</CardTitle>
            {item.description && (
              <CardDescription className="mt-1 line-clamp-2">
                {item.description}
              </CardDescription>
            )}
          </div>
          {item.difficulty && (
            <Badge
              variant={
                item.difficulty === 'L1'
                  ? 'default'
                  : item.difficulty === 'L2'
                  ? 'secondary'
                  : item.difficulty === 'L3'
                  ? 'outline'
                  : 'destructive'
              }
              className="ml-2 shrink-0"
            >
              {item.difficulty}
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>上次复习: {formatDate(item.last_reviewed)}</span>
          {item.memory_strength !== undefined && (
            <span className={cn(
              item.memory_strength >= 0.7
                ? 'text-green-600'
                : item.memory_strength >= 0.4
                ? 'text-yellow-600'
                : 'text-red-600'
            )}>
              记忆强度: {(item.memory_strength * 100).toFixed(0)}%
            </span>
          )}
        </div>

        <div className="rounded-md bg-muted/50 px-3 py-1.5 text-xs">
          <span className="text-muted-foreground">下次复习: </span>
          <span className="font-medium">{formatNextReview(item.next_review)}</span>
        </div>

        {/* Quality rating buttons */}
        <div className="space-y-1.5">
          <div className="text-xs text-muted-foreground">你对这道题的记忆如何?</div>
          <div className="grid grid-cols-3 gap-1.5 sm:grid-cols-6">
            {QUALITY_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                disabled={!isAuthenticated || submitting}
                onClick={() => setSelectedQuality(opt.value)}
                className={cn(
                  'rounded-md border px-2 py-1.5 text-xs font-medium transition-all',
                  selectedQuality === opt.value
                    ? `${opt.color} ${opt.textColor} border-transparent shadow-sm scale-105`
                    : 'border-input bg-background text-muted-foreground hover:bg-accent'
                )}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        <div className="flex gap-2">
          <Button
            className="flex-1"
            onClick={handleSubmit}
            disabled={selectedQuality === null || !isAuthenticated || submitting}
          >
            {submitting ? '提交中...' : '提交复习'}
          </Button>
          <Button variant="outline" onClick={handleSkip} disabled={submitting}>
            跳过
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

export default ReviewCard
