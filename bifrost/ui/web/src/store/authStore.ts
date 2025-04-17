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
  login: (email: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  resetPassword: (email: string) => Promise<void>;
  confirmPasswordReset: (token: string, newPassword: string) => Promise<void>;
  checkUserExists: (email: string) => Promise<boolean>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: typeof window !== 'undefined' ? Cookies.get('auth_token') || null : null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (email: string, password: string) => {
    try {
      set({ isLoading: true, error: null });
      const response = await apiClient.post('/auth/login', { email, password });
      const { token, user } = response.data;
      
      Cookies.set('auth_token', token, { 
        expires: 7, // 7 days
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
      await apiClient.post('/auth/reset-password/confirm', {
        token,
        newPassword
      });
      set({ isLoading: false });
    } catch (error: any) {
      const message = error.response?.data?.message || 'An error occurred while resetting password';
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  checkUserExists: async (email: string) => {
    try {
      const response = await apiClient.post('/auth/check-email', { email });
      return response.data.exists;
    } catch (error) {
      return false;
    }
  },

  clearError: () => set({ error: null }),
}));