'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import Link from 'next/link';
import Cookies from 'js-cookie';

export default function SimpleHomePage() {
  const router = useRouter();
  const { user, isAuthenticated, logout } = useAuthStore();
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    const checkAuth = () => {
      console.log('Checking auth state:', { user, isAuthenticated });
      
      // Short delay to ensure auth state is initialized
      setTimeout(() => {
        if (!isAuthenticated) {
          console.log('No authenticated user found, redirecting to login');
          router.push('/login');
          return;
        }
        setIsLoading(false);
      }, 500);
    };
    
    checkAuth();
  }, [user, isAuthenticated, router]);
  
  const handleLogout = () => {
    logout();
    router.push('/login');
  };
  
  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <div>Loading...</div>
      </div>
    );
  }
  
  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column',
      minHeight: '100vh',
      width: '100%',
      backgroundColor: '#f3f4f6'
    }}>
      {/* Header */}
      <header style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        padding: '0 24px',
        height: '64px',
        backgroundColor: '#1f2937',
        color: 'white',
        width: '100%',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <div style={{ fontSize: '24px', fontWeight: 'bold' }}>Bifrost</div>
        
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <div style={{ marginRight: '16px' }}>
            Welcome, {user?.username || 'User'}
          </div>
          <button 
            onClick={handleLogout}
            style={{
              backgroundColor: '#ef4444',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              padding: '8px 16px',
              cursor: 'pointer'
            }}
          >
            Logout
          </button>
        </div>
      </header>
      
      {/* Main Content */}
      <main style={{ 
        display: 'flex', 
        flex: '1',
        padding: '24px'
      }}>
        {/* Sidebar */}
        <div style={{
          width: '250px',
          backgroundColor: 'white',
          borderRadius: '8px',
          marginRight: '24px',
          padding: '16px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.05)'
        }}>
          <div style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '16px' }}>
            Main Menu
          </div>
          
          <nav>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
              {[
                { name: 'Dashboard', active: true },
                { name: 'Assets', active: false },
                { name: 'Shots', active: false },
                { name: 'Tasks', active: false },
                { name: 'Reviews', active: false },
                { name: 'Settings', active: false }
              ].map((item, index) => (
                <li key={index} style={{ marginBottom: '8px' }}>
                  <a 
                    href="#" 
                    style={{ 
                      display: 'block', 
                      padding: '10px 16px', 
                      borderRadius: '4px', 
                      textDecoration: 'none',
                      color: item.active ? 'white' : '#4b5563',
                      backgroundColor: item.active ? '#3b82f6' : 'transparent',
                      fontWeight: item.active ? 'bold' : 'normal'
                    }}
                  >
                    {item.name}
                  </a>
                </li>
              ))}
            </ul>
          </nav>
        </div>
        
        {/* Dashboard Content */}
        <div style={{ flex: 1 }}>
          <h1 style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '24px', color: '#111827' }}>
            Production Overview
          </h1>
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', 
            gap: '24px',
            marginBottom: '32px'
          }}>
            {/* Stats Cards */}
            {[
              { title: 'Assets', count: 5, color: '#3b82f6', link: 'View All Assets' },
              { title: 'Shots', count: 5, color: '#10b981', link: 'View All Shots' },
              { title: 'Tasks', count: 12, color: '#f59e0b', link: 'View All Tasks' },
              { title: 'Reviews', count: 3, color: '#8b5cf6', link: 'View All Reviews' }
            ].map((item, index) => (
              <div key={index} style={{ 
                backgroundColor: 'white', 
                borderRadius: '8px', 
                padding: '20px',
                boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)'
              }}>
                <h2 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '12px', color: '#374151' }}>{item.title}</h2>
                <p style={{ fontSize: '32px', fontWeight: 'bold', color: item.color, marginBottom: '8px' }}>{item.count}</p>
                <p style={{ color: '#6b7280', marginBottom: '16px' }}>Total {item.title}</p>
                <button style={{
                  backgroundColor: item.color,
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  padding: '8px 16px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}>
                  {item.link}
                </button>
              </div>
            ))}
          </div>
          
          {/* Recent Activity */}
          <div style={{ 
            backgroundColor: 'white', 
            borderRadius: '8px', 
            padding: '24px',
            boxShadow: '0 2px 4px rgba(0, 0, 0, 0.05)'
          }}>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              marginBottom: '16px'
            }}>
              <h2 style={{ fontSize: '18px', fontWeight: 'bold', color: '#374151' }}>Recent Activity</h2>
              <button style={{
                backgroundColor: 'transparent',
                color: '#3b82f6',
                border: '1px solid #3b82f6',
                borderRadius: '4px',
                padding: '6px 12px',
                cursor: 'pointer',
                fontSize: '14px'
              }}>
                View All
              </button>
            </div>
            
            <div>
              {[
                { id: 1, name: 'Character - Hero', type: 'Asset updated', date: '2023-10-05' },
                { id: 2, name: 'Environment - Forest', type: 'Asset updated', date: '2023-10-10' },
                { id: 3, name: 'Prop - Magic Sword', type: 'Asset updated', date: '2023-10-12' },
                { id: 4, name: 'Vehicle - Spaceship', type: 'Asset updated', date: '2023-10-08' },
                { id: 5, name: 'Character - Villain', type: 'Asset updated', date: '2023-10-07' }
              ].map(item => (
                <div key={item.id} style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  padding: '12px 0',
                  borderBottom: '1px solid #e5e7eb'
                }}>
                  <div>
                    <p style={{ fontWeight: '500', color: '#111827' }}>{item.name}</p>
                    <p style={{ fontSize: '14px', color: '#6b7280' }}>{item.type}</p>
                  </div>
                  <span style={{ 
                    fontSize: '14px', 
                    color: '#6b7280',
                    backgroundColor: '#f3f4f6',
                    padding: '4px 8px',
                    borderRadius: '4px'
                  }}>
                    {item.date}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
      
      {/* Footer */}
      <footer style={{
        backgroundColor: 'white',
        borderTop: '1px solid #e5e7eb',
        padding: '16px 24px',
        color: '#6b7280',
        fontSize: '14px',
        textAlign: 'center'
      }}>
        © 2025 Bifrost Animation Asset Management System
      </footer>
    </div>
  );
}
