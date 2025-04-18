'use client';
import { useEffect } from 'react';
import { useAuthStore } from '@/store/authStore';
import { ClientProviders } from '@/components/ClientProviders';
import { ErrorBoundary } from '@/components/ErrorBoundary';

export function ClientLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, isAuthenticated, initAuth } = useAuthStore();
  
  useEffect(() => {
    // Initialize authentication when component mounts
    initAuth().then(() => {
      console.log('Authentication initialized');
    }).catch(error => {
      console.error('Error initializing authentication:', error);
    });
  }, []);
  
  useEffect(() => {
    console.log('ClientLayout mounted', { isAuthenticated, user });
  }, [isAuthenticated, user]);
  
  return (
    <ErrorBoundary>
      <ClientProviders>{children}</ClientProviders>
    </ErrorBoundary>
  );
}