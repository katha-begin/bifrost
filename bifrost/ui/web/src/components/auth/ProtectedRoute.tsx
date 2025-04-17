'use client';

import { ReactNode, useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import LoadingSpinner from '../LoadingSpinner';

interface ProtectedRouteProps {
  children: ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { isAuthenticated, token } = useAuthStore();
  const [isValidating, setIsValidating] = useState(true);

  useEffect(() => {
    const publicPaths = ['/login', '/register', '/forgot-password', '/reset-password'];
    const isPublicPath = publicPaths.some(path => pathname?.startsWith(path));

    const validateAuth = async () => {
      try {
        if (!token && !isPublicPath) {
          router.push(`/login?returnUrl=${encodeURIComponent(pathname || '/')}`);
        } else if (token && isPublicPath) {
          router.push('/');
        }
      } finally {
        setIsValidating(false);
      }
    };

    validateAuth();
  }, [token, pathname, router]);

  // Show loading spinner while validating authentication
  if (isValidating) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  // For public routes, always render children
  if (pathname?.startsWith('/login') || 
      pathname?.startsWith('/register') || 
      pathname?.startsWith('/forgot-password') ||
      pathname?.startsWith('/reset-password')) {
    return <>{children}</>;
  }

  // For protected routes, only render when authenticated
  return isAuthenticated ? <>{children}</> : null;
}