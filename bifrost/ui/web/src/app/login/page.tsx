'use client';

import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/store/authStore';
import Cookies from 'js-cookie';

// Temporary mock user for development
const MOCK_USER = {
  id: 'dev-user-123',
  username: 'developer',
  email: 'dev@example.com',
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString()
};

// Temporary mock token
const MOCK_TOKEN = 'mock-jwt-token-for-development';

export default function LoginPage() {
  const router = useRouter();
  const { error, clearError } = useAuthStore();
  const [formData, setFormData] = useState({
    email: 'dev@example.com',
    password: 'password',
    rememberMe: true
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Add console logs for debugging
  console.log('Login page rendered');
  console.log('Current auth state:', useAuthStore.getState());

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    console.log('Login form submitted');
    setIsSubmitting(true);

    try {
      console.log('Setting mock authentication...');
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 800));

      // Set the mock token in cookies
      console.log('Setting auth cookie...');
      Cookies.set('auth_token', MOCK_TOKEN, {
        expires: 7, // 7 days
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict'
      });
      console.log('Cookie set:', Cookies.get('auth_token'));

      // Update the auth store directly
      console.log('Updating auth store...');
      const authStore = useAuthStore.getState();
      authStore.user = MOCK_USER;
      authStore.token = MOCK_TOKEN;
      authStore.isAuthenticated = true;
      console.log('Auth store updated:', useAuthStore.getState());

      // Navigate to home page
      console.log('Navigating to home page...');
      router.push('/');
    } catch (error) {
      console.error('Login failed:', error);
      alert('Login failed: ' + (error instanceof Error ? error.message : String(error)));
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900">
            Sign in to Bifrost
          </h2>
          <p className="mt-2 text-gray-600">Enter your credentials to access your account</p>
        </div>

        <form className="space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="p-4 bg-red-50 border-l-4 border-red-500 text-red-700 rounded">
              <p>{error}</p>
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                value={formData.email}
                onChange={(e) => {
                  clearError();
                  setFormData({ ...formData, email: e.target.value });
                }}
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                value={formData.password}
                onChange={(e) => {
                  clearError();
                  setFormData({ ...formData, password: e.target.value });
                }}
              />
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <input
                id="remember-me"
                name="remember-me"
                type="checkbox"
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                checked={formData.rememberMe}
                onChange={(e) => setFormData({ ...formData, rememberMe: e.target.checked })}
              />
              <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-900">
                Remember me
              </label>
            </div>

            <div className="text-sm">
              <Link
                href="/forgot-password"
                className="font-medium text-blue-600 hover:text-blue-500"
              >
                Forgot password?
              </Link>
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-blue-300"
            >
              {isSubmitting ? 'Signing in...' : 'Sign in'}
            </button>
          </div>

          <div className="text-center mt-4 pt-4 border-t border-gray-200">
            <span className="text-sm text-gray-600">Don't have an account? </span>
            <Link
              href="/register"
              className="font-medium text-blue-600 hover:text-blue-500"
            >
              Register here
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}