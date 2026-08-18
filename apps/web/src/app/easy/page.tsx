import PersonaFlow from '@/components/mode/PersonaFlow';

export const metadata = {
  title: 'Easy Mode — Phonos.ai',
  description: 'Select your persona and budget limit to get instant, verified smartphone recommendations.',
};

export default function EasyModePage() {
  return (
    <main>
      <PersonaFlow />
    </main>
  );
}
