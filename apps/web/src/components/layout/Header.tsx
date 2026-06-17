'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import styles from './Header.module.css';

export function Header() {
  const pathname = usePathname();
  const router = useRouter();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const links = [
    { label: 'HOME', href: '/' },
    { label: 'EASY MODE', href: '/easy' },
    { label: 'MEDIUM MODE', href: '/medium' },
    { label: 'DEEP MODE', href: '/deep' },
  ];

  return (
    <>
      <header className={styles.header}>
        <div className={styles.logo}>
          <Link href="/" className="display-text" onClick={() => setIsMenuOpen(false)}>
            FONE.AI
          </Link>
        </div>

        <div className={styles.actions}>
          <button 
            className={`${styles.magneticLink} display-text`}
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            [ {isMenuOpen ? 'CLOSE' : 'EXPLORE'} ]
          </button>
        </div>
      </header>

      <AnimatePresence>
        {isMenuOpen && (
          <motion.div 
            className={styles.menuOverlay}
            initial={{ y: "-100%" }}
            animate={{ y: 0 }}
            exit={{ y: "-100%" }}
            transition={{ duration: 0.8, ease: [0.76, 0, 0.24, 1] }}
          >
            <div className={styles.menuContent}>
              {links.map((link, idx) => {
                const isActive = pathname === link.href;
                return (
                  <motion.div
                    key={link.href}
                    initial={{ y: 50, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ delay: 0.4 + (idx * 0.1), duration: 0.6 }}
                  >
                    <Link 
                      href={link.href} 
                      className={`${styles.menuLink} display-text ${isActive ? styles.activeLink : ''}`}
                      onClick={() => setIsMenuOpen(false)}
                    >
                      {link.label}
                    </Link>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
