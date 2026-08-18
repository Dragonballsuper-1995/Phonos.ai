import Link from 'next/link';
import styles from './Hero.module.css';

export default function Hero() {
  return (
    <section className={styles.heroSection} aria-label="Introduction">
      <div className={styles.systemBadge}>
        <span className={styles.statusDot} />
        <span className="label-caps">INDIA SMARTPHONE INTELLIGENCE ENGINE</span>
      </div>

      <h1 className={styles.headline}>
        TELL US WHAT <br />
        YOU NEED. <span className={styles.vermilionText}>WE DECIDE</span> <br />
        WITH ZERO BIAS.
      </h1>

      <div className={styles.subGrid}>
        <p className={styles.subline}>
          Phonos.ai searches India&apos;s real smartphone market, filters out hardware defects, ranks
          candidates using 8-stage multi-factor intelligence, and explains exactly why the winners fit your life.
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
          <span className={styles.metaValue}>1,200+</span>
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
