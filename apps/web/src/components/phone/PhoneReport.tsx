'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { usePostHog } from 'posthog-js/react';
import type { PhoneDetails } from '@/lib/types';
import { cleanPhoneName, categorizeSpecs } from '@/lib/specHelpers';
import VerifiedBadge from '@/components/ui/VerifiedBadge';
import styles from './PhoneReport.module.css';

interface PhoneReportProps {
  phone: PhoneDetails;
}

export default function PhoneReport({ phone }: PhoneReportProps) {
  const router = useRouter();
  const posthog = usePostHog();

  const brand = phone.brand || 'Unknown';
  const rawFullName = phone.fullName || phone.name || phone.model || 'Unknown';
  const displayName = cleanPhoneName(rawFullName, brand);
  const formattedPrice = phone.price
    ? `₹${phone.price.toLocaleString('en-IN')}`
    : 'N/A';

  const categorized = categorizeSpecs(phone.specs, phone.raw_specs);

  const handleBuyClick = () => {
    if (posthog) {
      posthog.capture('buy_clicked', {
        phone_model: phone.model,
        brand: phone.brand,
        price: phone.price,
        source: 'phone_report',
      });
    }
  };

  const handleCompareClick = () => {
    if (phone.id) {
      router.push(`/compare?ids=${phone.id}`);
    }
  };

  const amazonSearchUrl = `https://www.amazon.in/s?k=${encodeURIComponent(
    `${brand} ${displayName}`
  )}`;

  return (
    <div className={styles.container}>
      {/* Breadcrumb */}
      <nav className={styles.breadcrumb} aria-label="Breadcrumbs">
        <Link href="/" className={styles.breadcrumbLink}>
          HOME
        </Link>
        <span>/</span>
        <span style={{ color: 'var(--color-ink)' }}>{brand}</span>
        <span>/</span>
        <span>{displayName}</span>
      </nav>

      {/* Hero Section */}
      <section className={styles.heroGrid} aria-label="Device Overview">
        <div className={styles.imageContainer}>
          {phone.imageUrl ? (
            <img
              src={phone.imageUrl}
              alt={`${brand} ${displayName}`}
              className={styles.phoneImg}
            />
          ) : (
            <div className={styles.devicePlaceholder}>
              <span className={styles.placeholderBrand}>{brand}</span>
              <span className={styles.placeholderBadge}>HARDWARE PROFILE</span>
            </div>
          )}
        </div>

        <div className={styles.infoBlock}>
          <div className={styles.brandVerifiedRow}>
            <span className="label-caps">{brand}</span>
            <VerifiedBadge title="AI verified Indian catalog data" />
          </div>

          <h1 className={styles.modelTitle}>{displayName}</h1>

          <div className={styles.priceBlock}>
            <span className={styles.price}>{formattedPrice}</span>
            <span className={styles.priceTier}>
              {phone.priceTier ? phone.priceTier.toUpperCase() : 'VERIFIED IN INDIA'}
            </span>
          </div>

          {phone.highlights && phone.highlights.length > 0 && (
            <ul className={styles.highlightsList}>
              {phone.highlights.map((h, idx) => (
                <li key={idx} className={styles.highlightItem}>
                  <span style={{ color: 'var(--color-vermilion)', fontWeight: 'bold' }}>
                    &rarr;
                  </span>
                  <span>{h}</span>
                </li>
              ))}
            </ul>
          )}

          <div className={styles.actionsRow}>
            <a
              href={amazonSearchUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary"
              onClick={handleBuyClick}
              id="report-buy-btn"
            >
              <span>CHECK LIVE PRICE ON AMAZON</span>
              <span>&rarr;</span>
            </a>

            {phone.id && (
              <button
                type="button"
                className="btn-secondary"
                onClick={handleCompareClick}
                id="report-compare-btn"
              >
                COMPARE WITH OTHER MODELS
              </button>
            )}
          </div>
        </div>
      </section>

      {/* Translated Capabilities */}
      <section className={styles.capabilitiesGrid} aria-label="Capability Analysis">
        <div className={styles.capabilityCard}>
          <div className={styles.capabilityHeader}>
            <span className={styles.capabilityTitle}>COMPUTE & CHIPSET</span>
          </div>
          <span className={styles.capabilityValue}>
            {phone.specs?.processor || 'Standard Platform'}
          </span>
          <p className={styles.capabilityDesc}>
            RAM: {phone.specs?.ram || 'Standard'} &bull; Storage: {phone.specs?.storage || 'Standard'}
          </p>
        </div>

        <div className={styles.capabilityCard}>
          <div className={styles.capabilityHeader}>
            <span className={styles.capabilityTitle}>OPTICS & SENSORS</span>
          </div>
          <span className={styles.capabilityValue}>
            {phone.specs?.mainCamera || 'Multi-Lens System'}
          </span>
          <p className={styles.capabilityDesc}>
            Front Camera: {phone.specs?.selfieCamera || 'HD Sensor'}
          </p>
        </div>

        <div className={styles.capabilityCard}>
          <div className={styles.capabilityHeader}>
            <span className={styles.capabilityTitle}>ENERGY & CHARGING</span>
          </div>
          <span className={styles.capabilityValue}>
            {phone.specs?.battery || 'All-Day Stamina'}
          </span>
          <p className={styles.capabilityDesc}>
            Speed: {phone.specs?.charging || 'Standard Charging'}
          </p>
        </div>

        <div className={styles.capabilityCard}>
          <div className={styles.capabilityHeader}>
            <span className={styles.capabilityTitle}>DISPLAY ARCHITECTURE</span>
          </div>
          <span className={styles.capabilityValue}>
            {phone.specs?.display || 'High Refresh Panel'}
          </span>
          <p className={styles.capabilityDesc}>
            Size: {phone.specs?.displaySize || 'Full Screen'} &bull; OS: {phone.specs?.os || 'Android'}
          </p>
        </div>
      </section>

      {/* Full Spec Matrix */}
      <section className={styles.specsSection} aria-label="Detailed Specifications">
        <div className={styles.specHeaderRow}>
          <span className="label-caps">COMPREHENSIVE HARDWARE SPECIFICATIONS</span>
        </div>

        {Object.entries(categorized).map(([category, specsObj]) => (
          <div key={category} className={styles.specCategoryBlock}>
            <span className={styles.specCategoryTitle}>{category}</span>
            <div className={styles.specGrid}>
              {Object.entries(specsObj).map(([key, val]) => (
                <div key={key} className={styles.specRow}>
                  <span className={styles.specLabel}>{key}</span>
                  <span className={styles.specDetail}>{val}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </section>
    </div>
  );
}
