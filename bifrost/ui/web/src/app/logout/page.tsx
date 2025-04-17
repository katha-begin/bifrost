'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import Cookies from 'js-cookie';

export default function LogoutPage() {
  const router = useRouter();
  const logout = useAuthStore(state => state.logout);

  useEffect(() => {
    // Clear authentication
    logout();
    
    // Remove auth cookie manually to be sure
    Cookies.remove('auth_token');
    
    // Redirect to login page
    setTimeout(() => {
      router.push('/login');
    }, 100);
  }, [logout, router]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <p>Logging out...</p>
    </div>
  );
}
