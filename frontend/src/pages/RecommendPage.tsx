
import { AppShell } from '@/components/layout/AppShell'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Sparkles } from 'lucide-react'

export default function RecommendPage() {
  return (
    <AppShell>
      <div className="space-y-6 max-w-5xl">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">智能推荐</h1>
          <p className="mt-1 text-slate-500">AI驱动的个性化算法题目推荐</p>
        </div>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-indigo-600" />
              推荐算法
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <Sparkles className="h-16 w-16 text-slate-200 mb-4" />
              <p className="text-lg font-medium text-slate-600">智能推荐引擎</p>
              <p className="mt-1 text-sm text-slate-400">
                Phase 2 实现 — 结合协同过滤与知识图谱的混合推荐算法
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  )
}
