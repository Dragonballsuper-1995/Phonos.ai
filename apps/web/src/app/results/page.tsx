'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import styles from './results.module.css';
import { api } from '@/lib/api';

// Utility to categorize raw specs
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

  // 1. Put standard mapped specs into Key Specs
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

  // 2. Parse Raw Specs into categories based on keywords
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

  // Remove empty categories
  Object.keys(categories).forEach(cat => {
    if (Object.keys(categories[cat]).length === 0) {
      delete categories[cat];
    }
  });

  return categories;
}

export default function Results() {
  const searchParams = useSearchParams();
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  useEffect(() => {
    const getResults = async () => {
      try {
        const mode = searchParams.get('mode');
        const budget = searchParams.get('budget');
        
        let reqData: any = { budget: parseInt(budget || '30000') };
        let data;
        
        if (mode === 'medium') {
          reqData.priorities = {
            performance: parseFloat(searchParams.get('w_perf') || '0.5'),
            camera: parseFloat(searchParams.get('w_cam') || '0.5'),
            battery: parseFloat(searchParams.get('w_bat') || '0.5'),
            display: parseFloat(searchParams.get('w_disp') || '0.5'),
            value: parseFloat(searchParams.get('w_val') || '0.5'),
          };
          data = await api.recommendMedium(reqData);
        } else {
          reqData.persona = searchParams.get('persona') || 'General';
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
  }, [searchParams]);

  if (loading) {
    return (
      <div className={styles.loadingScreen}>
        <div className={styles.spinner}></div>
        <h2 className="display-text blink" style={{marginLeft: '2rem', letterSpacing: '4px'}}>ANALYZING DATABASE...</h2>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className={styles.loadingScreen}>
        <h2 className="display-text" style={{color: 'var(--text-secondary)'}}>NO PHONES MATCH YOUR EXACT CRITERIA</h2>
      </div>
    );
  }

  const toggleExpand = (id: number) => {
    if (expandedId === id) {
      setExpandedId(null);
    } else {
      setExpandedId(id);
    }
  };

  return (
    <div className={styles.accordionContainer}>
      <div className={styles.headerSpacer}></div>
      
      <div className={styles.header}>
        <h1 className="display-text outline-text">EXHIBITION</h1>
        <p>Curated matches based on algorithmic performance scaling.</p>
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
          
          return (
            <div key={item.phone.id || index} className={`${styles.accordionRow} ${isExpanded ? styles.expanded : ''}`}>
              
              <div className={styles.rowMain} onClick={() => toggleExpand(index)}>
                <div className={styles.colRank}>
                  <span className={styles.rankBadge}>{(index + 1).toString().padStart(2, '0')}</span>
                </div>
                <div className={styles.colName}>
                  <div className={styles.phoneBrand}>{item.phone.brand}</div>
                  <div className={styles.phoneName}>{item.phone.fullName}</div>
                </div>
                <div className={styles.colScore}>
                  <span className={styles.scoreText}>{Math.round(item.score)}%</span>
                </div>
                <div className={styles.colPrice}>
                  ₹{item.phone.price ? item.phone.price.toLocaleString('en-IN') : 'N/A'}
                  <svg className={`${styles.chevron} ${isExpanded ? styles.chevronOpen : ''}`} width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 9l6 6 6-6"/></svg>
                </div>
              </div>

              {isExpanded && (
                <div className={styles.expandedContent}>
                  
                  <div className={styles.insightsSection}>
                    <div className={styles.insightBox}>
                      <h4 className={styles.insightTitle}>KEY STRENGTHS</h4>
                      <ul className={styles.insightList}>
                        {item.match_reasons.map((r: string, i: number) => (
                          <li key={`pos-${i}`} className={styles.insightPos}>
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><path d="M20 6L9 17l-5-5"/></svg>
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
                              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><path d="M18 6L6 18M6 6l12 12"/></svg>
                              {r}
                            </li>
                          ))}
                        </ul>
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
                                <td className={styles.specValue}>{value}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ))}
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
