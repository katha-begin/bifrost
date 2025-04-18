'use client';

import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Input } from '@/components/ui/Input';
import { useAuthStore } from '@/store/authStore';
import { z } from 'zod';

const registerSchema = z.object({
  username: z.string().min(3, 'Username must be at least 3 characters'),
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string()
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"]
});

type RegisterForm = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const router = useRouter();
  const { register, checkUserExists, isLoading, error, clearError } = useAuthStore();
  const [formData, setFormData] = useState<RegisterForm>({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [formErrors, setFormErrors] = useState<{[K in keyof RegisterForm]?: string}>({});

  const validateForm = async () => {
    try {
      const parsed = registerSchema.parse(formData);
      // Check if user exists
      const exists = await checkUserExists(parsed.email);
      if (exists) {
        setFormErrors({ email: 'User with this email already exists' });
        return false;
      }
      setFormErrors({});
      return true;
    } catch (error) {
      if (error instanceof z.ZodError) {
        const errors = error.errors.reduce((acc, curr) => {
          const path = curr.path[0] as keyof RegisterForm;
          acc[path] = curr.message;
          return acc;
        }, {} as {[K in keyof RegisterForm]?: string});
        setFormErrors(errors);
      }
      return false;
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearError();
    
    if (await validateForm()) {
      try {
        await register(formData.username, formData.email, formData.password);
        router.push('/');
      } catch (error) {
        // Error is handled by the store
      }
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="flex">
                <div className="text-sm text-red-700">{error}</div>
              </div>
            </div>
          )}
          <div className="rounded-md shadow-sm space-y-4">
            <Input
              label="Username"
              type="text"
              required
              value={formData.username}
              error={formErrors.username}
              onChange={(e) => {
                clearError();
                setFormData({ ...formData, username: e.target.value });
              }}
            />
            <Input
              label="Email address"
              type="email"
              required
              value={formData.email}
              error={formErrors.email}
              onChange={(e) => {
                clearError();
                setFormData({ ...formData, email: e.target.value });
              }}
            />
            <Input
              label="Password"
              type="password"
              required
              value={formData.password}
              error={formErrors.password}
              onChange={(e) => {
                clearError();
                setFormData({ ...formData, password: e.target.value });
              }}
            />
            <Input
              label="Confirm Password"
              type="password"
              required
              value={formData.confirmPassword}
              error={formErrors.confirmPassword}
              onChange={(e) => {
                clearError();
                setFormData({ ...formData, confirmPassword: e.target.value });
              }}
            />
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-blue-300"
            >
              {isLoading ? 'Creating account...' : 'Create account'}
            </button>
          </div>

          <div className="text-center">
            <span className="text-sm text-gray-600">Already have an account? </span>
            <Link
              href="/login"
              className="font-medium text-blue-600 hover:text-blue-500"
            >
              Sign in
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}