import apiClient from './client';

export const learningApi = {
  recordLearning: (data: { node_id: string; duration_seconds?: number }) =>
    apiClient.post('/learning/record', data),
  getHistory: (params?: { limit?: number }) =>
    apiClient.get('/learning/history', { params }),
  getPath: (targetNodeId?: string) =>
    apiClient.get('/learning/path', { params: { target_node_id: targetNodeId } }),
};
