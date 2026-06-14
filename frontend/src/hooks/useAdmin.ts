import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ApiClient } from '../lib/api';

// Users
export const useAdminUsers = (skip = 0, limit = 50) => {
  return useQuery({
    queryKey: ['admin', 'users', skip, limit],
    queryFn: () => ApiClient.get(`/admin/users?skip=${skip}&limit=${limit}`),
  });
};

export const useCreateUser = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => ApiClient.post('/admin/users', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin', 'users'] }),
  });
};

export const useUpdateUser = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => ApiClient.put(`/admin/users/${id}`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin', 'users'] }),
  });
};

export const useToggleUserSubscription = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: { sub_type: string, duration_days: number } }) => 
      ApiClient.post(`/admin/users/${id}/subscription/toggle`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin', 'users'] }),
  });
};

// Teams
export const useAdminTeams = (skip = 0, limit = 50) => {
  return useQuery({
    queryKey: ['admin', 'teams', skip, limit],
    queryFn: () => ApiClient.get(`/admin/teams?skip=${skip}&limit=${limit}`),
  });
};

export const useCreateTeam = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => ApiClient.post('/admin/teams', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin', 'teams'] }),
  });
};

export const useUpdateTeam = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => ApiClient.put(`/admin/teams/${id}`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin', 'teams'] }),
  });
};

export const useDeleteTeam = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => ApiClient.delete(`/admin/teams/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin', 'teams'] }),
  });
};

// Settings
export const useAdminSystemSettings = () => {
  return useQuery({
    queryKey: ['admin', 'system-settings'],
    queryFn: () => ApiClient.get('/admin/system-settings'),
  });
};

export const useUpdateSystemSetting = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ key, data }: { key: string; data: any }) => ApiClient.put(`/admin/system-settings/${key}`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin', 'system-settings'] }),
  });
};

export const useAdminFeatureFlags = () => {
  return useQuery({
    queryKey: ['admin', 'feature-flags'],
    queryFn: () => ApiClient.get('/admin/feature-flags'),
  });
};

export const useUpdateFeatureFlag = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ key, data }: { key: string; data: any }) => ApiClient.put(`/admin/feature-flags/${key}`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin', 'feature-flags'] }),
  });
};

// Conversations (Support)
export const useAdminConversations = (skip = 0, limit = 50, status?: string) => {
  return useQuery({
    queryKey: ['admin', 'conversations', skip, limit, status],
    queryFn: () => ApiClient.get(`/admin/conversations?skip=${skip}&limit=${limit}${status ? `&status=${status}` : ''}`),
  });
};

export const useAdminConversationMessages = (id: string) => {
  return useQuery({
    queryKey: ['admin', 'conversations', id, 'messages'],
    queryFn: () => ApiClient.get(`/admin/conversations/${id}/messages`),
    enabled: !!id,
  });
};

export const useUpdateConversation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => ApiClient.put(`/admin/conversations/${id}`, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'conversations'] });
    },
  });
};

export const useReplyConversation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, content }: { id: string; content: string }) => ApiClient.post(`/admin/conversations/${id}/messages`, { content }),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'conversations', id, 'messages'] });
      queryClient.invalidateQueries({ queryKey: ['admin', 'conversations'] });
    },
  });
};

// Tasks
export const useAdminTasks = (skip = 0, limit = 50) => {
  return useQuery({
    queryKey: ['admin', 'tasks', skip, limit],
    queryFn: () => ApiClient.get(`/admin/tasks?skip=${skip}&limit=${limit}`),
  });
};

export const useDeleteAdminTask = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => ApiClient.delete(`/admin/tasks/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin', 'tasks'] }),
  });
};

// Subscriptions
export const useAdminSubscriptionPlans = () => {
  return useQuery({
    queryKey: ['admin', 'subscription-plans'],
    queryFn: () => ApiClient.get('/admin/subscriptions/plans'),
  });
};

export const useCreateSubscriptionPlan = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => ApiClient.post('/admin/subscriptions/plans', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin', 'subscription-plans'] }),
  });
};

export const useUpdateSubscriptionPlan = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => ApiClient.put(`/admin/subscriptions/plans/${id}`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin', 'subscription-plans'] }),
  });
};

export const useAdminSubscriptions = () => {
  return useQuery({
    queryKey: ['admin', 'subscriptions'],
    queryFn: () => ApiClient.get('/admin/subscriptions'),
  });
};

// --- AI Settings & Usage ---
export const useAdminAIProviders = () => {
  return useQuery({
    queryKey: ['admin', 'ai', 'providers'],
    queryFn: () => ApiClient.get('/admin/ai/providers'),
  });
};

export const useCreateAIProvider = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => ApiClient.post('/admin/ai/providers', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin', 'ai', 'providers'] }),
  });
};

export const useUpdateAIProvider = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => ApiClient.put(`/admin/ai/providers/${id}`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin', 'ai', 'providers'] }),
  });
};

export const useAdminAIModels = (provider_id?: string) => {
  return useQuery({
    queryKey: ['admin', 'ai', 'models', provider_id],
    queryFn: () => ApiClient.get(`/admin/ai/models${provider_id ? `?provider_id=${provider_id}` : ''}`),
  });
};

export const useCreateAIModel = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => ApiClient.post('/admin/ai/models', data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin', 'ai', 'models'] }),
  });
};

export const useUpdateAIModel = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => ApiClient.put(`/admin/ai/models/${id}`, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin', 'ai', 'models'] }),
  });
};

export const useAdminAIUsageLogs = (skip = 0, limit = 50, provider?: string) => {
  return useQuery({
    queryKey: ['admin', 'ai', 'usage', skip, limit, provider],
    queryFn: () => ApiClient.get(`/admin/ai/usage?skip=${skip}&limit=${limit}${provider ? `&provider=${provider}` : ''}`),
  });
};
