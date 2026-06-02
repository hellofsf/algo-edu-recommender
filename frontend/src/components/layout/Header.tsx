
import { Link, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/hooks/useAuth'
import { BookOpen, LogOut, User } from 'lucide-react'

export function Header() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white/80 backdrop-blur">
      <div className="flex h-14 items-center px-4 gap-4">
        <Link to="/" className="flex items-center gap-2 font-semibold text-indigo-600">
          <BookOpen className="h-5 w-5" />
          <span>AlgoEdu</span>
        </Link>

        <div className="flex-1" />

        {user && (
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-sm text-slate-600">
              <User className="h-4 w-4" />
              <span>{user.username}</span>
            </div>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4 mr-1" />
              退出
            </Button>
          </div>
        )}
      </div>
    </header>
  )
}
