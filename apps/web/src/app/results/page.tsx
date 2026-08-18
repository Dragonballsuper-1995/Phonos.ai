'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import styles from './results.module.css';
import { api } from '@/lib/api';
import { usePostHog } from 'posthog-js/react';

// ─── Helpers ──────────────────────────────────────────────────────────────────

/** Strip the brand prefix from a full phone name, avoiding duplication */
function stripBrandPrefix(fullName: string, brand: string): string {
  if (!fullName || !brand) return fullName || '';
  // Escape special regex chars in brand name
  const escaped = brand.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return fullName.replace(new RegExp(`^${escaped}\\s*`, 'i'), '').trim();
}

/** Strip RAM/ROM specs like "(16GB RAM + 256GB)" from displayed name */
function stripRamRom(name: string): string {
  return name
    .replace(/\s*\(\d+GB\s+RAM\s*\+\s*\d+GB\)/gi, '')
    .replace(/\s*\(\d+GB\s*\+\s*\d+GB\)/gi, '')
    .replace(/\s*\(\d+GB\s+RAM\)/gi, '')
    .trim();
}

/** Clean a display name: remove brand prefix + RAM/ROM */
function cleanPhoneName(fullName: string, brand: string): string {
  return stripRamRom(stripBrandPrefix(fullName, brand));
}

// ─── Spec categorizer ─────────────────────────────────────────────────────────
function categorizeSpecs(specs: any, rawSpecs: any) {
  const categories: Record<string, Record<string, string>> = {
    "Key Specifications": {},
    "Display & Design": {},
    "Performance": {},
    "Cameras": {},
    "Battery & Charging": {},
    "Connectivity": {},
    "Features": {},
    "Misc": {}
  };

  if (specs?.processor) categories["Performance"]["Processor"] = specs.processor;
  if (specs?.ram) categories["Performance"]["RAM"] = specs.ram;
  if (specs?.storage) categories["Performance"]["Storage"] = specs.storage;
  if (specs?.os) categories["Performance"]["Operating System"] = specs.os;
  if (specs?.display) categories["Display & Design"]["Display"] = specs.display;
  if (specs?.displaySize) categories["Display & Design"]["Size"] = specs.displaySize;
  if (specs?.mainCamera) categories["Cameras"]["Main Camera"] = specs.mainCamera;
  if (specs?.selfieCamera) categories["Cameras"]["Selfie Camera"] = specs.selfieCamera;
  if (specs?.battery) categories["Battery & Charging"]["Battery"] = specs.battery;
  if (specs?.charging) categories["Battery & Charging"]["Charging"] = specs.charging;

  if (rawSpecs) {
    Object.entries(rawSpecs).forEach(([key, value]) => {
      if (!value || value === "Unknown" || value === "No" || typeof value !== 'string') return;
      if (key === "Brand" || key === "Product_Name" || key === "Related_Items") return;

      const cleanKey = key.replace(/_/g, ' ');
      const valStr = value.toString();
      const lowerKey = key.toLowerCase();

      if (lowerKey.includes('display') || lowerKey.includes('screen') || lowerKey.includes('body') || lowerKey.includes('dimension') || lowerKey.includes('weight')) {
        categories["Display & Design"][cleanKey] = valStr;
      } else if (lowerKey.includes('cpu') || lowerKey.includes('gpu') || lowerKey.includes('chipset') || lowerKey.includes('memory') || lowerKey.includes('ram') || lowerKey.includes('storage') || lowerKey.includes('os') || lowerKey.includes('platform')) {
        categories["Performance"][cleanKey] = valStr;
      } else if (lowerKey.includes('camera') || lowerKey.includes('video') || lowerKey.includes('lens')) {
        categories["Cameras"][cleanKey] = valStr;
      } else if (lowerKey.includes('battery') || lowerKey.includes('charging')) {
        categories["Battery & Charging"][cleanKey] = valStr;
      } else if (lowerKey.includes('network') || lowerKey.includes('wifi') || lowerKey.includes('bluetooth') || lowerKey.includes('comms') || lowerKey.includes('usb') || lowerKey.includes('sim') || lowerKey.includes('5g') || lowerKey.includes('4g')) {
        categories["Connectivity"][cleanKey] = valStr;
      } else if (lowerKey.includes('sensor') || lowerKey.includes('feature') || lowerKey.includes('fingerprint') || lowerKey.includes('unlock') || lowerKey.includes('resistant') || lowerKey.includes('jack')) {
        categories["Features"][cleanKey] = valStr;
      } else {
        categories["Misc"][cleanKey] = valStr;
      }
    });
  }

  Object.keys(categories).forEach(cat => {
    if (Object.keys(categories[cat]).length === 0) {
      delete categories[cat];
    }
  });

  return categories;
}

