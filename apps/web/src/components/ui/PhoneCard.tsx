import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { formatPrice } from '@/lib/utils';
import { cn } from '@/lib/utils';
import { MatchScore } from './MatchScore';
import { Button } from './Button';
import styles from './PhoneCard.module.css';
import { Phone } from '@/lib/types';

interface PhoneCardProps {
  phone: Phone;
  matchScore?: number;
  matchReasons?: string[];
  rank?: number;
  className?: string;
}

export function PhoneCard({ phone, matchScore, matchReasons, rank, className }: PhoneCardProps) {
  // Placeholder image if not provided
  const imageUrl = phone.imageUrl || `https://via.placeholder.com/400x500?text=${encodeURIComponent(phone.fullName)}`;

  return (
    <div className={cn(styles.card, rank === 1 && styles.topPick, className)}>
      {rank === 1 && (
        <div className={styles.badge}>🏆 Top Match</div>
      )}
      
      <div className={styles.imageContainer}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={imageUrl} alt={phone.fullName} className={styles.image} />
        {matchScore && (
          <div className={styles.scoreWrapper}>
            <MatchScore score={matchScore} size="sm" />
          </div>
        )}
      </div>

      <div className={styles.content}>
        <div className={styles.brand}>{phone.brand}</div>
        <h3 className={styles.name}>{phone.fullName}</h3>
        <div className={styles.price}>{formatPrice(phone.price)}</div>

        {matchReasons && matchReasons.length > 0 && (
          <div className={styles.reasons}>
            {matchReasons.slice(0, 3).map((reason, idx) => (
              <div key={idx} className={styles.reason}>
                <span className={styles.check}>✓</span> {reason}
              </div>
            ))}
          </div>
        )}

        <div className={styles.specs}>
          <div className={styles.spec}>
            <span className={styles.icon}>📱</span>
            <span>{phone.specs?.display || '6.7" AMOLED'}</span>
          </div>
          <div className={styles.spec}>
            <span className={styles.icon}>🔋</span>
            <span>{phone.specs?.battery || '5000 mAh'}</span>
          </div>
          <div className={styles.spec}>
            <span className={styles.icon}>📸</span>
            <span>{(phone.specs as any)?.mainCamera || (phone.specs as any)?.camera || '50MP Main'}</span>
          </div>
        </div>

        <div className={styles.actions}>
          <Link href={`/phone/${phone.slug}`} passHref className={styles.linkWrapper}>
            <Button variant={rank === 1 ? 'primary' : 'secondary'} fullWidth>
              View Details
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
