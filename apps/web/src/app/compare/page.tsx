import { Suspense } from 'react';
import type { Metadata } from 'next';
import CompareView from '@/components/compare/CompareView';
import LoadingState from '@/components/ui/LoadingState';

export const metadata: Metadata = {
  title: 'Compare Smartphones — Phonos.ai',
  description: 'Side-by-side technical matrix comparing performance, cameras, battery life, and live Indian pricing.',
};

export default function ComparePage() {
  return (
    <main>
      <Suspense fallback={<LoadingState />}>
        <CompareView />
      </Suspense>
    </main>
  );
}
