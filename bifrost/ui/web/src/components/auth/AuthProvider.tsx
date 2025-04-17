'use client';

import { ReactNode } from 'react';
import { ProtectedRoute } from './ProtectedRoute';

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  return (
    <ProtectedRoute>
      {children}
    </ProtectedRoute>
  );
}