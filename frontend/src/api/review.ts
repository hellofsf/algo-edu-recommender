import apiClient from './client';

export const reviewApi = {
  getDueReviews: () => apiClient.get('/review/due'),
  getForgettingCurve: (nodeId: string) => apiClient.get(`/review/curve/${nodeId}`),
  submitReview: (data: { node_id: string; quality: number }) =>
    apiClient.post('/review/schedule', data),
  getStats: () => apiClient.get('/review/stats'),
};
