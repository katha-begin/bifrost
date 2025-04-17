'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import Cookies from 'js-cookie';

export default function SimpleHomePage() {
  const [user, setUser] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    // Try to get user from localStorage
    const storedUser = localStorage.getItem('bifrost_user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        console.error('Failed to parse user from localStorage', e);
      }
    }
    
    setIsLoading(false);
  }, []);
  
  const handleLogout = () => {
    // Clear authentication
    Cookies.remove('auth_token');
    localStorage.removeItem('bifrost_auth_token');
    localStorage.removeItem('bifrost_user');
    localStorage.removeItem('bifrost_auth_state');
    
    // Redirect to login
    window.location.href = '/static-login.html';
  };
  
  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <div>Loading...</div>
      </div>
    );
  }
  
  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      {/* Header */}
      <header style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        padding: '16px',
        backgroundColor: '#1f2937',
        color: 'white',
        borderRadius: '8px',
        marginBottom: '24px'
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
      <main>
        <h1 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '24px' }}>
          Production Overview
        </h1>
        
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', 
          gap: '24px',
          marginBottom: '32px'
        }}>
          {/* Assets Card */}
          <div style={{ 
            backgroundColor: 'white', 
            borderRadius: '8px', 
            padding: '24px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
          }}>
            <h2 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '16px' }}>Assets</h2>
            <p style={{ fontSize: '36px', fontWeight: 'bold', color: '#3b82f6', marginBottom: '8px' }}>5</p>
            <p style={{ color: '#6b7280', marginBottom: '16px' }}>Total Assets</p>
            <button style={{
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              padding: '8px 16px',
              cursor: 'pointer'
            }}>
              View All Assets
            </button>
          </div>
          
          {/* Shots Card */}
          <div style={{ 
            backgroundColor: 'white', 
            borderRadius: '8px', 
            padding: '24px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
          }}>
            <h2 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '16px' }}>Shots</h2>
            <p style={{ fontSize: '36px', fontWeight: 'bold', color: '#3b82f6', marginBottom: '8px' }}>5</p>
            <p style={{ color: '#6b7280', marginBottom: '16px' }}>Total Shots</p>
            <button style={{
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              padding: '8px 16px',
              cursor: 'pointer'
            }}>
              View All Shots
            </button>
          </div>
        </div>
        
        {/* Recent Activity */}
        <div style={{ 
          backgroundColor: 'white', 
          borderRadius: '8px', 
          padding: '24px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
        }}>
          <h2 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '16px' }}>Recent Activity</h2>
          
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
                padding: '16px 0',
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
      </main>
    </div>
  );
}
