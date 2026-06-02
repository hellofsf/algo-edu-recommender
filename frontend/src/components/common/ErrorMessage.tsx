
import { AlertTriangle, XCircle, Info } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface ErrorMessageProps {
  title?: string
  message?: string
  onRetry?: () => void
  variant?: 'error' | 'warning' | 'info'
}

export function ErrorMessage({
  title = '出错了',
  message = '发生了未知错误，请稍后重试。',
  onRetry,
  variant = 'error',
}: ErrorMessageProps) {
  const iconMap = {
    error: <XCircle className="h-8 w-8 text-red-500" />,
    warning: <AlertTriangle className="h-8 w-8 text-amber-500" />,
    info: <Info className="h-8 w-8 text-blue-500" />,
  }

  const colorMap = {
    error: 'border-red-200 bg-red-50',
    warning: 'border-amber-200 bg-amber-50',
    info: 'border-blue-200 bg-blue-50',
  }

  return (
    <div className={`flex flex-col items-center gap-3 rounded-lg border p-6 ${colorMap[variant]}`}>
      {iconMap[variant]}
      <div className="text-center">
        <p className="font-medium text-slate-800">{title}</p>
        {message && <p className="mt-1 text-sm text-slate-600">{message}</p>}
      </div>
      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry}>
          重试
        </Button>
      )}
    </div>
  )
}