// ─── Inner component that uses useSearchParams ────────────────────────────────
function ResultsContent() {
  const searchParams = useSearchParams();
  const posthog = usePostHog();
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const mode = searchParams.get('mode');
  const budget = searchParams.get('budget');
  const persona = searchParams.get('persona');
  const q = searchParams.get('q');
  const w_perf = searchParams.get('w_perf');
  const w_cam = searchParams.get('w_cam');
  const w_bat = searchParams.get('w_bat');
  const w_disp = searchParams.get('w_disp');
  const w_val = searchParams.get('w_val');

  useEffect(() => {
    const getResults = async () => {
      try {
        let reqData: any = { budget: parseInt(budget || '30000') };
        let data;

        if (mode === 'medium') {
          reqData.priorities = {
            performance: parseFloat(w_perf || '0.5'),
            camera: parseFloat(w_cam || '0.5'),
            battery: parseFloat(w_bat || '0.5'),
            display: parseFloat(w_disp || '0.5'),
            value: parseFloat(w_val || '0.5'),
          };
          data = await api.recommendMedium(reqData);
        } else if (mode === 'deep') {
          const query = q || 'Best phone overall';
          data = await api.recommendDeep({ query, budget: reqData.budget });
        } else {
          reqData.persona = persona || 'General';
          data = await api.recommendEasy(reqData);
        }
        if (data && data.recommendations) {
          setResults(data.recommendations);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    getResults();
  }, [mode, budget, persona, q, w_perf, w_cam, w_bat, w_disp, w_val]);

  if (loading) {
    return (
      <div className={styles.loadingScreen}>
        <div className={styles.spinner}></div>
        <h2 className="display-text blink" style={{ marginLeft: '2rem', letterSpacing: '4px' }}>ANALYZING DATABASE...</h2>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className={styles.loadingScreen}>
        <h2 className="display-text" style={{ color: 'var(--text-secondary)' }}>NO PHONES MATCH YOUR EXACT CRITERIA</h2>
      </div>
    );
  }

  const toggleExpand = (id: number, phoneDetails: any, rank: number) => {
    const isExpanding = expandedId !== id;
    setExpandedId(isExpanding ? id : null);
    
    if (isExpanding && posthog) {
      posthog.capture('phone_expanded', {
        phone_model: phoneDetails.model,
        brand: phoneDetails.brand,
        price: phoneDetails.price_numeric,
        ai_rank: rank,
        search_budget: searchParams.get('budget'),
        persona: searchParams.get('persona')
      });
    }
  };

  return (
    <div className={styles.accordionContainer}>
      <div className={styles.headerSpacer}></div>

      <div className={styles.header}>
        <h1 className="display-text outline-text">EXHIBITION</h1>
        <p>AI-verified matches, confirmed available in India.</p>
      </div>

      <div className={styles.listContainer}>
        <div className={styles.listHeader}>
          <div className={styles.colRank}>RANK</div>
          <div className={styles.colName}>MODEL</div>
          <div className={styles.colScore}>AI MATCH</div>
          <div className={styles.colPrice}>PRICE</div>
        </div>

        {results.map((item, index) => {
          const isExpanded = expandedId === index;
          const categorizedSpecs = categorizeSpecs(item.phone.specs, item.phone.raw_specs);
          const brand: string = item.phone.brand || '';
          const fullName: string = item.phone.fullName || item.phone.name || '';
          // Clean the display name — no brand prefix, no RAM/ROM
          const displayName = cleanPhoneName(fullName, brand);

          return (
            <div key={item.phone.id || index} className={`${styles.accordionRow} ${isExpanded ? styles.expanded : ''}`}>

              <div className={styles.rowMain} onClick={() => toggleExpand(index, item.phone, index + 1)}>
                <div className={styles.colRank}>
                  <span className={styles.rankBadge}>{(index + 1).toString().padStart(2, '0')}</span>
                </div>
                <div className={styles.colName}>
                  {/* Brand label — only the brand, never duplicated */}
                  <div className={styles.phoneBrand}>
                    {brand.toUpperCase()}
                    {item.ai_verified && (
                      <span className={styles.verifiedBadge} title="AI verified — available in India">
                        ✓ INDIA VERIFIED
                      </span>
                    )}
                  </div>
                  {/* Phone model name — brand already stripped */}
                  <div className={styles.phoneName}>{displayName}</div>
                </div>
                <div className={styles.colScore}>
                  <span className={styles.scoreText}>{Math.round(item.score)}%</span>
                </div>
                <div className={styles.colPrice}>
                  ₹{item.phone.price ? item.phone.price.toLocaleString('en-IN') : 'N/A'}
                  <svg className={`${styles.chevron} ${isExpanded ? styles.chevronOpen : ''}`} width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 9l6 6 6-6" /></svg>
                </div>
              </div>

              {isExpanded && (
                <div className={styles.expandedContent}>

                  <div className={styles.insightsSection}>
                    {item.ai_explanation && (
                      <div className={styles.insightBox} style={{ gridColumn: '1 / -1', background: 'rgba(56, 189, 248, 0.05)', border: '1px solid rgba(56, 189, 248, 0.2)' }}>
                        <h4 className={styles.insightTitle} style={{ color: '#38bdf8' }}>
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ display: 'inline', marginRight: '6px', verticalAlign: 'text-bottom' }}><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" /></svg>
                          AI EXPERT PITCH
                        </h4>
                        <p className={styles.aiExplanation}>{item.ai_explanation}</p>
                      </div>
                    )}
                    <div className={styles.insightBox}>
                      <h4 className={styles.insightTitle}>KEY STRENGTHS</h4>
                      <ul className={styles.insightList}>
                        {item.match_reasons.map((r: string, i: number) => (
                          <li key={`pos-${i}`} className={styles.insightPos}>
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><path d="M20 6L9 17l-5-5" /></svg>
                            {r}
                          </li>
                        ))}
                      </ul>
                    </div>
                    {item.trade_offs.length > 0 && (
                      <div className={styles.insightBox}>
                        <h4 className={styles.insightTitle}>COMPROMISES</h4>
                        <ul className={styles.insightList}>
                          {item.trade_offs.map((r: string, i: number) => (
                            <li key={`neg-${i}`} className={styles.insightNeg}>
                              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><path d="M18 6L6 18M6 6l12 12" /></svg>
                              {r}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {item.ai_verified && item.verify_reason && (
                      <div className={styles.insightBox}>
                        <h4 className={styles.insightTitle}>AI VERIFICATION</h4>
                        <p className={styles.verifyNote}>{item.verify_reason}</p>
                      </div>
                    )}
                  </div>

                  <div className={styles.specsTableContainer}>
                    {Object.entries(categorizedSpecs).map(([category, specsList]) => (
                      <div key={category} className={styles.specCategoryBlock}>
                        <div className={styles.specCategoryHeader}>{category}</div>
                        <table className={styles.specsTable}>
                          <tbody>
                            {Object.entries(specsList).map(([key, value]) => (
                              <tr key={key}>
                                <td className={styles.specKey}>{key}</td>
                                <td className={styles.specValue}>{value as string}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ))}
                  </div>

                  {/* RLHF Actionable Bar */}
                  <div className={styles.rlhfActionBar}>
                    <a 
                      href={`https://www.amazon.in/s?k=${encodeURIComponent(item.phone.model)}`} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className={styles.buyButton}
                      onClick={(e) => {
                        e.stopPropagation();
                        if (posthog) {
                          posthog.capture('buy_clicked', {
                            phone_model: item.phone.model,
                            brand: item.phone.brand,
                            price: item.phone.price_numeric,
                            ai_rank: index + 1
                          });
                        }
                      }}
                    >
                      BUY ON AMAZON
                    </a>
                    
                    <button 
                      className={styles.rejectButton}
                      onClick={(e) => {
                        e.stopPropagation();
                        if (posthog) {
                          posthog.capture('phone_rejected', {
                            phone_model: item.phone.model,
                            brand: item.phone.brand,
                            ai_rank: index + 1,
                            reason: "user_rejected"
                          });
                        }
                        // Simple UI trick: hide this phone if rejected (RLHF simulation)
                        setResults(prev => prev.filter(r => r.phone.id !== item.phone.id));
                      }}
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 6L6 18M6 6l12 12" /></svg>
                      REJECT
                    </button>
                  </div>

                </div>
              )}

            </div>
          );
        })}
      </div>
    </div>
  );
}

// ── Page export: wraps the inner component in Suspense ─────────────────────
export default function Results() {
  return (
    <Suspense fallback={
      <div className={styles.loadingScreen}>
        <div className={styles.spinner}></div>
        <h2 className="display-text blink" style={{ marginLeft: '2rem', letterSpacing: '4px' }}>LOADING...</h2>
      </div>
    }>
      <ResultsContent />
    </Suspense>
  );
}
