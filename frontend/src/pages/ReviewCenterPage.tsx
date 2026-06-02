
import { AppShell } from '@/components/layout/AppShell'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { RefreshCcw } from 'lucide-react'

export default function ReviewCenterPage() {
  return (
    <AppShell>
      <div className="space-y-6 max-w-5xl">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">复习中心</h1>
          <p className="mt-1 text-slate-500">基于艾宾浩斯遗忘曲线的智能复习</p>
        </div>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <RefreshCcw className="h-5 w-5 text-indigo-600" />
              复习队列
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <RefreshCcw className="h-16 w-16 text-slate-200 mb-4" />
              <p className="text-lg font-medium text-slate-600">间隔重复复习</p>
              <p className="mt-1 text-sm text-slate-400">
                Phase 3 实现 — 根据记忆曲线自动安排复习时间和内容
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  )
}
