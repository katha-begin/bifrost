import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './api-client';
import { Asset } from '../types';

// Mock data for assets
const mockAssets: Asset[] = [
  {
    id: 'asset-001',
    name: 'Character - Hero',
    type: 'character',
    status: 'in_progress',
    version: 3,
    metadata: {
      artist: 'John Doe',
      department: 'Character',
      polygons: 12500
    },
    created_at: '2023-09-15T10:30:00Z',
    updated_at: '2023-10-05T14:45:00Z'
  },
  {
    id: 'asset-002',
    name: 'Environment - Forest',
    type: 'environment',
    status: 'approved',
    version: 5,
    metadata: {
      artist: 'Jane Smith',
      department: 'Environment',
      area: 'Main Forest'
    },
    created_at: '2023-08-20T09:15:00Z',
    updated_at: '2023-10-10T11:20:00Z'
  },
  {
    id: 'asset-003',
    name: 'Prop - Magic Sword',
    type: 'prop',
    status: 'completed',
    version: 2,
    metadata: {
      artist: 'Mike Johnson',
      department: 'Props',
      material: 'Metal'
    },
    created_at: '2023-09-25T13:45:00Z',
    updated_at: '2023-10-12T16:30:00Z'
  },
  {
    id: 'asset-004',
    name: 'Vehicle - Spaceship',
    type: 'vehicle',
    status: 'in_review',
    version: 4,
    metadata: {
      artist: 'Sarah Williams',
      department: 'Vehicles',
      size: 'Large'
    },
    created_at: '2023-09-10T08:20:00Z',
    updated_at: '2023-10-08T09:15:00Z'
  },
  {
    id: 'asset-005',
    name: 'Character - Villain',
    type: 'character',
    status: 'in_progress',
    version: 2,
    metadata: {
      artist: 'Robert Chen',
      department: 'Character',
      polygons: 15000
    },
    created_at: '2023-09-18T11:30:00Z',
    updated_at: '2023-10-07T13:45:00Z'
  }
];

export const useAssets = () => {
  return useQuery({
    queryKey: ['assets'],
    queryFn: async () => {
      try {
        const { data } = await apiClient.get<Asset[]>('/api/v1/assets/');
        return data;
      } catch (error) {
        console.log('Using mock assets data');
        return mockAssets;
      }
    }
  });
};

export const useAsset = (id: string) => {
  return useQuery({
    queryKey: ['assets', id],
    queryFn: async () => {
      try {
        const { data } = await apiClient.get<Asset>(`/api/v1/assets/${id}`);
        return data;
      } catch (error) {
        console.log('Using mock asset data');
        const asset = mockAssets.find(a => a.id === id);
        if (!asset) throw new Error('Asset not found');
        return asset;
      }
    },
    enabled: !!id
  });
};

export const useCreateAsset = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (newAsset: Omit<Asset, 'id' | 'created_at' | 'updated_at'>) => {
      const { data } = await apiClient.post<Asset>('/api/v1/assets/', newAsset);
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
      const { data } = await apiClient.patch<Asset>(`/api/v1/assets/${id}`, updateData);
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['assets', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['assets'] });
    }
  });
};