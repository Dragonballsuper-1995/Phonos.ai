'use client';

import { useState, useEffect, useCallback } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import type { PhoneDetails } from '@/lib/types';
import { cleanPhoneName } from '@/lib/specHelpers';
import LoadingState from '@/components/ui/LoadingState';
import VerifiedBadge from '@/components/ui/VerifiedBadge';
import styles from './CompareView.module.css';

export default function CompareView() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const idsParam = searchParams.get('ids') || '';
  const [phones, setPhones] = useState<PhoneDetails[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<PhoneDetails[]>([]);
  const [searching, setSearching] = useState(false);

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
      setPhones(res.phones || []);
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

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setSearching(true);
    try {
      const results = await api.searchPhones(searchQuery);
      setSearchResults(results);
    } catch (err) {
      if (process.env.NODE_ENV === 'development') {
        console.warn('Search notice:', err);
      }
    } finally {
      setSearching(false);
    }
  };

  const handleAddPhone = (phone: PhoneDetails) => {
    if (!phone.id) return;
    const currentIds = phones.map((p) => p.id).filter(Boolean);
    if (!currentIds.includes(phone.id)) {
      const newIds = [...currentIds, phone.id].join(',');
      router.push(`/compare?ids=${newIds}`);
      setSearchResults([]);
      setSearchQuery('');
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

  if (loading) {
    return <LoadingState />;
  }

  const specRows = [
    { section: 'PRICING & VERIFICATION' },
    {
      label: 'Verified Price',
      render: (p: PhoneDetails) =>
        p.price ? `₹${p.price.toLocaleString('en-IN')}` : 'N/A',
    },
    {
      label: 'Price Tier',
      render: (p: PhoneDetails) => p.priceTier?.toUpperCase() || 'MID-RANGE',
    },
    {
      label: 'India Verified',
      render: () => <VerifiedBadge />,
    },
    { section: 'PERFORMANCE & PLATFORM' },
    {
      label: 'Processor / SoC',
      render: (p: PhoneDetails) => p.specs?.processor || 'N/A',
    },
    {
      label: 'RAM & Storage',
      render: (p: PhoneDetails) =>
        `${p.specs?.ram || 'Standard'} RAM + ${p.specs?.storage || 'Standard'} Storage`,
    },
    {
      label: 'Operating System',
      render: (p: PhoneDetails) => p.specs?.os || 'Android',
    },
    { section: 'DISPLAY & OPTICS' },
    {
      label: 'Display Technology',
      render: (p: PhoneDetails) => p.specs?.display || 'N/A',
    },
    {
      label: 'Screen Size',
      render: (p: PhoneDetails) => p.specs?.displaySize || 'N/A',
    },
    {
      label: 'Main Camera',
      render: (p: PhoneDetails) => p.specs?.mainCamera || 'N/A',
    },
    {
      label: 'Selfie Camera',
      render: (p: PhoneDetails) => p.specs?.selfieCamera || 'N/A',
    },
    { section: 'BATTERY & FEATURES' },
    {
      label: 'Battery Capacity',
      render: (p: PhoneDetails) => p.specs?.battery || 'N/A',
    },
    {
      label: 'Charging Speed',
      render: (p: PhoneDetails) => p.specs?.charging || 'Standard',
    },
    {
      label: 'Water Resistance',
      render: (p: PhoneDetails) => p.specs?.waterResistance || 'Standard',
    },
  ];

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <span className="label-caps">SIDE-BY-SIDE MATRIX</span>
        <h1 className={styles.pageTitle}>SMARTPHONE SPEC COMPARISON</h1>
        <p className="body-md">
          Compare verified architectural differences, pricing, and hardware capabilities across candidates.
        </p>
      </div>

      {/* Add Phone Section */}
      <section className={styles.searchSection}>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: 'var(--space-sm)', width: '100%' }}>
          <input
            type="text"
            className={styles.searchInput}
            placeholder="Search phone to add to comparison (e.g. OnePlus 12, Galaxy S24, Vivo X100)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button type="submit" className="btn-primary" disabled={searching}>
            {searching ? 'SEARCHING...' : 'SEARCH & ADD'}
          </button>
        </form>

        {searchResults.length > 0 && (
          <div className={styles.searchResults}>
            <span className="label-caps" style={{ width: '100%' }}>
              CLICK TO ADD:
            </span>
            {searchResults.slice(0, 6).map((phone) => (
              <button
                key={phone.id || phone.slug}
                type="button"
                className={styles.searchChip}
                onClick={() => handleAddPhone(phone)}
              >
                + {phone.brand} {cleanPhoneName(phone.fullName || phone.model, phone.brand)} (₹{phone.price ? phone.price.toLocaleString('en-IN') : 'N/A'})
              </button>
            ))}
          </div>
        )}
      </section>

      {phones.length === 0 ? (
        <div className={styles.emptyCompare}>
          <h3 className="display-md">NO PHONES SELECTED FOR COMPARISON</h3>
          <p className="body-md">
            Use the search box above or click &ldquo;Compare&rdquo; from any recommendation to inspect models side-by-side.
          </p>
        </div>
      ) : (
        <div className={styles.matrixWrapper}>
          <table className={styles.matrixTable}>
            <thead>
              <tr>
                <th className={`${styles.matrixTh} ${styles.labelCol}`}>SPECIFICATION</th>
                {phones.map((phone) => (
                  <th key={phone.id} className={styles.matrixTh}>
                    <div className={styles.phoneColHeader}>
                      <span className={styles.phoneBrand}>{phone.brand}</span>
                      <h2 className={styles.phoneName}>
                        {cleanPhoneName(phone.fullName || phone.model, phone.brand)}
                      </h2>
                      <span className={styles.phonePrice}>
                        ₹{phone.price ? phone.price.toLocaleString('en-IN') : 'N/A'}
                      </span>
                      {phone.id && (
                        <button
                          type="button"
                          className="btn-ghost"
                          style={{ padding: 0, alignSelf: 'flex-start', fontSize: 11 }}
                          onClick={() => handleRemovePhone(phone.id!)}
                        >
                          &times; REMOVE
                        </button>
                      )}
                    </div>
                  </th>
                ))}
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

                return (
                  <tr key={`row-${idx}`}>
                    <td className={`${styles.matrixTd} ${styles.labelCol}`}>
                      {row.label}
                    </td>
                    {phones.map((phone) => (
                      <td key={phone.id} className={styles.matrixTd}>
                        {row.render ? row.render(phone) : 'N/A'}
                      </td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
