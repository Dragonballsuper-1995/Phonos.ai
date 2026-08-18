import NaturalInput from '@/components/mode/NaturalInput';

export const metadata = {
  title: 'Deep Mode — Phonos.ai',
  description: 'Describe what smartphone you need in plain English with semantic vector matching.',
};

export default function DeepModePage() {
  return (
    <main>
      <NaturalInput />
    </main>
  );
}
