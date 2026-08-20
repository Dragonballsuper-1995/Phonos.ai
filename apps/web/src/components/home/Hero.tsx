import Link from 'next/link';
import styles from './Hero.module.css';

export default function Hero() {
  return (
    <section className={styles.heroSection} aria-label="Introduction">
      <div className={styles.systemBadge}>
        <span className={styles.statusDot} />
        <span className="label-caps">INDIA SMARTPHONE INTELLIGENCE ENGINE &bull; DECODE YOUR COMPANION</span>
      </div>

      <h1 className={styles.headline}>
        STOP GUESSING. <br />
        <span className={styles.vermilionText}>START</span> <br />
        KNOWING.
      </h1>

      <div className={styles.subGrid}>
        <p className={styles.subline}>
          Decode your daily digital companion with zero sponsored bias. Phonos.ai runs
          8-stage multi-factor verification across India&apos;s live smartphone catalogue &mdash;
          no brand deals, pure engineering truth.
        </p>

        <div className={styles.ctaGroup}>
          <a href="#modes" className="btn-primary" id="hero-cta-button">
            FIND MY SMARTPHONE &darr;
          </a>
          <span className="body-sm">No affiliate bias &bull; AI defect filtering &bull; 100% transparent</span>
        </div>
      </div>

      <div className={styles.metaList}>
        <div className={styles.metaItem}>
          <span className={styles.metaValue}>8-STAGE</span>
          <span className={styles.metaLabel}>Waterfall Pipeline</span>
        </div>
        <div className={styles.metaItem}>
          <span className={styles.metaValue}>1,430+</span>
          <span className={styles.metaLabel}>Phones Verified</span>
        </div>
        <div className={styles.metaItem}>
          <span className={styles.metaValue}>ABSA+XGB</span>
          <span className={styles.metaLabel}>Aspect Sentiment ML</span>
        </div>
        <div className={styles.metaItem}>
          <span className={styles.metaValue}>100%</span>
          <span className={styles.metaLabel}>India Market Truth</span>
        </div>
      </div>
    </section>
  );
}
