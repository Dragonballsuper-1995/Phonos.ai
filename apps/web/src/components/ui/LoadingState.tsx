'use client';

import { useEffect, useState } from 'react';
import styles from './LoadingState.module.css';

const PHASES = [
  'Searching Indian smartphone catalog...',
  'Evaluating specs against priorities...',
  'Computing aspect sentiment & benchmarks...',
  'Verifying live India pricing & availability...',
  'Synthesizing recommendation rationale...',
];

export default function LoadingState() {
  const [phaseIndex, setPhaseIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setPhaseIndex((prev) => (prev + 1) % PHASES.length);
    }, 900);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className={styles.loadingWrapper} role="status" aria-live="polite">
      <div className={styles.barTrack}>
        <div className={styles.barFill} />
      </div>
      <div className={styles.statusLabel}>{PHASES[phaseIndex]}</div>
    </div>
  );
}
