'use client';

import React, { useState, useEffect } from 'react';
import { useAuthStore } from '@/store/authStore';

// Error boundary component
class ErrorBoundary extends React.Component<
  { children: React.ReactNode; name: string },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: { children: React.ReactNode; name: string }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error(`Error in ${this.props.name}:`, error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          padding: '16px',
          margin: '16px 0',
          backgroundColor: '#fee2e2',
          border: '1px solid #ef4444',
          borderRadius: '8px'
        }}>
          <h3 style={{ color: '#b91c1c', marginTop: 0 }}>Error in {this.props.name}</h3>
          <p>{this.state.error?.message || 'Unknown error'}</p>
          <pre style={{
            backgroundColor: '#fff',
            padding: '8px',
            borderRadius: '4px',
            overflow: 'auto',
            maxHeight: '200px'
          }}>
            {this.state.error?.stack}
          </pre>
        </div>
      );
    }

    return this.props.children;
  }
}

// Test components to isolate issues
const TestAuthStore = () => {
  const [error, setError] = useState<string | null>(null);
  const [authState, setAuthState] = useState<any>(null);

  useEffect(() => {
    try {
      const state = useAuthStore.getState();
      setAuthState(state);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }, []);

  return (
    <div>
      <h3>Auth Store Test</h3>
      {error ? (
        <div style={{ color: 'red' }}>Error: {error}</div>
      ) : (
        <pre>{JSON.stringify(authState, null, 2)}</pre>
      )}
    </div>
  );
};

const TestCookies = () => {
  const [cookies, setCookies] = useState<string>('');

  useEffect(() => {
    setCookies(document.cookie);
  }, []);

  return (
    <div>
      <h3>Cookies Test</h3>
      <pre>{cookies || 'No cookies found'}</pre>
    </div>
  );
};

const TestLocalStorage = () => {
  const [storage, setStorage] = useState<Record<string, string>>({});

  useEffect(() => {
    const items: Record<string, string> = {};
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key) {
        items[key] = localStorage.getItem(key) || '';
      }
    }
    setStorage(items);
  }, []);

  return (
    <div>
      <h3>LocalStorage Test</h3>
      <pre>{JSON.stringify(storage, null, 2)}</pre>
    </div>
  );
};

const TestEnvironment = () => {
  return (
    <div>
      <h3>Environment Test</h3>
      <pre>
        {`
Node Environment: ${process.env.NODE_ENV}
Next Public API URL: ${process.env.NEXT_PUBLIC_API_URL || 'Not set'}
        `}
      </pre>
    </div>
  );
};

export default function DiagnosticPage() {
  const [browserInfo, setBrowserInfo] = useState<string>('');

  useEffect(() => {
    setBrowserInfo(`
User Agent: ${navigator.userAgent}
Window Size: ${window.innerWidth}x${window.innerHeight}
Device Pixel Ratio: ${window.devicePixelRatio}
    `);

    // Log React version
    console.log('React version:', React.version);

    // Log any global errors
    window.onerror = (message, source, lineno, colno, error) => {
      console.error('Global error:', { message, source, lineno, colno, error });
    };

    // Log unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      console.error('Unhandled promise rejection:', event.reason);
    });
  }, []);

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      <h1>Bifrost Diagnostic Page</h1>
      <p>This page helps diagnose rendering issues in the application.</p>

      <div style={{ marginBottom: '32px' }}>
        <h2>Browser Information</h2>
        <pre>{browserInfo}</pre>
      </div>

      <ErrorBoundary name="Auth Store">
        <div style={{ marginBottom: '32px' }}>
          <TestAuthStore />
        </div>
      </ErrorBoundary>

      <ErrorBoundary name="Cookies">
        <div style={{ marginBottom: '32px' }}>
          <TestCookies />
        </div>
      </ErrorBoundary>

      <ErrorBoundary name="LocalStorage">
        <div style={{ marginBottom: '32px' }}>
          <TestLocalStorage />
        </div>
      </ErrorBoundary>

      <ErrorBoundary name="Environment">
        <div style={{ marginBottom: '32px' }}>
          <TestEnvironment />
        </div>
      </ErrorBoundary>

      <div style={{ marginTop: '32px' }}>
        <h2>Next Steps</h2>
        <p>Check the browser console (F12) for additional error messages.</p>
        <p>
          <a
            href="/static-login.html"
            style={{
              display: 'inline-block',
              padding: '8px 16px',
              backgroundColor: '#3b82f6',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '4px',
              marginRight: '16px'
            }}
          >
            Go to Static Login
          </a>
          <a
            href="/static-dashboard.html"
            style={{
              display: 'inline-block',
              padding: '8px 16px',
              backgroundColor: '#10b981',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '4px'
            }}
          >
            Go to Static Dashboard
          </a>
        </p>
      </div>
    </div>
  );
}
