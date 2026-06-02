import apiClient from './client';

export const graphApi = {
  getSubgraph: (centerNodeId?: string, depth: number = 2) =>
    apiClient.get('/graph/subgraph', { params: { center_node_id: centerNodeId, depth } }),
  getOverview: () => apiClient.get('/graph/overview'),
};
