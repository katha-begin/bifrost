import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './api-client';
import { Shot } from '../types';

// Mock data for shots
const mockShots: Shot[] = [
  {
    id: 'shot-001',
    name: 'Opening Scene',
    sequence: 'seq001',
    frameStart: 1001,
    frameEnd: 1124,
    status: 'in_progress',
    version: 2,
    assets: ['asset-001', 'asset-002'],
    created_at: '2023-09-20T09:30:00Z',
    updated_at: '2023-10-08T15:45:00Z'
  },
  {
    id: 'shot-002',
    name: 'Hero vs Villain',
    sequence: 'seq003',
    frameStart: 3045,
    frameEnd: 3156,
    status: 'in_review',
    version: 3,
    assets: ['asset-001', 'asset-003', 'asset-005'],
    created_at: '2023-09-22T10:15:00Z',
    updated_at: '2023-10-10T14:30:00Z'
  },
  {
    id: 'shot-003',
    name: 'Spaceship Landing',
    sequence: 'seq002',
    frameStart: 2078,
    frameEnd: 2145,
    status: 'completed',
    version: 4,
    assets: ['asset-004', 'asset-002'],
    created_at: '2023-09-18T11:45:00Z',
    updated_at: '2023-10-12T16:20:00Z'
  },
  {
    id: 'shot-004',
    name: 'Forest Chase',
    sequence: 'seq004',
    frameStart: 4012,
    frameEnd: 4189,
    status: 'in_progress',
    version: 1,
    assets: ['asset-001', 'asset-002', 'asset-003'],
    created_at: '2023-09-25T13:30:00Z',
    updated_at: '2023-10-09T10:45:00Z'
  },
  {
    id: 'shot-005',
    name: 'Final Battle',
    sequence: 'seq005',
    frameStart: 5001,
    frameEnd: 5234,
    status: 'not_started',
    version: 1,
    assets: ['asset-001', 'asset-003', 'asset-005'],
    created_at: '2023-09-28T14:15:00Z',
    updated_at: '2023-09-28T14:15:00Z'
  }
];

export const useShots = () => {
  return useQuery({
    queryKey: ['shots'],
    queryFn: async () => {
      try {
        const { data } = await apiClient.get<Shot[]>('/api/v1/shots/');
        return data;
      } catch (error) {
        console.log('Using mock shots data');
        return mockShots;
      }
    }
  });
};

export const useShot = (id: string) => {
  return useQuery({
    queryKey: ['shots', id],
    queryFn: async () => {
      try {
        const { data } = await apiClient.get<Shot>(`/api/v1/shots/${id}`);
        return data;
      } catch (error) {
        console.log('Using mock shot data');
        const shot = mockShots.find(s => s.id === id);
        if (!shot) throw new Error('Shot not found');
        return shot;
      }
    },
    enabled: !!id
  });
};

export const useCreateShot = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (newShot: Omit<Shot, 'id' | 'created_at' | 'updated_at'>) => {
      const { data } = await apiClient.post<Shot>('/api/v1/shots/', newShot);
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
      const { data } = await apiClient.patch<Shot>(`/api/v1/shots/${id}`, updateData);
      return data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['shots', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['shots'] });
    }
  });
};