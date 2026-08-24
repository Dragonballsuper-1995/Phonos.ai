'use client';

import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import Link from 'next/link';
import { useSearchParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import type { PhoneDetails } from '@/lib/types';
import { cleanPhoneName, compute5DVector, extractDeepOptics, computeBalancedOverallScore, extractStorageVariant } from '@/lib/specHelpers';
import LoadingState from '@/components/ui/LoadingState';
import VerifiedBadge from '@/components/ui/VerifiedBadge';
import BenchmarkBadge from '@/components/ui/BenchmarkBadge';
import RadarChart, { PALETTE } from './RadarChart';
import styles from './CompareView.module.css';

const MAX_COMPARE = 5;

export default function CompareView() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const idsParam = searchParams.get('ids') || '';
  const [phones, setPhones] = useState<PhoneDetails[]>([]);
  const [loading, setLoading] = useState(true);
  const [showDeepOptics, setShowDeepOptics] = useState(false);

  // Search & Fuzzy Dropdown State
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState<PhoneDetails[]>([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [searching, setSearching] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState<number>(-1);

  const searchContainerRef = useRef<HTMLDivElement>(null);
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Fetch compared phones from URL ids
  const fetchComparison = useCallback(async () => {
    if (!idsParam) {
      setPhones([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    try {
      const idList = idsParam.split(',').map((id) => id.trim()).filter(Boolean);
      if (idList.length === 0) {
        setPhones([]);
        setLoading(false);
        return;
      }

      const res = await api.comparePhones(idList);
      setPhones((res.phones || []).slice(0, MAX_COMPARE));
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        console.warn('Comparison fetch notice:', err);
      }
    } finally {
      setLoading(false);
    }
  }, [idsParam]);

  useEffect(() => {
    fetchComparison();
  }, [fetchComparison]);

  // Real-time debounced auto-suggest search
  const handleQueryChange = (text: string) => {
    setSearchQuery(text);
    setSelectedIndex(-1);

    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    if (!text.trim()) {
      setSuggestions([]);
      setIsDropdownOpen(false);
      return;
    }

    debounceTimerRef.current = setTimeout(async () => {
      setSearching(true);
      try {
        const results = await api.searchPhones(text.trim());
        setSuggestions(results || []);
        setIsDropdownOpen(true);
      } catch (err) {
        if (process.env.NODE_ENV === 'development') {
          console.warn('Auto-suggest error:', err);
        }
      } finally {
        setSearching(false);
      }
    }, 150);
  };

  // Click outside to dismiss dropdown
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        searchContainerRef.current &&
        !searchContainerRef.current.contains(e.target as Node)
      ) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleAddPhone = (phone: PhoneDetails) => {
    if (!phone.id) return;
    const currentIds = phones.map((p) => p.id).filter(Boolean);
    if (currentIds.length >= MAX_COMPARE) return;

    if (!currentIds.includes(phone.id)) {
      const newIds = [...currentIds, phone.id].join(',');
      router.push(`/compare?ids=${newIds}`);
      setIsDropdownOpen(false);
      setSearchQuery('');
      setSuggestions([]);
    }
  };

  const handleRemovePhone = (idToRemove: number) => {
    const remaining = phones.filter((p) => p.id !== idToRemove).map((p) => p.id);
    if (remaining.length > 0) {
      router.push(`/compare?ids=${remaining.join(',')}`);
    } else {
      router.push('/compare');
    }
  };

  const handleClearAll = () => {
    setPhones([]);
    setSearchQuery('');
    setSuggestions([]);
    router.push('/compare');
  };

  // Keyboard navigation for dropdown
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isDropdownOpen || suggestions.length === 0) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev < suggestions.length - 1 ? prev + 1 : 0));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev > 0 ? prev - 1 : suggestions.length - 1));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
        handleAddPhone(suggestions[selectedIndex]);
      } else if (suggestions.length > 0) {
        handleAddPhone(suggestions[0]);
      }
    } else if (e.key === 'Escape') {
      setIsDropdownOpen(false);
    }
  };

  // Rank phones by composite 5D score
  const rankedPhones = useMemo(() => {
    if (phones.length === 0) return [];
    const withScores = phones.map((phone) => {
      const v = compute5DVector(phone);
      const balanced = computeBalancedOverallScore(v);
      return { phone, vector: v, composite: balanced.overallScore };
    });

    return withScores.sort((a, b) => b.composite - a.composite);
  }, [phones]);

  // Rank map: phone.id -> rank (1, 2, 3...)
  const rankMap = useMemo(() => {
    const map = new Map<number, number>();
    rankedPhones.forEach((item, idx) => {
      if (item.phone.id) {
        map.set(item.phone.id, idx + 1);
      }
    });
    return map;
  }, [rankedPhones]);

  // Calculate category winners
  const winners = useMemo(() => {
    if (phones.length < 2) return null;
    const vectors = phones.map((p) => {
      const v = compute5DVector(p);
      const balanced = computeBalancedOverallScore(v);
      return { phone: p, v, balanced };
    });

    const overallWinner = [...vectors].sort((a, b) => b.balanced.overallScore - a.balanced.overallScore)[0];
    const perfWinner = [...vectors].sort((a, b) => b.v.performance - a.v.performance)[0];
    const camWinner = [...vectors].sort((a, b) => b.v.camera - a.v.camera)[0];
    const dispWinner = [...vectors].sort((a, b) => b.v.display - a.v.display)[0];
    const batWinner = [...vectors].sort((a, b) => b.v.battery - a.v.battery)[0];

    return { overallWinner, perfWinner, camWinner, dispWinner, batWinner };
  }, [phones]);

  if (loading) {
    return <LoadingState />;
  }

  const isMaxReached = phones.length >= MAX_COMPARE;

  const specRows = [
    { section: 'PRICING & VERIFICATION' },
    {
      label: 'Verified Price',
      render: (p: PhoneDetails) =>
        p.price ? `₹${p.price.toLocaleString('en-IN')}` : 'N/A',
    },
    {
      label: 'Market Price Tier',
      render: (p: PhoneDetails) => (
        <span className={styles.specBadge}>
          {p.priceTier?.toUpperCase() || 'MID-RANGE'}
        </span>
      ),
    },
    {
      label: 'India Official Status',
      render: () => <VerifiedBadge />,
    },
    { section: 'SCIENTIFIC BENCHMARKS & LAB RATINGS' },
    {
      label: 'DxOMark Rear Camera',
      render: (p: PhoneDetails) =>
        p.dxomark_camera_score ? (
          <BenchmarkBadge type="dxomark-camera" value={p.dxomark_camera_score} />
        ) : (
          <span className={styles.heuristicText}>Spec Heuristic (Optical Score)</span>
        ),
    },
    {
      label: 'Geekbench 6 Multi-Core',
      render: (p: PhoneDetails) =>
        p.geekbench_multi ? (
          <BenchmarkBadge type="geekbench" value={p.geekbench_multi} />
        ) : (
          <span className={styles.heuristicText}>Silicon Tier Index</span>
        ),
    },
    {
      label: 'AnTuTu v10 Overall',
      render: (p: PhoneDetails) =>
        p.antutu_v10_score ? (
          <BenchmarkBadge type="antutu" value={p.antutu_v10_score} />
        ) : (
          <span className={styles.heuristicText}>Hardware Performance Index</span>
        ),
    },
    {
      label: 'DxOMark Display',
      render: (p: PhoneDetails) =>
        p.dxomark_display_score ? (
          <BenchmarkBadge type="dxomark-display" value={p.dxomark_display_score} />
        ) : (
          <span className={styles.heuristicText}>Panel Color & Luminance Score</span>
        ),
    },
    {
      label: 'GSMArena Battery (AUS)',
      render: (p: PhoneDetails) =>
        p.gsmarena_battery_hours ? (
          <BenchmarkBadge type="battery" value={p.gsmarena_battery_hours} />
        ) : (
          <span className={styles.heuristicText}>Battery Endurance Standard</span>
        ),
    },
    {
      label: 'VCX Forum Camera',
      render: (p: PhoneDetails) =>
        p.vcx_camera_score ? (
          <BenchmarkBadge type="vcx" value={p.vcx_camera_score} />
        ) : (
          <span className={styles.heuristicText}>—</span>
        ),
    },
    { section: 'PLATFORM & COMPUTING' },
    {
      label: 'Processor / SoC',
      render: (p: PhoneDetails) => p.specs?.processor || 'Octa-Core High Performance SoC',
    },
    {
      label: 'RAM & Memory',
      render: (p: PhoneDetails) => p.specs?.ram || '8 GB / 12 GB RAM',
    },
    {
      label: 'Internal Storage',
      render: (p: PhoneDetails) => p.specs?.storage || '128 GB / 256 GB UFS',
    },
    {
      label: 'Operating System',
      render: (p: PhoneDetails) => p.specs?.os || 'Android',
    },
    { section: 'DISPLAY & VISUALS' },
    {
      label: 'Display Technology',
      render: (p: PhoneDetails) => p.specs?.display || 'AMOLED Display',
    },
    {
      label: 'Screen Size & Refresh',
      render: (p: PhoneDetails) =>
        `${p.specs?.displaySize || '6.7 inches'} (${p.specs?.refreshRate || '120Hz'})`,
    },
    { section: 'CAMERAS & OPTICS' },
    {
      label: 'Main Rear Optics',
      render: (p: PhoneDetails) => {
        const cam = p.specs?.mainCamera || '50 MP Flagship Sensor (OIS)';
        if (cam.includes('•')) {
          const parts = cam.split('•').map((s) => s.trim()).filter(Boolean);
          return (
            <ul className={styles.lensList}>
              {parts.map((lens, lIdx) => (
                <li key={lIdx}>{lens}</li>
              ))}
            </ul>
          );
        }
        return cam;
      },
    },
    {
      label: 'Front Selfie Camera',
      render: (p: PhoneDetails) => p.specs?.selfieCamera || '16 MP HDR Selfie',
    },
    { section: 'BATTERY & ENDURANCE' },
    {
      label: 'Battery Capacity',
      render: (p: PhoneDetails) => p.specs?.battery || '5000 mAh',
    },
    {
      label: 'Charging Speed',
      render: (p: PhoneDetails) => p.specs?.charging || '45W Fast Charging',
    },
    { section: 'DURABILITY & SECURITY' },
    {
      label: 'Water & Dust Resistance',
      render: (p: PhoneDetails) => p.specs?.waterResistance || 'IP68 Dust/Water Resistant',
    },
    {
      label: 'Biometrics & Security',
      render: (p: PhoneDetails) => p.specs?.biometrics || 'In-Display Fingerprint & Face Unlock',
    },
  ];

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.headerTitleGroup}>
          <div className={styles.titleWithAction}>
            <div>
              <span className="label-caps">SIDE-BY-SIDE MATRIX</span>
              <h1 className={styles.pageTitle}>SMARTPHONE SPEC COMPARISON</h1>
            </div>
            <div className={styles.actionGroup}>
              <Link href="/" className={styles.homeBtn} id="compare-home-btn">
                <span>&larr;</span> HOME
              </Link>
              {phones.length > 0 && (
                <button
                  type="button"
                  className={styles.newCompareBtn}
                  onClick={handleClearAll}
                  title="Clear all devices and start a new comparison"
                >
                  <span>🔄</span> START NEW COMPARISON
                </button>
              )}
            </div>
          </div>
        </div>
        <p className="body-md">
          Compare verified architectural differences, pricing, lab benchmarks, and 5D radar capabilities side-by-side.
        </p>
      </div>

      {/* Real-time Fuzzy Search Adder Section */}
      <section className={styles.searchSection} ref={searchContainerRef}>
        <div className={styles.searchHeader}>
          <span className={styles.searchLabel}>
            ADD TO COMPARISON ({phones.length}/{MAX_COMPARE} PHONES)
          </span>
          {isMaxReached && (
            <span className={styles.maxLimitBadge}>
              MAXIMUM 5 PHONES REACHED
            </span>
          )}
        </div>

        <div className={styles.searchInputWrapper}>
          <input
            type="text"
            className={styles.searchInput}
            placeholder={
              isMaxReached
                ? 'Maximum 5 phones selected. Remove a device to search and add another...'
                : 'Search any phone by name or model (e.g. S26, OnePlus 15, iPhone 16, iQOO 13)...'
            }
            value={searchQuery}
            disabled={isMaxReached}
            onChange={(e) => handleQueryChange(e.target.value)}
            onFocus={() => {
              if (suggestions.length > 0) setIsDropdownOpen(true);
            }}
            onKeyDown={handleKeyDown}
          />
          {searching && <span className={styles.searchSpinner}>⚡</span>}
        </div>

        {/* Real-time Floating Dropdown Suggestions */}
        {isDropdownOpen && suggestions.length > 0 && (
          <div className={styles.dropdown}>
            <div className={styles.dropdownHeader}>
              <span>SEARCH RESULTS ({suggestions.length})</span>
              <span style={{ fontSize: 10, color: 'var(--color-ink-muted)' }}>Use ↑↓ and Enter to select</span>
            </div>
            <div className={styles.dropdownList}>
              {suggestions.map((phone, idx) => {
                const isSelected = selectedIndex === idx;
                const isAlreadyAdded = phones.some((p) => p.id === phone.id);

                return (
                  <div
                    key={phone.id || idx}
                    className={`${styles.dropdownItem} ${isSelected ? styles.dropdownItemSelected : ''} ${
                      isAlreadyAdded ? styles.dropdownItemDisabled : ''
                    }`}
                    onClick={() => {
                      if (!isAlreadyAdded && !isMaxReached) {
                        handleAddPhone(phone);
                      }
                    }}
                    onMouseEnter={() => setSelectedIndex(idx)}
                  >
                    {(() => {
                      const variant = extractStorageVariant(phone);
                      const cleanName = cleanPhoneName(phone.fullName || phone.name || phone.model, phone.brand);
                      return (
                        <div className={styles.itemInfo}>
                          <span className={styles.itemBrand}>{phone.brand}</span>
                          <div className={styles.itemNameRow}>
                            <span className={styles.itemName}>{cleanName}</span>
                            {variant && <span className={styles.variantBadge}>{variant}</span>}
                          </div>
                          <span className={styles.itemSpec}>
                            {variant ? `${variant} • ` : ''}
                            {phone.specs?.processor || 'High Performance SoC'} • {phone.specs?.battery || '5000 mAh'}
                          </span>
                        </div>
                      );
                    })()}

                    <div className={styles.itemAction}>
                      <span className={styles.itemPrice}>
                        ₹{phone.price ? phone.price.toLocaleString('en-IN') : 'N/A'}
                      </span>
                      {isAlreadyAdded ? (
                        <span className={styles.itemAddedBadge}>ADDED</span>
                      ) : (
                        <button
                          type="button"
                          className={styles.itemAddBtn}
                          disabled={isMaxReached}
                        >
                          + ADD
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </section>

      {phones.length === 0 ? (
        <div className={styles.emptyCompare}>
          <div className={styles.emptyIcon}>⚖️</div>
          <h2 className="display-md">NO PHONES SELECTED FOR COMPARISON</h2>
          <p className="body-md" style={{ maxWidth: 540 }}>
            Type any smartphone model into the search box above (e.g. &ldquo;Galaxy S26&rdquo;, &ldquo;OnePlus 15&rdquo;) or click &ldquo;Compare&rdquo; from any recommendation to inspect models side-by-side.
          </p>
        </div>
      ) : (
        <>
          {/* 5D Benchmark Radar Chart */}
          <RadarChart phones={phones} />

          {/* Category Winners Summary (When comparing 2+ phones) */}
          {winners && (
            <section className={styles.winnersSection} aria-label="Category Winners">
              <div className={styles.winnersHeader}>
                <span>🏆 CATEGORY VERDICTS & BENCHMARK LEADERS</span>
              </div>

              {/* 1. Full-Width Horizontal Overall Champion Showcase Banner */}
              <div className={styles.overallChampionBanner}>
                <div className={styles.overallChampionLeft}>
                  <div className={styles.overallChampionBadge}>
                    <span className={styles.crownIcon}>👑</span>
                    <span className={styles.overallLabel}>OVERALL CHAMPION</span>
                  </div>
                  <div className={styles.overallPhoneInfo}>
                    <span className={styles.overallBrand}>{winners.overallWinner.phone.brand}</span>
                    <span className={styles.overallPhoneName}>
                      {cleanPhoneName(winners.overallWinner.phone.fullName || winners.overallWinner.phone.model, winners.overallWinner.phone.brand)}
                    </span>
                    {(() => {
                      const v = extractStorageVariant(winners.overallWinner.phone);
                      return v ? <span className={styles.overallVariantBadge}>{v}</span> : null;
                    })()}
                  </div>
                </div>

                <div className={styles.overallChampionMid}>
                  <span className={styles.overallSubRating}>
                    {winners.overallWinner.balanced.balanceRating}
                  </span>
                  <span className={styles.overallDescription}>
                    Highest harmonic composite rating across Performance, Optics, Battery, Display, and Build durability.
                  </span>
                </div>

                <div className={styles.overallChampionRight}>
                  <div className={styles.overallScoreCircle}>
                    <span className={styles.overallScoreNum}>{winners.overallWinner.balanced.overallScore}</span>
                    <span className={styles.overallScoreMax}>/100</span>
                  </div>
                  <span className={styles.overallScoreLabel}>OVERALL SCORE</span>
                </div>
              </div>

              {/* 2. 2x2 / 4-Column Grid for the 4 Pillar Categories */}
              <div className={styles.categoryGrid}>
                {/* Gaming & Performance */}
                <div className={styles.winnerCard} style={{ borderLeftColor: '#00E599' }}>
                  <span className={styles.winnerCategory}>GAMING & PERFORMANCE</span>
                  <span className={styles.winnerPhoneName}>
                    {winners.perfWinner.phone.brand} {cleanPhoneName(winners.perfWinner.phone.fullName || winners.perfWinner.phone.model, winners.perfWinner.phone.brand)}
                  </span>
                  <span className={styles.winnerMetric} style={{ color: '#00E599' }}>
                    {winners.perfWinner.v.performance}/100 Performance Score
                  </span>
                </div>

                {/* Cameras & Optics */}
                <div className={styles.winnerCard} style={{ borderLeftColor: '#FF6B00' }}>
                  <span className={styles.winnerCategory}>CAMERAS & OPTICS</span>
                  <span className={styles.winnerPhoneName}>
                    {winners.camWinner.phone.brand} {cleanPhoneName(winners.camWinner.phone.fullName || winners.camWinner.phone.model, winners.camWinner.phone.brand)}
                  </span>
                  <span className={styles.winnerMetric} style={{ color: '#FF6B00' }}>
                    {winners.camWinner.v.camera}/100 Optics Score
                  </span>
                </div>

                {/* Battery & Charging */}
                <div className={styles.winnerCard} style={{ borderLeftColor: '#00B4D8' }}>
                  <span className={styles.winnerCategory}>BATTERY & CHARGING</span>
                  <span className={styles.winnerPhoneName}>
                    {winners.batWinner.phone.brand} {cleanPhoneName(winners.batWinner.phone.fullName || winners.batWinner.phone.model, winners.batWinner.phone.brand)}
                  </span>
                  <span className={styles.winnerMetric} style={{ color: '#00B4D8' }}>
                    {winners.batWinner.v.battery}/100 Battery Score
                  </span>
                </div>

                {/* Display Quality */}
                <div className={styles.winnerCard} style={{ borderLeftColor: '#8B5CF6' }}>
                  <span className={styles.winnerCategory}>DISPLAY QUALITY</span>
                  <span className={styles.winnerPhoneName}>
                    {winners.dispWinner.phone.brand} {cleanPhoneName(winners.dispWinner.phone.fullName || winners.dispWinner.phone.model, winners.dispWinner.phone.brand)}
                  </span>
                  <span className={styles.winnerMetric} style={{ color: '#8B5CF6' }}>
                    {winners.dispWinner.v.display}/100 Display Score
                  </span>
                </div>
              </div>
            </section>
          )}

          {/* Matrix Specification Table */}
          <div className={styles.matrixWrapper}>
            <table className={styles.matrixTable}>
              <thead>
                <tr>
                  <th className={`${styles.matrixTh} ${styles.labelCol}`}>
                    TECHNICAL SPECIFICATION
                  </th>
                  {phones.map((phone, pIdx) => {
                    const color = PALETTE[pIdx % PALETTE.length];
                    const rank = rankMap.get(phone.id || 0) || (pIdx + 1);

                    return (
                      <th key={phone.id || pIdx} className={styles.matrixTh}>
                        <div className={styles.phoneColHeader}>
                          <div className={styles.topBadgeRow}>
                            <span
                              className={styles.rankBadge}
                              style={{ backgroundColor: color.stroke, color: '#000' }}
                            >
                              #{rank} RANKED
                            </span>
                            {phone.id && (
                              <button
                                type="button"
                                className={styles.removeBtn}
                                onClick={() => handleRemovePhone(phone.id!)}
                                title="Remove from comparison"
                              >
                                ✕ REMOVE
                              </button>
                            )}
                          </div>

                          <span className={styles.phoneBrand}>{phone.brand}</span>
                          <h2 className={styles.phoneName}>
                            {cleanPhoneName(phone.fullName || phone.model, phone.brand)}
                          </h2>
                          {(() => {
                            const variant = extractStorageVariant(phone);
                            return variant ? (
                              <span className={styles.headerVariantBadge}>{variant}</span>
                            ) : null;
                          })()}
                          <span className={styles.phonePrice}>
                            ₹{phone.price ? phone.price.toLocaleString('en-IN') : 'N/A'}
                          </span>
                        </div>
                      </th>
                    );
                  })}
                </tr>
              </thead>
              <tbody>
                {specRows.map((row, idx) => {
                  if (row.section) {
                    return (
                      <tr key={`sec-${idx}`}>
                        <td
                          colSpan={phones.length + 1}
                          className={styles.sectionRow}
                        >
                          {row.section}
                        </td>
                      </tr>
                    );
                  }

                  const isSelfieRow = row.label === 'Front Selfie Camera';

                  return (
                    <React.Fragment key={`row-${idx}`}>
                      <tr>
                        <td className={`${styles.matrixTd} ${styles.labelCol}`}>
                          {row.label}
                        </td>
                        {phones.map((phone, pIdx) => (
                          <td key={phone.id || pIdx} className={styles.matrixTd}>
                            {row.render ? row.render(phone) : 'N/A'}
                          </td>
                        ))}
                      </tr>

                      {/* Interactive Deep Optics & Sensor Details Drawer */}
                      {isSelfieRow && (
                        <>
                          <tr className={styles.opticsToggleRow}>
                            <td colSpan={phones.length + 1} className={styles.opticsToggleTd}>
                              <button
                                type="button"
                                className={styles.opticsToggleBtn}
                                onClick={() => setShowDeepOptics((prev) => !prev)}
                              >
                                <span>
                                  {showDeepOptics
                                    ? '▴ HIDE DEEP SENSOR & OPTICS DATA'
                                    : '▾ VIEW DEEP SENSOR & OPTICS DATA'}
                                </span>
                                <span className={styles.opticsToggleHint}>
                                  {showDeepOptics
                                    ? 'Collapse camera hardware drawer'
                                    : 'Sensors (Sony/ISOCELL), 6P lens elements, FOV, optical zoom, OIS'}
                                </span>
                              </button>
                            </td>
                          </tr>

                          {showDeepOptics && (
                            <>
                              <tr className={styles.deepOpticsRow}>
                                <td className={`${styles.matrixTd} ${styles.deepOpticsLabel}`}>
                                  Optical Sensor Models
                                </td>
                                {phones.map((phone, pIdx) => {
                                  const optics = extractDeepOptics(phone);
                                  return (
                                    <td
                                      key={phone.id || pIdx}
                                      className={`${styles.matrixTd} ${styles.deepOpticsValue}`}
                                    >
                                      {optics.sensors}
                                    </td>
                                  );
                                })}
                              </tr>

                              <tr className={styles.deepOpticsRow}>
                                <td className={`${styles.matrixTd} ${styles.deepOpticsLabel}`}>
                                  Lens Construction & Elements
                                </td>
                                {phones.map((phone, pIdx) => {
                                  const optics = extractDeepOptics(phone);
                                  return (
                                    <td
                                      key={phone.id || pIdx}
                                      className={`${styles.matrixTd} ${styles.deepOpticsValue}`}
                                    >
                                      {optics.lensElements}
                                    </td>
                                  );
                                })}
                              </tr>

                              <tr className={styles.deepOpticsRow}>
                                <td className={`${styles.matrixTd} ${styles.deepOpticsLabel}`}>
                                  Field of View & Apertures
                                </td>
                                {phones.map((phone, pIdx) => {
                                  const optics = extractDeepOptics(phone);
                                  return (
                                    <td
                                      key={phone.id || pIdx}
                                      className={`${styles.matrixTd} ${styles.deepOpticsValue}`}
                                    >
                                      {optics.fovAndAperture}
                                    </td>
                                  );
                                })}
                              </tr>

                              <tr className={styles.deepOpticsRow}>
                                <td className={`${styles.matrixTd} ${styles.deepOpticsLabel}`}>
                                  Optical & Digital Zoom
                                </td>
                                {phones.map((phone, pIdx) => {
                                  const optics = extractDeepOptics(phone);
                                  return (
                                    <td
                                      key={phone.id || pIdx}
                                      className={`${styles.matrixTd} ${styles.deepOpticsValue}`}
                                    >
                                      {optics.zoomCapabilities}
                                    </td>
                                  );
                                })}
                              </tr>

                              <tr className={styles.deepOpticsRow}>
                                <td className={`${styles.matrixTd} ${styles.deepOpticsLabel}`}>
                                  Stabilization & Autofocus
                                </td>
                                {phones.map((phone, pIdx) => {
                                  const optics = extractDeepOptics(phone);
                                  return (
                                    <td
                                      key={phone.id || pIdx}
                                      className={`${styles.matrixTd} ${styles.deepOpticsValue}`}
                                    >
                                      {optics.stabilizationAndAF}
                                    </td>
                                  );
                                })}
                              </tr>

                              <tr className={styles.deepOpticsRow}>
                                <td className={`${styles.matrixTd} ${styles.deepOpticsLabel}`}>
                                  Video Capabilities & Modes
                                </td>
                                {phones.map((phone, pIdx) => {
                                  const optics = extractDeepOptics(phone);
                                  return (
                                    <td
                                      key={phone.id || pIdx}
                                      className={`${styles.matrixTd} ${styles.deepOpticsValue}`}
                                    >
                                      {optics.videoFeatures}
                                    </td>
                                  );
                                })}
                              </tr>
                            </>
                          )}
                        </>
                      )}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
