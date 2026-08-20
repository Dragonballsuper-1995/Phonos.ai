'use client';

import { useEffect, useState } from 'react';
import styles from './LoadingState.module.css';

const PHASES = [
  { step: '01/05', text: 'STAGE 1: PURGING DEFECTIVE HARDWARE VIA KNOWLEDGE GRAPH...' },
  { step: '02/05', text: 'STAGE 2: COMPUTING 5D HARDWARE VECTOR EMBEDDINGS...' },
  { step: '03/05', text: 'STAGE 3: MODULATING ASPECT SENTIMENT GATES (ABSA)...' },
  { step: '04/05', text: 'STAGE 4: SCORING CANDIDATES WITH XGBOOST DLRM RANKER...' },
  { step: '05/05', text: 'STAGE 5: CALIBRATING VERIFIED INDIAN MARKET VERDICTS...' },
];

export default function LoadingState() {
  const [phaseIndex, setPhaseIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setPhaseIndex((prev) => (prev + 1) % PHASES.length);
    }, 1100);
    return () => clearInterval(interval);
  }, []);

  const current = PHASES[phaseIndex];

  return (
    <div className={styles.loadingWrapper} role="status" aria-live="polite">
      <div className={styles.stageBadge}>
        <span className={styles.stageDot} />
        <span className="label-caps">{current.step} INTELLIGENCE PIPELINE</span>
      </div>
      <div className={styles.barTrack}>
        <div className={styles.barFill} />
      </div>
      <div className={styles.statusLabel}>{current.text}</div>
    </div>
  );
}
