'use client';

import { FormEvent, useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Input } from '@/components/ui/Input';
import { useAuthStore } from '@/store/authStore';
import { z } from 'zod';

const passwordSchema = z.object({
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string()
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"]
});

type PasswordForm = z.infer<typeof passwordSchema>;

export default function ResetPasswordPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { confirmPasswordReset, isLoading, error, clearError } = useAuthStore();
  const [formData, setFormData] = useState<PasswordForm>({
    password: '',
    confirmPassword: ''
  });
  const [formErrors, setFormErrors] = useState<{[K in keyof PasswordForm]?: string}>({});

  // Get token from URL
  const token = searchParams.get('token');

  useEffect(() => {
    if (!token) {
      router.push('/login');
    }
  }, [token, router]);

  const validateForm = () => {
    try {
      passwordSchema.parse(formData);
      setFormErrors({});
      return true;
    } catch (error) {
      if (error instanceof z.ZodError) {
        const errors = error.errors.reduce((acc, curr) => {
          const path = curr.path[0] as keyof PasswordForm;
          acc[path] = curr.message;
          return acc;
        }, {} as {[K in keyof PasswordForm]?: string});
        setFormErrors(errors);
      }
      return false;
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearError();

    if (validateForm() && token) {
      try {
        await confirmPasswordReset(token, formData.password);
        router.push('/login');
      } catch (error) {
        // Error is handled by the store
      }
    }
  };

  if (!token) {
    return null;
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Reset your password
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
              label="New Password"
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
              label="Confirm New Password"
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
              {isLoading ? 'Resetting password...' : 'Reset password'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}