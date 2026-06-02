import { useState, type ChangeEvent, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { authApi } from '@/api/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { BookOpen, AlertCircle } from 'lucide-react'

export default function RegisterPage() {
  const navigate = useNavigate()
  const { setUser } = useAuth()
  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    password_confirm: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')

    if (form.password !== form.password_confirm) {
      setError('两次密码输入不一致')
      return
    }

    if (form.password.length < 6) {
      setError('密码长度至少为6位')
      return
    }

    setLoading(true)

    try {
      const response = await authApi.register(form)
      setUser(response.user, response.access_token)
      navigate('/')
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string; message?: string } } }
      const detail = axiosError.response?.data?.detail || axiosError.response?.data?.message
      setError(detail || '注册失败，请稍后重试。')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <Card className="w-full max-w-sm">
        <CardHeader className="space-y-1 text-center">
          <div className="flex justify-center mb-2">
            <BookOpen className="h-10 w-10 text-indigo-600" />
          </div>
          <CardTitle className="text-2xl">创建账号</CardTitle>
          <CardDescription>注册 AlgoEdu，开始你的算法学习之旅</CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            {error && (
              <div className="flex items-center gap-2 rounded-md bg-red-50 p-3 text-sm text-red-600">
                <AlertCircle className="h-4 w-4 flex-shrink-0" />
                {error}
              </div>
            )}
            <div className="space-y-2">
              <Label htmlFor="username">用户名</Label>
              <Input
                id="username"
                name="username"
                type="text"
                placeholder="请输入用户名"
                value={form.username}
                onChange={handleChange}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">邮箱</Label>
              <Input
                id="email"
                name="email"
                type="email"
                placeholder="请输入邮箱"
                value={form.email}
                onChange={handleChange}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">密码</Label>
              <Input
                id="password"
                name="password"
                type="password"
                placeholder="请输入密码"
                value={form.password}
                onChange={handleChange}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password_confirm">确认密码</Label>
              <Input
                id="password_confirm"
                name="password_confirm"
                type="password"
                placeholder="请再次输入密码"
                value={form.password_confirm}
                onChange={handleChange}
                required
              />
            </div>
          </CardContent>
          <CardFooter className="flex flex-col gap-3">
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? '注册中...' : '注册'}
            </Button>
            <p className="text-sm text-center text-slate-500">
              已有账号？{' '}
              <Link to="/login" className="text-indigo-600 hover:underline font-medium">
                立即登录
              </Link>
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  )
}
