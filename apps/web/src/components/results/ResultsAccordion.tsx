'use client';

import { useState } from 'react';
import { usePostHog } from 'posthog-js/react';
import type { RecommendedPhone } from '@/lib/types';
import PhoneRow from './PhoneRow';
import styles from './ResultsAccordion.module.css';

interface ResultsAccordionProps {
  initialRecommendations: RecommendedPhone[];
}

export default function ResultsAccordion({
  initialRecommendations,
}: ResultsAccordionProps) {
  const posthog = usePostHog();
  const [recommendations, setRecommendations] = useState<RecommendedPhone[]>(
    initialRecommendations
  );
  // Default first result open
  const [expandedIndex, setExpandedIndex] = useState<number | null>(0);

  const handleToggle = (index: number, phone: RecommendedPhone) => {
    const nextIndex = expandedIndex === index ? null : index;
    setExpandedIndex(nextIndex);

    if (nextIndex !== null && posthog) {
      posthog.capture('phone_expanded', {
        phone_model: phone.phone.model,
        brand: phone.phone.brand,
        price: phone.phone.price,
        ai_rank: index + 1,
      });
    }
  };

  const handleReject = (phoneId: string | number) => {
    setRecommendations((prev) =>
      prev.filter((item, idx) => (item.phone.id || idx + 1) !== phoneId)
    );
  };

  if (recommendations.length === 0) {
    return (
      <div className={styles.emptyState}>
        <h3 className={styles.emptyTitle}>ALL CANDIDATES DISMISSED</h3>
        <p className="body-md">
          You have dismissed all recommended models from this session.
        </p>
        <button
          type="button"
          className="btn-secondary"
          onClick={() => setRecommendations(initialRecommendations)}
        >
          RESTORE RECOMMENDATIONS
        </button>
      </div>
    );
  }

  return (
    <div className={styles.container} role="region" aria-label="Smartphone Recommendations List">
      <div className={styles.tableHeader}>
        <span className={styles.th}>RANK</span>
        <span className={styles.th}>SMARTPHONE MODEL</span>
        <span className={`${styles.th} ${styles.thScore}`}>AI MATCH</span>
        <span className={`${styles.th} ${styles.thPrice}`}>PRICE (INR)</span>
        <span className={styles.th} />
      </div>

      <div className={styles.listBody}>
        {recommendations.map((item, index) => (
          <PhoneRow
            key={item.phone.id || item.phone.slug || index}
            item={item}
            rank={index + 1}
            isExpanded={expandedIndex === index}
            onToggle={() => handleToggle(index, item)}
            onReject={handleReject}
          />
        ))}
      </div>
    </div>
  );
}
