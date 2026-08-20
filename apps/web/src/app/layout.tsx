import type { Metadata } from 'next';
import { Barlow_Condensed, DM_Sans, JetBrains_Mono } from 'next/font/google';
import { CSPostHogProvider } from './providers';
import Nav from '@/components/layout/Nav';
import './globals.css';

const barlowCondensed = Barlow_Condensed({
  subsets: ['latin'],
  weight: ['600', '700', '800'],
  variable: '--font-barlow-condensed',
  display: 'swap',
});

const dmSans = DM_Sans({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-dm-sans',
  display: 'swap',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  weight: ['400', '500', '600'],
  variable: '--font-jetbrains-mono',
  display: 'swap',
});

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
    <html
      lang="en"
      suppressHydrationWarning
      className={`${barlowCondensed.variable} ${dmSans.variable} ${jetbrainsMono.variable}`}
    >
      <body>
        <CSPostHogProvider>
          <Nav />
          {children}
        </CSPostHogProvider>
      </body>
    </html>
  );
}
