import apiClient from './client'

export const healthApi = {
  check: async (): Promise<{ status: string; message: string }> => {
    const response = await apiClient.get<{ status: string; message: string }>('/health')
    return response.data
  },
}
