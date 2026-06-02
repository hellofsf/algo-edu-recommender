import { useState, useCallback } from 'react'
import apiClient from '@/api/client'

interface UseApiOptions<T> {
  onSuccess?: (data: T) => void
  onError?: (error: unknown) => void
}

interface UseApiReturn {
  data: unknown
  error: unknown
  isLoading: boolean
  execute: (config: Parameters<typeof apiClient>[0]) => Promise<unknown>
}

export function useApi<T = unknown>(options?: UseApiOptions<T>): UseApiReturn {
  const [data, setData] = useState<unknown>(null)
  const [error, setError] = useState<unknown>(null)
  const [isLoading, setIsLoading] = useState(false)

  const execute = useCallback(async (config: Parameters<typeof apiClient>[0]) => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await apiClient(config)
      setData(response.data)
      options?.onSuccess?.(response.data as T)
      return response.data
    } catch (err) {
      setError(err)
      options?.onError?.(err)
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [options])

  return { data, error, isLoading, execute }
}
