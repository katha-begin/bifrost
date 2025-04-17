'use client';

import { PropsWithChildren, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import Cookies from 'js-cookie';

export function AuthProvider({ children }: PropsWithChildren) {
  const router = useRouter();
  const pathname = usePathname();
  const { isAuthenticated, user } = useAuthStore();

  useEffect(() => {
    // Check for auth token in cookies
    const token = Cookies.get('auth_token');
    console.log('AuthProvider: Checking auth state', { token, isAuthenticated, pathname });

    const publicPaths = ['/login', '/register', '/forgot-password', '/reset-password'];
    const isPublicPath = publicPaths.some(pp => pathname?.startsWith(pp));

    if (!token && !isPublicPath) {
      console.log('AuthProvider: No token found, redirecting to login');
      router.push('/login');
      return;
    }

    if (token && isPublicPath) {
      console.log('AuthProvider: Token found on public path, redirecting to home');
      router.push('/');
      return;
    }
  }, [isAuthenticated, pathname, router]);

  return <>{children}</>;
}