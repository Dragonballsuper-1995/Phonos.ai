'use client';

import { usePostHog } from 'posthog-js/react';
import type { RecommendedPhone } from '@/lib/types';
import { cleanPhoneName, categorizeSpecs } from '@/lib/specHelpers';
import ScoreBar from '@/components/ui/ScoreBar';
import VerifiedBadge from '@/components/ui/VerifiedBadge';
import styles from './PhoneRow.module.css';

interface PhoneRowProps {
  item: RecommendedPhone;
  rank: number;
  isExpanded: boolean;
  onToggle: () => void;
  onReject: (phoneId: string | number) => void;
}

export default function PhoneRow({
  item,
  rank,
  isExpanded,
  onToggle,
  onReject,
}: PhoneRowProps) {
  const posthog = usePostHog();
  const phone = item.phone;
  const brand = phone.brand || 'Unknown';
  const rawFullName = phone.fullName || phone.name || phone.model || 'Unknown';
  const displayName = cleanPhoneName(rawFullName, brand);

  const isTopRank = rank === 1;
  const rankLabel = rank.toString().padStart(2, '0');
  const priceFormatted = phone.price
    ? `₹${phone.price.toLocaleString('en-IN')}`
    : 'N/A';

  const categorized = categorizeSpecs(phone.specs, phone.raw_specs);
  const launchYear = phone.launch_year || 2025;

  const handleBuyClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (posthog) {
      posthog.capture('buy_clicked', {
        phone_model: phone.model,
        brand: phone.brand,
        price: phone.price,
        ai_rank: rank,
      });
    }
  };

  const handleRejectClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (posthog) {
      posthog.capture('phone_rejected', {
        phone_model: phone.model,
        brand: phone.brand,
        ai_rank: rank,
      });
    }
    onReject(phone.id || rank);
  };

  const amazonSearchUrl = `https://www.amazon.in/s?k=${encodeURIComponent(
    `${brand} ${displayName}`
  )}`;

  return (
    <div
      className={`${styles.rowWrapper} ${isExpanded ? styles.rowExpanded : ''}`}
      id={`phone-row-${rank}`}
    >
      {/* Row Header */}
      <div
        className={styles.rowHeader}
        onClick={onToggle}
        role="button"
        tabIndex={0}
        aria-expanded={isExpanded}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            onToggle();
          }
        }}
      >
        <span className={`${styles.rankBadge} ${isTopRank ? styles.rankTop : ''}`}>
          {rankLabel}
        </span>

        <div className={styles.nameBlock}>
          <div className={styles.brandRow}>
            <span className={styles.brandLabel}>{brand}</span>
            {item.ai_verified && (
              <VerifiedBadge title="Official Indian market launch" />
            )}
            {launchYear >= 2026 && (
              <span className={`${styles.yearBadge} ${styles.yearBadge2026}`}>
                2026 RELEASE
              </span>
            )}
            {launchYear === 2025 && (
              <span className={styles.yearBadge}>
                2025 FLAGSHIP
              </span>
            )}
          </div>
          <h3 className={styles.modelName}>{displayName}</h3>
        </div>

        <div className={styles.scoreBlock}>
          <span className={styles.scoreText}>{Math.round(item.score)}% COMPATIBILITY</span>
          <ScoreBar score={item.score} isTopRank={isTopRank} />
        </div>

        <div className={styles.priceBlock}>{priceFormatted}</div>

        <div className={`${styles.chevron} ${isExpanded ? styles.chevronOpen : ''}`}>
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="square"
            strokeLinejoin="miter"
          >
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </div>
      </div>

      {/* Expanded View */}
      {isExpanded && (
        <div className={styles.expandedPanel}>
          {/* 1. AI Pitch */}
          {item.ai_explanation && (
            <div className={styles.pitchBox}>
              <span className={styles.pitchTitle}>AI RECOMMENDATION RATIONALE</span>
              <p className={styles.pitchText}>{item.ai_explanation}</p>
            </div>
          )}

          {/* 2. Strengths & Tradeoffs */}
          <div className={styles.twoColGrid}>
            <div className={styles.insightCard}>
              <span className={styles.insightTitle}>KEY STRENGTHS & ADVANTAGES</span>
              <ul className={styles.bulletsList}>
                {item.match_reasons && item.match_reasons.length > 0 ? (
                  item.match_reasons.map((reason, i) => (
                    <li key={`str-${i}`} className={styles.strengthItem}>
                      <span className={styles.arrowBullet}>&rarr;</span>
                      <span>{reason}</span>
                    </li>
                  ))
                ) : (
                  <li className={styles.strengthItem}>
                    <span className={styles.arrowBullet}>&rarr;</span>
                    <span>High composite score across hardware benchmarks.</span>
                  </li>
                )}
              </ul>
            </div>

            <div className={styles.insightCard}>
              <span className={styles.insightTitle}>COMPROMISES & CONSIDERATIONS</span>
              <ul className={styles.bulletsList}>
                {item.trade_offs && item.trade_offs.length > 0 ? (
                  item.trade_offs.map((tradeoff, i) => (
                    <li key={`tr-${i}`} className={styles.compromiseItem}>
                      <span className={styles.dashBullet}>&mdash;</span>
                      <span>{tradeoff}</span>
                    </li>
                  ))
                ) : (
                  <li className={styles.compromiseItem}>
                    <span className={styles.dashBullet}>&mdash;</span>
                    <span>No critical hardware compromises flagged in this tier.</span>
                  </li>
                )}
              </ul>
            </div>

            {item.ai_verified && item.verify_reason && (
              <div className={styles.verifyBox}>
                <span className={styles.verifyTitle}>&#10003; VERIFIED IN INDIA:</span>
                <span className={styles.verifyText}>{item.verify_reason}</span>
              </div>
            )}
          </div>

          {/* 3. Specs Table */}
          <div className={styles.specsContainer}>
            <span className="label-caps">HARDWARE ARCHITECTURE SPECIFICATIONS</span>

            {Object.entries(categorized).map(([category, specsObj]) => (
              <div key={category} className={styles.specBlock}>
                <span className={styles.specCategoryHeader}>{category}</span>
                <div className={styles.specGrid}>
                  {Object.entries(specsObj).map(([key, val]) => (
                    <div key={key} className={styles.specPair}>
                      <span className={styles.specKey}>{key}</span>
                      <span className={styles.specValue}>{val}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* 4. Action Bar */}
          <div className={styles.actionBar}>
            <div style={{ display: 'flex', gap: 'var(--space-md)', alignItems: 'center' }}>
              <a
                href={amazonSearchUrl}
                target="_blank"
                rel="noopener noreferrer"
                className={`btn-primary ${styles.buyBtn}`}
                onClick={handleBuyClick}
                id={`buy-btn-${rank}`}
              >
                <span>CHECK LIVE PRICE ON AMAZON</span>
                <span>&rarr;</span>
              </a>
            </div>

            <button
              type="button"
              className="btn-ghost"
              onClick={handleRejectClick}
              id={`reject-btn-${rank}`}
            >
              &#10005; REMOVE THIS SMARTPHONE
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
