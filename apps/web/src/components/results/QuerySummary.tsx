'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import styles from './QuerySummary.module.css';

interface QuerySummaryProps {
  mode: string | null;
  budget: string | null;
  persona: string | null;
  query: string | null;
  personaDetected?: string | null;
  budgetUsed?: number;
}

export default function QuerySummary({
  mode,
  budget,
  persona,
  query,
  personaDetected,
  budgetUsed,
}: QuerySummaryProps) {
  const router = useRouter();

  const formattedBudget = budget
    ? `₹${parseInt(budget, 10).toLocaleString('en-IN')}`
    : budgetUsed
    ? `₹${budgetUsed.toLocaleString('en-IN')}`
    : 'N/A';

  const modeLabel = (mode || 'EASY').toUpperCase();

  return (
    <div className={styles.summaryBanner} role="region" aria-label="Query Summary">
      <div className={styles.leftBlock}>
        <span className="label-caps">UNDERSTOOD CRITERIA</span>
        <h2 className={styles.headline}>
          {mode === 'deep' && query ? `"${query}"` : `${modeLabel} MODE EVALUATION`}
        </h2>

        <div className={styles.tags}>
          <span className={`${styles.tag} ${styles.tagVermilion}`}>{modeLabel} MODE</span>
          <span className={styles.tag}>CEILING: {formattedBudget}</span>

          {persona && (
            <span className={styles.tag}>PERSONA: {persona.toUpperCase()}</span>
          )}

          {personaDetected && (
            <span className={styles.tag}>INFERRED INTENT: {personaDetected.toUpperCase()}</span>
          )}
        </div>
      </div>

      <div className={styles.actionGroup}>
        <Link href="/" className={styles.homeBtn} id="results-home-btn">
          <span>&larr;</span> HOME
        </Link>
        <button
          type="button"
          className={styles.refineBtn}
          onClick={() => router.back()}
          id="refine-parameters-btn"
        >
          REFINE PARAMETERS
        </button>
      </div>
    </div>
  );
}
