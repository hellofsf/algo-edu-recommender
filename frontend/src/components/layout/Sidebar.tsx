
import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/utils'
import {
  LayoutDashboard,
  GitBranch,
  Route,
  RefreshCcw,
  Sparkles,
  Settings,
} from 'lucide-react'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: '首页', exact: true },
  { to: '/graph', icon: GitBranch, label: '知识图谱' },
  { to: '/path', icon: Route, label: '学习路径' },
  { to: '/review', icon: RefreshCcw, label: '复习中心' },
  { to: '/recommend', icon: Sparkles, label: '智能推荐' },
  { to: '/settings', icon: Settings, label: '设置' },
]

export function Sidebar() {
  const location = useLocation()

  return (
    <aside className="hidden md:flex w-56 flex-col border-r bg-white">
      <nav className="flex flex-col gap-1 p-3">
        {navItems.map(({ to, icon: Icon, label, exact }) => {
          const isActive = exact
            ? location.pathname === to
            : location.pathname.startsWith(to)
          return (
            <Link
              key={to}
              to={to}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-indigo-50 text-indigo-700'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              )}
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
