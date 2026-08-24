'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePostHog } from 'posthog-js/react';
import type { RecommendedPhone } from '@/lib/types';
import { cleanPhoneName, categorizeSpecs, compute5DVector } from '@/lib/specHelpers';
import ScoreBar from '@/components/ui/ScoreBar';
import VerifiedBadge from '@/components/ui/VerifiedBadge';
import styles from './PhoneRow.module.css';

interface PhoneRowProps {
  item: RecommendedPhone;
  rank: number;
  isExpanded: boolean;
  onToggle: () => void;
  onReject: (phoneId: string | number) => void;
  persona?: string;
  budget?: number;
  mode?: string;
}

export default function PhoneRow({
  item,
  rank,
  isExpanded,
  onToggle,
  onReject,
  persona,
  budget,
  mode,
}: PhoneRowProps) {
  const [showSpecs, setShowSpecs] = useState(false);
  const posthog = usePostHog();
  const phone = item.phone;
  const brand = phone.brand || 'Unknown';
  const rawFullName = phone.fullName || phone.name || phone.model || 'Unknown';
  const rawModelName = cleanPhoneName(rawFullName, brand);
  const fullDisplayName = rawModelName.toLowerCase().startsWith(brand.toLowerCase())
    ? rawModelName
    : `${brand} ${rawModelName}`;

  const isFlagship = (phone.price || 0) >= 55000;
  const isTopRank = rank === 1;
  const rankLabel = rank.toString().padStart(2, '0');
  const priceFormatted = phone.price
    ? `₹${phone.price.toLocaleString('en-IN')}`
    : 'N/A';

  const categorized = categorizeSpecs(phone.specs, phone.raw_specs);
  const launchYear = phone.launch_year || 2025;
  const vector5D = compute5DVector(phone);
  const hasLabBenchmarks = Boolean(
    phone.dxomark_camera_score ||
    phone.geekbench_multi ||
    phone.antutu_v10_score ||
    phone.gsmarena_battery_hours
  );

  const handleBuyClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (posthog) {
      posthog.capture('buy_clicked', {
        phone_name: fullDisplayName,
        phone_model: phone.model,
        brand: phone.brand,
        price: phone.price,
        ai_rank: rank,
        persona,
        budget,
        mode,
      });
    }
  };

  const handleRejectClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (posthog) {
      posthog.capture('phone_rejected', {
        phone_name: fullDisplayName,
        phone_model: phone.model,
        brand: phone.brand,
        ai_rank: rank,
        persona,
        budget,
        mode,
      });
    }
    onReject(phone.id || rank);
  };

  const amazonSearchUrl = `https://www.amazon.in/s?k=${encodeURIComponent(
    fullDisplayName
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
          <div className={styles.titleRow}>
            <h3 className={styles.modelName}>{fullDisplayName}</h3>
            <div className={styles.badgeGroup}>
              {item.ai_verified && (
                <VerifiedBadge title="Official Indian market launch" />
              )}
              {launchYear >= 2026 && (
                <span className={`${styles.yearBadge} ${styles.yearBadge2026}`}>
                  {isFlagship ? '2026 FLAGSHIP' : '2026 RELEASE'}
                </span>
              )}
              {launchYear === 2025 && (
                <span className={`${styles.yearBadge} ${isFlagship ? styles.yearBadgeFlagship : ''}`}>
                  {isFlagship ? '2025 FLAGSHIP' : '2025 RELEASE'}
                </span>
              )}
            </div>
          </div>
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

          {/* 2. Scientific Lab & Architectural Benchmark Scores */}
          <div className={styles.benchmarksSection}>
            <div className={styles.benchmarksHeader}>
              <span className={styles.benchmarksTitle}>
                {hasLabBenchmarks ? 'SCIENTIFIC LAB BENCHMARK SCORES' : '5D HARDWARE ARCHITECTURAL PROFILE'}
              </span>
              <span className={styles.benchmarksSubtitle}>
                {hasLabBenchmarks ? 'Lab Verified Testing Suite' : 'Algorithmic Hardware Vector (0-100)'}
              </span>
            </div>

            {hasLabBenchmarks ? (
              <div className={styles.benchmarkMetricsGrid}>
                {phone.dxomark_camera_score && (
                  <div className={`${styles.metricCard} ${styles.metricDxomark}`}>
                    <div className={styles.metricCardTop}>
                      <span className={styles.metricIcon}>📷</span>
                      <span className={styles.metricName}>DxOMark Optics</span>
                    </div>
                    <div className={styles.metricValue}>{Math.round(phone.dxomark_camera_score)}</div>
                    <span className={styles.metricDesc}>Camera Sensor & Lens Score</span>
                  </div>
                )}

                {phone.geekbench_multi && (
                  <div className={`${styles.metricCard} ${styles.metricGeekbench}`}>
                    <div className={styles.metricCardTop}>
                      <span className={styles.metricIcon}>⚡</span>
                      <span className={styles.metricName}>Geekbench 6</span>
                    </div>
                    <div className={styles.metricValue}>{phone.geekbench_multi.toLocaleString('en-IN')}</div>
                    <span className={styles.metricDesc}>Multi-Core CPU Compute</span>
                  </div>
                )}

                {phone.antutu_v10_score && (
                  <div className={`${styles.metricCard} ${styles.metricAntutu}`}>
                    <div className={styles.metricCardTop}>
                      <span className={styles.metricIcon}>🚀</span>
                      <span className={styles.metricName}>AnTuTu v10</span>
                    </div>
                    <div className={styles.metricValue}>
                      {phone.antutu_v10_score >= 1000000 
                        ? `${(phone.antutu_v10_score / 1000000).toFixed(2)}M`
                        : phone.antutu_v10_score.toLocaleString('en-IN')}
                    </div>
                    <span className={styles.metricDesc}>Full Hardware Pipeline Score</span>
                  </div>
                )}

                {phone.gsmarena_battery_hours && (
                  <div className={`${styles.metricCard} ${styles.metricBattery}`}>
                    <div className={styles.metricCardTop}>
                      <span className={styles.metricIcon}>🔋</span>
                      <span className={styles.metricName}>Active Battery</span>
                    </div>
                    <div className={styles.metricValue}>{phone.gsmarena_battery_hours.toFixed(1)} hrs</div>
                    <span className={styles.metricDesc}>Active Screen Endurance (AUS)</span>
                  </div>
                )}
              </div>
            ) : (
              <div className={styles.benchmarkMetricsGrid}>
                <div className={`${styles.metricCard} ${styles.metricGeekbench}`}>
                  <div className={styles.metricCardTop}>
                    <span className={styles.metricIcon}>⚡</span>
                    <span className={styles.metricName}>Compute Power</span>
                  </div>
                  <div className={styles.metricValue}>{Math.round(vector5D.performance)}/100</div>
                  <span className={styles.metricDesc}>{phone.specs?.processor || 'SoC Hardware Index'}</span>
                </div>

                <div className={`${styles.metricCard} ${styles.metricDxomark}`}>
                  <div className={styles.metricCardTop}>
                    <span className={styles.metricIcon}>📷</span>
                    <span className={styles.metricName}>Optics Index</span>
                  </div>
                  <div className={styles.metricValue}>{Math.round(vector5D.camera)}/100</div>
                  <span className={styles.metricDesc}>{phone.specs?.mainCamera ? 'Camera Architecture' : 'Sensor Profile'}</span>
                </div>

                <div className={`${styles.metricCard} ${styles.metricBattery}`}>
                  <div className={styles.metricCardTop}>
                    <span className={styles.metricIcon}>🔋</span>
                    <span className={styles.metricName}>Endurance Index</span>
                  </div>
                  <div className={styles.metricValue}>{Math.round(vector5D.battery)}/100</div>
                  <span className={styles.metricDesc}>{phone.specs?.battery || 'Power Management'}</span>
                </div>

                <div className={`${styles.metricCard} ${styles.metricAntutu}`}>
                  <div className={styles.metricCardTop}>
                    <span className={styles.metricIcon}>🖥️</span>
                    <span className={styles.metricName}>Display Quality</span>
                  </div>
                  <div className={styles.metricValue}>{Math.round(vector5D.display)}/100</div>
                  <span className={styles.metricDesc}>{phone.specs?.display || 'Visual Calibration'}</span>
                </div>
              </div>
            )}
          </div>

          {/* 3. Strengths & Tradeoffs */}
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

          {/* 4. Collapsible Hardware Architecture Specifications Dropdown */}
          <div className={styles.specsDropdownContainer}>
            <button
              type="button"
              className={styles.specsDropdownToggle}
              onClick={(e) => {
                e.stopPropagation();
                setShowSpecs(!showSpecs);
              }}
              aria-expanded={showSpecs}
              id={`specs-toggle-${rank}`}
            >
              <div className={styles.specsToggleLeft}>
                <span className="label-caps" style={{ color: 'var(--color-ink)', fontWeight: 700 }}>
                  HARDWARE ARCHITECTURE SPECIFICATIONS
                </span>
                <span className={styles.specsToggleHint}>
                  {showSpecs ? 'Click to collapse full technical breakdown' : 'Click to expand full technical breakdown'}
                </span>
              </div>

              <div className={styles.specsToggleRight}>
                <span className={styles.specsToggleActionText}>
                  {showSpecs ? 'HIDE SPECS' : 'VIEW SPECS'}
                </span>
                <span className={`${styles.specsChevron} ${showSpecs ? styles.specsChevronOpen : ''}`}>
                  ▼
                </span>
              </div>
            </button>

            {showSpecs && (
              <div className={styles.specsContainer}>
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
            )}
          </div>

          {/* 5. Action Bar */}
          <div className={styles.actionBar}>
            <div style={{ display: 'flex', gap: 'var(--space-md)', alignItems: 'center', flexWrap: 'wrap' }}>
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

              <Link
                href={phone.id ? `/compare?ids=${phone.id}` : `/compare?ids=${encodeURIComponent(phone.slug || phone.model || phone.name || '')}`}
                className="btn-secondary"
                id={`compare-btn-${rank}`}
                style={{ padding: '0.65rem 1.25rem', fontSize: '0.85rem' }}
              >
                <span>COMPARE 5D RADAR</span>
                <span>&rarr;</span>
              </Link>
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
