'use client';

import { useEffect, useState } from 'react';
import styles from './LoadingState.module.css';

const PHASES = [
  '1. SHIELDING: PURGING DEFECTIVE HARDWARE CANDIDATES...',
  '2. VECTORS: COMPUTING 5D SPEC EMBEDDINGS...',
  '3. ABSA: MODULATING ASPECT SENTIMENT GATES...',
  '4. DLRM: SCORING WITH XGBOOST RANKER...',
  '5. SYNTHESIZING TOP SMARTPHONE VERDICTS...',
];

export default function LoadingState() {
  const [phaseIndex, setPhaseIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setPhaseIndex((prev) => (prev + 1) % PHASES.length);
    }, 1100);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className={styles.loadingWrapper} role="status" aria-live="polite">
      <div className={styles.loadingCard}>
        <div className={styles.pulseBadge}>
          <span className={styles.pulseDot} />
          <span className="label-caps">ANALYZING CANDIDATE MATRIX</span>
        </div>
        <div className={styles.barTrack}>
          <div className={styles.barFill} />
        </div>
        <div className={styles.statusLabel}>{PHASES[phaseIndex]}</div>
      </div>
    </div>
  );
}
