import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import '@/styles/globals.css';
import { ClientProviders } from '@/components/ClientProviders';
import { AuthProvider } from '@/components/auth/AuthProvider';
import MainLayout from '@/components/layout/MainLayout';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Bifrost Production Management',
  description: 'Animation asset and production management system',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <ClientProviders>
          <AuthProvider>
            <MainLayout>{children}</MainLayout>
          </AuthProvider>
        </ClientProviders>
      </body>
    </html>
  );
}
