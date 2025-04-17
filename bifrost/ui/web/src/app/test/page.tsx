'use client';

import React, { useState } from 'react';

export default function TestPage() {
  const [count, setCount] = useState(0);
  
  console.log('TestPage rendering with count:', count);
  
  return (
    <div style={{ 
      maxWidth: '500px', 
      margin: '100px auto', 
      padding: '20px',
      backgroundColor: 'white',
      borderRadius: '8px',
      boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
    }}>
      <h1>React Test Page</h1>
      <p>This is a minimal React component to test if React is working properly.</p>
      
      <div style={{ margin: '20px 0' }}>
        <p>Count: {count}</p>
        <button 
          onClick={() => setCount(count + 1)}
          style={{
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            padding: '8px 16px',
            cursor: 'pointer',
            marginRight: '8px'
          }}
        >
          Increment
        </button>
        <button 
          onClick={() => setCount(0)}
          style={{
            backgroundColor: '#ef4444',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            padding: '8px 16px',
            cursor: 'pointer'
          }}
        >
          Reset
        </button>
      </div>
      
      <div style={{ marginTop: '20px' }}>
        <a 
          href="/debug.html"
          style={{
            display: 'inline-block',
            marginRight: '10px',
            color: '#3b82f6',
            textDecoration: 'none'
          }}
        >
          Debug Console
        </a>
        <a 
          href="/static-dashboard.html"
          style={{
            display: 'inline-block',
            color: '#3b82f6',
            textDecoration: 'none'
          }}
        >
          Static Dashboard
        </a>
      </div>
    </div>
  );
}
