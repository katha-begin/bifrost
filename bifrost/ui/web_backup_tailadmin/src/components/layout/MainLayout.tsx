'use client';

import { ReactNode } from 'react';
import { usePathname } from 'next/navigation';
import Header from './Header';
import { useAuthStore } from '@/store/authStore';

interface MainLayoutProps {
  children: ReactNode;
}

export default function MainLayout({ children }: MainLayoutProps) {
  const pathname = usePathname();
  const { isAuthenticated } = useAuthStore();
  
  // Don't show header on login and other public pages
  const isPublicPage = ['/login', '/register', '/forgot-password', '/reset-password', '/logout'].some(
    path => pathname?.startsWith(path)
  );

  return (
    <div className="min-h-screen flex flex-col">
      {isAuthenticated && !isPublicPage && <Header />}
      <main className="flex-grow">
        {children}
      </main>
    </div>
  );
}
