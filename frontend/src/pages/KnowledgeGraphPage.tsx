
import { AppShell } from '@/components/layout/AppShell'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Brain } from 'lucide-react'

export default function KnowledgeGraphPage() {
  return (
    <AppShell>
      <div className="space-y-6 max-w-5xl">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">知识图谱</h1>
          <p className="mt-1 text-slate-500">可视化展示算法知识体系结构</p>
        </div>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-indigo-600" />
              图谱展示
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <Brain className="h-16 w-16 text-slate-200 mb-4" />
              <p className="text-lg font-medium text-slate-600">React Flow 图谱</p>
              <p className="mt-1 text-sm text-slate-400">
                Phase 2 实现 — 基于 React Flow 12.x 渲染可交互的知识图谱
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  )
}
