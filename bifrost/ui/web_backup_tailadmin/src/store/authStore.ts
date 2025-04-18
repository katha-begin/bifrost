import { create } from 'zustand';
import { User } from '../types';
import { apiClient } from '../services/api-client';
import Cookies from 'js-cookie';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  initAuth: () => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  resetPassword: (email: string) => Promise<void>;
  confirmPasswordReset: (token: string, newPassword: string) => Promise<void>;
  checkUserExists: (email: string) => Promise<boolean>;
  clearError: () => void;
}

// For development/mock API
const MOCK_USER = {
  id: 'dev-user-123',
  username: 'developer',
  email: 'dev@example.com',
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString()
};

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: typeof window !== 'undefined' ? Cookies.get('auth_token') || null : null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  initAuth: async () => {
    const token = Cookies.get('auth_token');
    
    if (!token) {
      // No token found, user is not authenticated
      set({ isAuthenticated: false, isLoading: false });
      return;
    }
    
    // For development/mock API, create a user from the token
    if (process.env.NODE_ENV !== 'production') {
      set({ 
        user: MOCK_USER, 
        token, 
        isAuthenticated: true, 
        isLoading: false 
      });
      return;
    }
    
    // For production, validate the token with the server
    try {
      const response = await apiClient.get('/auth/me');
      set({ 
        user: response.data, 
        token, 
        isAuthenticated: true, 
        isLoading: false 
      });
    } catch (error) {
      // Token is invalid
      Cookies.remove('auth_token');
      set({ user: null, token: null, isAuthenticated: false, isLoading: false });
    }
  },

  login: async (email: string, password: string) => {
    try {
      set({ isLoading: true, error: null });
      
      // For development/mock API
      if (process.env.NODE_ENV !== 'production') {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Set mock data
        const mockToken = 'mock-jwt-token-for-development';
        Cookies.set('auth_token', mockToken, {
          expires: 7,
          secure: false,
          sameSite: 'strict'
        });
        
        set({ 
          user: MOCK_USER, 
          token: mockToken, 
          isAuthenticated: true, 
          isLoading: false 
        });
        return;
      }

      // Production API call
      const response = await apiClient.post('/auth/login', { email, password });
      const { token, user } = response.data;
      
      Cookies.set('auth_token', token, {
        expires: 7,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict'
      });
      
      set({ user, token, isAuthenticated: true, isLoading: false });
    } catch (error: any) {
      const message = error.response?.data?.message || 'Login failed';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  register: async (username: string, email: string, password: string) => {
    try {
      set({ isLoading: true, error: null });
      
      // For development/mock API
      if (process.env.NODE_ENV !== 'production') {
        await new Promise(resolve => setTimeout(resolve, 500));
        const mockToken = 'mock-jwt-token-for-development';
        const mockUser = { ...MOCK_USER, username, email };
        
        Cookies.set('auth_token', mockToken, {
          expires: 7,
          secure: false,
          sameSite: 'strict'
        });
        
        set({ 
          user: mockUser, 
          token: mockToken, 
          isAuthenticated: true, 
          isLoading: false 
        });
        return;
      }

      const response = await apiClient.post('/auth/register', { username, email, password });
      const { token, user } = response.data;
      
      Cookies.set('auth_token', token, {
        expires: 7,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict'
      });
      
      set({ user, token, isAuthenticated: true, isLoading: false });
    } catch (error: any) {
      const message = error.response?.data?.message || 'Registration failed';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  logout: () => {
    Cookies.remove('auth_token');
    set({ user: null, token: null, isAuthenticated: false });
  },

  resetPassword: async (email: string) => {
    try {
      set({ isLoading: true, error: null });
      if (process.env.NODE_ENV !== 'production') {
        await new Promise(resolve => setTimeout(resolve, 500));
        set({ isLoading: false });
        return;
      }
      await apiClient.post('/auth/reset-password', { email });
      set({ isLoading: false });
    } catch (error: any) {
      const message = error.response?.data?.message || 'Password reset request failed';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  confirmPasswordReset: async (token: string, newPassword: string) => {
    try {
      set({ isLoading: true, error: null });
      if (process.env.NODE_ENV !== 'production') {
        await new Promise(resolve => setTimeout(resolve, 500));
        set({ isLoading: false });
        return;
      }
      await apiClient.post('/auth/reset-password/confirm', { token, newPassword });
      set({ isLoading: false });
    } catch (error: any) {
      const message = error.response?.data?.message || 'Password reset failed';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  checkUserExists: async (email: string) => {
    if (process.env.NODE_ENV !== 'production') {
      await new Promise(resolve => setTimeout(resolve, 500));
      return email === MOCK_USER.email;
    }
    try {
      const response = await apiClient.post('/auth/check-email', { email });
      return response.data.exists;
    } catch (error) {
      return false;
    }
  },

  clearError: () => set({ error: null }),
}));