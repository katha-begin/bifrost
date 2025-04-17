import axios, { AxiosError } from 'axios';
import { useAuthStore } from '@/store/authStore';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Add request interceptor for authentication
apiClient.interceptors.request.use(
  (config) => {
    // For development/mock API, add a mock token
    if (process.env.NODE_ENV !== 'production') {
      config.headers.Authorization = 'Bearer mock-jwt-token-for-development';
    }
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Clear any existing auth state
      const authStore = useAuthStore.getState();
      authStore.logout();
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    
    // Add additional error information for debugging
    const enhancedError = {
      ...error,
      message: error.response?.data?.message || error.message,
      timestamp: new Date().toISOString(),
      url: error.config?.url,
      method: error.config?.method,
    };
    
    console.error('API Error:', enhancedError);
    return Promise.reject(enhancedError);
  }
);