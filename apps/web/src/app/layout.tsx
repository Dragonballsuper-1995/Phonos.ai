import type { Metadata } from 'next';
import { CSPostHogProvider } from './providers';
import Nav from '@/components/layout/Nav';
import './globals.css';

export const metadata: Metadata = {
  title: 'Phonos.ai — Smartphone Intelligence for India',
  description:
    'AI-powered smartphone intelligence and recommendation system for the Indian market. Precision filtering, multi-factor ranking, and explainable choices.',
  keywords: ['smartphone recommendation', 'mobile phone advisor', 'india smartphone buying guide', 'phonos ai'],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,400..700;1,9..40,400..700&family=JetBrains+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <CSPostHogProvider>
          <Nav />
          {children}
        </CSPostHogProvider>
      </body>
    </html>
  );
}
