'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import styles from './Nav.module.css';

export default function Nav() {
  const pathname = usePathname();
  const isModeFlow = pathname === '/easy' || pathname === '/medium' || pathname === '/deep';

  return (
    <nav className={styles.navBar} aria-label="Main Navigation">
      <Link href="/" className={styles.brand} id="nav-brand">
        <span>PHONOS.AI</span>
        <span className={styles.brandDot} />
      </Link>

      {isModeFlow ? (
        <Link href="/" className={styles.backLink} id="nav-exit-flow">
          <span>&larr;</span> EXIT TO HOME
        </Link>
      ) : (
        <ul className={styles.navLinks}>
          <li className={styles.navItem}>
            <Link
              href="/easy"
              className={`${styles.navLink} ${pathname === '/easy' ? styles.activeLink : ''}`}
              id="nav-link-easy"
            >
              Easy
            </Link>
          </li>
          <li className={styles.navItem}>
            <Link
              href="/medium"
              className={`${styles.navLink} ${pathname === '/medium' ? styles.activeLink : ''}`}
              id="nav-link-medium"
            >
              Medium
            </Link>
          </li>
          <li className={styles.navItem}>
            <Link
              href="/deep"
              className={`${styles.navLink} ${pathname === '/deep' ? styles.activeLink : ''}`}
              id="nav-link-deep"
            >
              Deep
            </Link>
          </li>
        </ul>
      )}
    </nav>
  );
}
