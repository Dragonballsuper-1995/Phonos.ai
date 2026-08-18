import Link from 'next/link';
import { MODES } from '@/lib/constants';
import styles from './ModePicker.module.css';

export default function ModePicker() {
  return (
    <section className={styles.pickerSection} id="modes" aria-label="Recommendation Modes">
      <div className={styles.header}>
        <span className="label-caps">CHOOSE YOUR PATH</span>
        <h2 className={styles.sectionTitle}>SELECT RECOMMENDATION DEPTH</h2>
        <p className="body-md">
          Every mode accesses the same 8-stage verification pipeline. Choose the interaction model that fits your intent.
        </p>
      </div>

      <div className={styles.grid}>
        {MODES.map((mode, index) => (
          <Link
            key={mode.id}
            href={mode.href}
            className={styles.tile}
            id={`mode-card-${mode.id}`}
          >
            <div className={styles.tileTop}>
              <div className={styles.tileMeta}>
                <span className={styles.index}>0{index + 1}</span>
                <span className={styles.badge}>{mode.badge}</span>
              </div>

              <div className={styles.titleBlock}>
                <h3 className={styles.modeName}>{mode.name}</h3>
                <span className={styles.tagline}>{mode.tagline}</span>
              </div>

              <p className={styles.desc}>{mode.description}</p>
            </div>

            <div className={styles.tileAction}>
              <span>ENTER {mode.name.toUpperCase()} MODE</span>
              <span className={styles.arrow}>&rarr;</span>
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}
