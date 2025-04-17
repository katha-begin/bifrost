import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './api-client';
import { Shot } from '../types';

export const useShots = () => {
  return useQuery({
    queryKey: ['shots'],
    queryFn: async () => {
      const { data } = await apiClient.get<Shot[]>('/api/shots');
      return data;
    }
  });
};

export const useShot = (id: string) => {
  return useQuery({
    queryKey: ['shots', id],
    queryFn: async () => {
      const { data } = await apiClient.get<Shot>(`/api/shots/${id}`);
      return data;
    },
    enabled: !!id
  });
};

export const useCreateShot = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (newShot: Omit<Shot, 'id' | 'created_at' | 'updated_at'>) => {
      const { data } = await apiClient.post<Shot>('/api/shots', newShot);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shots'] });
    }
  });
};

export const useUpdateShot = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, ...updateData }: Partial<Shot> & { id: string }) => {
      const { data } = await apiClient.patch<Shot>(`/api/shots/${id}`, updateData);
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['shots', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['shots'] });
    }
  });
};