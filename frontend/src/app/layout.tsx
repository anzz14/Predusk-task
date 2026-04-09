import type { Metadata } from 'next';
import { AuthProvider } from '@/context/AuthContext';
import './globals.css';

export const metadata: Metadata = {
  title: 'SEO Analyzer',
  description: 'Bulk SEO content analyzer',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          {children}
          {/* Toaster for global toast notifications - will be implemented after shadcn setup */}
        </AuthProvider>
      </body>
    </html>
  );
}