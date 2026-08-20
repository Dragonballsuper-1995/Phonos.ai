'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { cleanPhoneName } from '@/lib/specHelpers';
import styles from './SimilarPhones.module.css';

interface SimilarPhoneItem {
  id: number;
  name: string;
  brand: string;
  price: number;
  similarity_score: number;
}

interface SimilarPhonesProps {
  phoneName: string;
  currentPhoneId?: string | number;
  budget?: number;
}

export default function SimilarPhones({
  phoneName,
  currentPhoneId,
  budget,
}: SimilarPhonesProps) {
  const router = useRouter();
  const [similarPhones, setSimilarPhones] = useState<SimilarPhoneItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    async function loadSimilar() {
      if (!phoneName) {
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        const res = await api.getSimilarPhones(phoneName, budget, 4);
        if (isMounted && res && res.similar_phones) {
          setSimilarPhones(res.similar_phones);
        }
      } catch (err) {
        if (process.env.NODE_ENV === 'development') {
          console.warn('Could not load similar phones:', err);
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadSimilar();
    return () => {
      isMounted = false;
    };
  }, [phoneName, budget]);

  if (!loading && similarPhones.length === 0) {
    return null;
  }

  return (
    <section className={styles.container} aria-label="Similar Hardware Alternatives">
      <div className={styles.headerRow}>
        <span className={styles.title}>CLOSEST HARDWARE ALTERNATIVES</span>
        <span className={styles.subtitle}>5D COSINE SPEC MATCH</span>
      </div>

      {loading ? (
        <div className={styles.loadingSkeleton}>
          <div className={styles.skeletonCard}>CALCULATING HARDWARE VECTORS...</div>
          <div className={styles.skeletonCard}>CALCULATING HARDWARE VECTORS...</div>
          <div className={styles.skeletonCard}>CALCULATING HARDWARE VECTORS...</div>
        </div>
      ) : (
        <div className={styles.grid}>
          {similarPhones.map((phone) => {
            const displayName = cleanPhoneName(phone.name, phone.brand);
            const matchPct = Math.min(99, Math.max(50, Math.round(phone.similarity_score * 100)));
            const priceFormatted = phone.price
              ? `₹${phone.price.toLocaleString('en-IN')}`
              : 'N/A';
            const compareUrl = currentPhoneId
              ? `/compare?ids=${currentPhoneId},${phone.id}`
              : `/compare?ids=${phone.id}`;

            return (
              <div key={phone.id} className={styles.card}>
                <div>
                  <div className={styles.cardTop}>
                    <span className={styles.brandLabel}>{phone.brand}</span>
                    <span className={styles.matchBadge}>{matchPct}% MATCH</span>
                  </div>
                  <h4 className={styles.phoneName}>{displayName}</h4>
                  <div className={styles.price}>{priceFormatted}</div>
                </div>

                <div className={styles.actions}>
                  <Link href={`/phone/${encodeURIComponent(phone.name)}`} className={styles.btnAction}>
                    VIEW REPORT
                  </Link>
                  <Link href={compareUrl} className={`${styles.btnAction} ${styles.btnPrimaryAction}`}>
                    COMPARE
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
