
import { AppShell } from '@/components/layout/AppShell'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Route } from 'lucide-react'

export default function LearningPathPage() {
  return (
    <AppShell>
      <div className="space-y-6 max-w-5xl">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">学习路径</h1>
          <p className="mt-1 text-slate-500">基于知识图谱的个性化学习路线</p>
        </div>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Route className="h-5 w-5 text-indigo-600" />
              学习路径
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <Route className="h-16 w-16 text-slate-200 mb-4" />
              <p className="text-lg font-medium text-slate-600">个性化学习路径</p>
              <p className="mt-1 text-sm text-slate-400">
                Phase 2 实现 — 根据知识图谱和推荐算法生成学习路线
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  )
}
