'use client';

import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';
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

export default function SimpleLoginPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  
  console.log('Simple login page rendered');

  const handleLogin = async () => {
    try {
      console.log('Login button clicked');
      setIsLoading(true);
      
      // Set the mock token in cookies
      console.log('Setting auth cookie...');
      Cookies.set('auth_token', MOCK_TOKEN, { 
        expires: 7, // 7 days
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict'
      });
      
      // Update the auth store directly
      console.log('Updating auth store...');
      const authStore = useAuthStore.getState();
      authStore.user = MOCK_USER;
      authStore.token = MOCK_TOKEN;
      authStore.isAuthenticated = true;
      
      // Navigate to home page
      console.log('Navigating to home page...');
      router.push('/');
    } catch (error) {
      console.error('Login failed:', error);
      alert('Login failed: ' + (error instanceof Error ? error.message : String(error)));
      setIsLoading(false);
    }
  };

  return (
    <div style={{ 
      padding: '20px', 
      maxWidth: '400px', 
      margin: '100px auto', 
      border: '1px solid #ccc',
      borderRadius: '8px',
      backgroundColor: 'white'
    }}>
      <h1 style={{ textAlign: 'center', marginBottom: '20px' }}>Bifrost Login</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '5px' }}>Email:</label>
        <input 
          type="email" 
          value="dev@example.com" 
          readOnly
          style={{ 
            width: '100%', 
            padding: '8px', 
            border: '1px solid #ccc', 
            borderRadius: '4px' 
          }} 
        />
      </div>
      
      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '5px' }}>Password:</label>
        <input 
          type="password" 
          value="password" 
          readOnly
          style={{ 
            width: '100%', 
            padding: '8px', 
            border: '1px solid #ccc', 
            borderRadius: '4px' 
          }} 
        />
      </div>
      
      <button 
        onClick={handleLogin}
        disabled={isLoading}
        style={{ 
          width: '100%', 
          padding: '10px', 
          backgroundColor: '#3b82f6', 
          color: 'white', 
          border: 'none', 
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        {isLoading ? 'Logging in...' : 'Login'}
      </button>
      
      <p style={{ marginTop: '20px', textAlign: 'center', fontSize: '14px' }}>
        This is a simplified login page for demonstration purposes.
      </p>
    </div>
  );
}
