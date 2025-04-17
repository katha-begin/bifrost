import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './api-client';
import { Asset } from '../types';

export const useAssets = () => {
  return useQuery({
    queryKey: ['assets'],
    queryFn: async () => {
      const { data } = await apiClient.get<Asset[]>('/api/assets');
      return data;
    }
  });
};

export const useAsset = (id: string) => {
  return useQuery({
    queryKey: ['assets', id],
    queryFn: async () => {
      const { data } = await apiClient.get<Asset>(`/api/assets/${id}`);
      return data;
    },
    enabled: !!id
  });
};

export const useCreateAsset = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (newAsset: Omit<Asset, 'id' | 'created_at' | 'updated_at'>) => {
      const { data } = await apiClient.post<Asset>('/api/assets', newAsset);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assets'] });
    }
  });
};

export const useUpdateAsset = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, ...updateData }: Partial<Asset> & { id: string }) => {
      const { data } = await apiClient.patch<Asset>(`/api/assets/${id}`, updateData);
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['assets', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['assets'] });
    }
  });
};