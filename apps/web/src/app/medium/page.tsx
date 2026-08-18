import WeightsPanel from '@/components/mode/WeightsPanel';

export const metadata = {
  title: 'Medium Mode — Phonos.ai',
  description: 'Customize heuristic weights for performance, camera, battery, display, and value to find your ideal smartphone.',
};

export default function MediumModePage() {
  return (
    <main>
      <WeightsPanel />
    </main>
  );
}
