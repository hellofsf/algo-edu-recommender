
import { useAuth } from '@/hooks/useAuth'
import { AppShell } from '@/components/layout/AppShell'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { BookOpen, Brain, RefreshCcw, TrendingUp, ChevronRight } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function DashboardPage() {
  const { user } = useAuth()

  const greeting = (() => {
    const hour = new Date().getHours()
    if (hour < 12) return '早上好'
    if (hour < 18) return '下午好'
    return '晚上好'
  })()

  return (
    <AppShell>
      <div className="space-y-6 max-w-5xl">
        {/* 欢迎横幅 */}
        <div className="rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 p-6 text-white shadow-lg">
          <h1 className="text-2xl font-bold">
            {greeting}，{user?.username ?? '同学'} 👋
          </h1>
          <p className="mt-1 text-indigo-100">
            欢迎来到你的个人算法学习中心，今天也要加油哦！
          </p>
        </div>

        {/* 统计卡片 */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardContent className="flex items-center gap-4 p-4">
              <div className="rounded-full bg-indigo-100 p-3">
                <BookOpen className="h-5 w-5 text-indigo-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">—</p>
                <p className="text-xs text-slate-500">今日任务</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="flex items-center gap-4 p-4">
              <div className="rounded-full bg-green-100 p-3">
                <TrendingUp className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">—</p>
                <p className="text-xs text-slate-500">已掌握</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="flex items-center gap-4 p-4">
              <div className="rounded-full bg-amber-100 p-3">
                <RefreshCcw className="h-5 w-5 text-amber-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">—</p>
                <p className="text-xs text-slate-500">待复习</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="flex items-center gap-4 p-4">
              <div className="rounded-full bg-purple-100 p-3">
                <Brain className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">—</p>
                <p className="text-xs text-slate-500">连续学习</p>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* 今日任务 */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <div>
                <CardTitle>今日学习任务</CardTitle>
                <CardDescription>你的每日算法练习</CardDescription>
              </div>
              <Link to="/path" className="text-sm text-indigo-600 hover:underline flex items-center gap-1">
                查看全部 <ChevronRight className="h-4 w-4" />
              </Link>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <BookOpen className="h-10 w-10 text-slate-300 mb-3" />
                <p className="text-sm font-medium text-slate-600">暂无今日任务</p>
                <p className="mt-1 text-xs text-slate-400">Phase 2 将接入推荐算法生成个性化任务</p>
                <Link
                  to="/recommend"
                  className="mt-4 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
                >
                  获取推荐
                </Link>
              </div>
            </CardContent>
          </Card>

          {/* 复习提醒 */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <div>
                <CardTitle>复习提醒</CardTitle>
                <CardDescription>基于艾宾浩斯遗忘曲线</CardDescription>
              </div>
              <Link to="/review" className="text-sm text-indigo-600 hover:underline flex items-center gap-1">
                查看全部 <ChevronRight className="h-4 w-4" />
              </Link>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <RefreshCcw className="h-10 w-10 text-slate-300 mb-3" />
                <p className="text-sm font-medium text-slate-600">暂无复习提醒</p>
                <p className="mt-1 text-xs text-slate-400">完成练习后将自动生成复习计划</p>
                <Link
                  to="/graph"
                  className="mt-4 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
                >
                  查看知识图谱
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 快捷入口 */}
        <div>
          <h2 className="mb-3 text-lg font-semibold text-slate-800">快捷入口</h2>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { to: '/graph', label: '知识图谱', icon: Brain, color: 'bg-indigo-50 text-indigo-700' },
              { to: '/path', label: '学习路径', icon: TrendingUp, color: 'bg-green-50 text-green-700' },
              { to: '/review', label: '复习中心', icon: RefreshCcw, color: 'bg-amber-50 text-amber-700' },
              { to: '/recommend', label: '智能推荐', icon: BookOpen, color: 'bg-purple-50 text-purple-700' },
            ].map(({ to, label, icon: Icon, color }) => (
              <Link
                key={to}
                to={to}
                className={`flex items-center gap-3 rounded-lg border p-4 transition-colors hover:border-indigo-300 hover:bg-indigo-50/50 ${color}`}
              >
                <Icon className="h-5 w-5" />
                <span className="text-sm font-medium">{label}</span>
              </Link>
            ))}
          </div>
        </div>

        {/* 进度概览 */}
        <Card>
          <CardHeader>
            <CardTitle>学习进度概览</CardTitle>
            <CardDescription>各模块掌握情况</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { topic: '数组与链表', progress: 0, color: 'bg-indigo-500' },
                { topic: '栈与队列', progress: 0, color: 'bg-green-500' },
                { topic: '树与图', progress: 0, color: 'bg-amber-500' },
                { topic: '动态规划', progress: 0, color: 'bg-purple-500' },
                { topic: '排序与搜索', progress: 0, color: 'bg-rose-500' },
              ].map(({ topic, progress, color }) => (
                <div key={topic} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">{topic}</span>
                    <span className="font-medium text-slate-400">{progress}%</span>
                  </div>
                  <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
                    <div className={`h-full rounded-full transition-all ${color}`} style={{ width: `${progress}%` }} />
                  </div>
                </div>
              ))}
            </div>
            <p className="mt-4 text-center text-xs text-slate-400">
              Phase 2-3 将接入真实学习数据
            </p>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  )
}
