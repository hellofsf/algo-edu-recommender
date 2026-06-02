
import { AppShell } from '@/components/layout/AppShell'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Settings } from 'lucide-react'

export default function SettingsPage() {
  return (
    <AppShell>
      <div className="space-y-6 max-w-5xl">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">设置</h1>
          <p className="mt-1 text-slate-500">个人偏好与系统配置</p>
        </div>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5 text-indigo-600" />
              设置选项
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <Settings className="h-16 w-16 text-slate-200 mb-4" />
              <p className="text-lg font-medium text-slate-600">设置面板</p>
              <p className="mt-1 text-sm text-slate-400">
                Phase 2 实现 — 学习目标、每日提醒、主题切换等个性化设置
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  )
}
