import styles from './Footer.module.css';
import Link from 'next/link';

export function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={styles.container}>
        <div className={styles.content}>
          <div className={styles.brand}>
            <Link href="/" className={styles.logo}>
              Fone<span>.ai</span>
            </Link>
            <p className={styles.tagline}>AI-powered smartphone recommender for the Indian market.</p>
          </div>
          
          <div className={styles.links}>
            <div className={styles.column}>
              <h4>Modes</h4>
              <Link href="/easy">Easy Mode</Link>
              <Link href="/medium">Medium Mode</Link>
              <Link href="/deep">Deep Mode</Link>
            </div>
            <div className={styles.column}>
              <h4>Project</h4>
              <a href="https://github.com/sujal/fone.ai" target="_blank" rel="noopener noreferrer">GitHub</a>
              <Link href="/about">About</Link>
            </div>
          </div>
        </div>
        
        <div className={styles.bottom}>
          <p>Built with ❤️ by Sujal</p>
          <div className={styles.badges}>
            <span className={styles.badge}>Next.js 15</span>
            <span className={styles.badge}>FastAPI</span>
            <span className={styles.badge}>AI</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
