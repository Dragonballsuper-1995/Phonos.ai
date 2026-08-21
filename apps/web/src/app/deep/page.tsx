import DeepStreamView from '@/components/deep/DeepStreamView';

export const metadata = {
  title: 'Deep Mode — Phonos.ai',
  description: 'Describe what smartphone you need in plain English with real-time streaming neural copilot and benchmark reasoning.',
};

export default function DeepModePage() {
  return (
    <main>
      <DeepStreamView />
    </main>
  );
}
