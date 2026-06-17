'use client';

import { useEffect, useRef } from 'react';
import Link from 'next/link';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import styles from './page.module.css';

if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

export default function Home() {
  const containerRef = useRef<HTMLDivElement>(null);
  const heroTextRef = useRef<HTMLHeadingElement>(null);
  const scrollWrapperRef = useRef<HTMLDivElement>(null);
  const horizontalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // 1. Hero Parallax & Fade
    gsap.to(heroTextRef.current, {
      y: 200,
      opacity: 0,
      ease: "none",
      scrollTrigger: {
        trigger: containerRef.current,
        start: "top top",
        end: "800px top",
        scrub: true,
      }
    });

    // 2. Horizontal Scroll Section
    if (scrollWrapperRef.current && horizontalRef.current) {
      const scrollWidth = horizontalRef.current.scrollWidth - window.innerWidth;
      
      gsap.to(horizontalRef.current, {
        x: -scrollWidth,
        ease: "none",
        scrollTrigger: {
          trigger: scrollWrapperRef.current,
          start: "top top",
          end: `+=${scrollWidth}`,
          scrub: 1,
          pin: true,
        }
      });
    }

    return () => {
      ScrollTrigger.getAll().forEach(t => t.kill());
    };
  }, []);

  return (
    <div className={styles.mainContainer} ref={containerRef}>
      
      {/* 1. Cinematic Hero */}
      <section className={styles.heroSection}>
        <div className={styles.heroContent} ref={heroTextRef}>
          <h1 className={`${styles.massiveText} display-text`}>
            DISCOVER<br/>
            <span className="outline-text">DECIDE.</span>
          </h1>
          <p className={styles.heroSub}>
            THE NEURAL ENGINE FOR HARDWARE INTELLIGENCE.
          </p>
        </div>
        <div className={styles.scrollIndicator}>
          SCROLL TO INGEST
          <div className={styles.scrollLine}></div>
        </div>
      </section>

      {/* 2. Horizontal Scroll Data Sequence */}
      <section className={styles.horizontalWrapper} ref={scrollWrapperRef}>
        <div className={styles.horizontalContent} ref={horizontalRef}>
          <div className={styles.hPanel}>
            <h2 className="display-text">1,000+ MODELS</h2>
            <p>We indexed the entire modern smartphone landscape. Prices, specs, and reviews.</p>
          </div>
          <div className={styles.hPanel}>
            <h2 className="display-text">VECTOR MATH</h2>
            <p>No arbitrary sorting. Strict mathematical similarity based on 50+ data dimensions.</p>
          </div>
          <div className={styles.hPanel}>
            <h2 className="display-text outline-text">NO BIAS.</h2>
            <p>Pure algorithmic recommendations.</p>
          </div>
        </div>
      </section>

      {/* 3. The Split Screen Path Selector */}
      <section className={styles.splitSection}>
        <div className={styles.splitLeft}>
          <h2 className="display-text">CHOOSE<br/>YOUR<br/>PATH.</h2>
        </div>
        <div className={styles.splitRight}>
          <Link href="/easy" className={styles.pathBlock}>
            <div className={styles.pathContent}>
              <span className={styles.pathNumber}>01</span>
              <h3 className="display-text">GUIDED SEARCH</h3>
              <p>Curated personas for instant discovery.</p>
            </div>
            <div className={styles.pathHoverBg}></div>
          </Link>

          <Link href="/medium" className={styles.pathBlock}>
            <div className={styles.pathContent}>
              <span className={styles.pathNumber}>02</span>
              <h3 className="display-text">PARAMETER CONTROL</h3>
              <p>Manual slider weighting for enthusiasts.</p>
            </div>
            <div className={styles.pathHoverBg}></div>
          </Link>

          <Link href="/deep" className={styles.pathBlock}>
            <div className={styles.pathContent}>
              <span className={styles.pathNumber}>03</span>
              <h3 className="display-text">NEURAL CHAT</h3>
              <p>Conversational LLM discovery.</p>
            </div>
            <div className={styles.pathHoverBg}></div>
          </Link>
        </div>
      </section>

      {/* 4. Magnetic Footer / CTA */}
      <section className={styles.footerCTA}>
        <Link href="/easy" className={styles.magneticBtnWrapper}>
          <div className={styles.magneticBtn}>
            <h2 className="display-text">BEGIN<br/>ENGINE</h2>
          </div>
        </Link>
      </section>

    </div>
  );
}
