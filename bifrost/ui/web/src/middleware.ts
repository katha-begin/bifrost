import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Define paths that don't require authentication
const PUBLIC_PATHS = [
  '/login',
  '/register',
  '/forgot-password',
  '/reset-password',
  '/auth/check-email',
  '/auth/login',
  '/auth/register',
  '/auth/reset-password',
  '/auth/reset-password/confirm'
];

// Helper function to check if the path is public
const isPublicPath = (path: string) =>
  PUBLIC_PATHS.some(publicPath =>
    path.startsWith(publicPath) || path.startsWith(`/api${publicPath}`)
  );

export async function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname;

  // Allow access to public files and paths
  if (
    path.startsWith('/_next') ||
    path.startsWith('/static') ||
    path.startsWith('/api/public') ||
    path.includes('.') ||
    isPublicPath(path) ||
    path === '/' // Allow direct access to the main page
  ) {
    return NextResponse.next();
  }

  // Check for auth token
  const token = request.cookies.get('auth_token');

  // Redirect to static login page if no token is present
  if (!token) {
    // Use the static HTML login page instead of the React component
    const loginUrl = new URL('/static-login.html', request.url);
    return NextResponse.redirect(loginUrl);
  }

  // Continue with the request if token exists
  return NextResponse.next();
}

// Configure paths that trigger the middleware
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * 1. /_next/static (static files)
     * 2. /_next/image (image optimization files)
     * 3. /favicon.ico (favicon file)
     * 4. Files with extensions (.jpg, .png, etc)
     */
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};