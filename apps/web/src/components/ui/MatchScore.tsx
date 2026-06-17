'use client';

import React, { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import styles from './MatchScore.module.css';

interface MatchScoreProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
}

export function MatchScore({ score, size = 'md' }: MatchScoreProps) {
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    let start = 0;
    const end = Math.round(score);
    if (start === end) return;

    const duration = 1500;
    const incrementTime = (duration / end);
    
    const timer = setInterval(() => {
      start += 1;
      setAnimatedScore(start);
      if (start === end) clearInterval(timer);
    }, incrementTime);

    return () => clearInterval(timer);
  }, [score]);

  const radius = size === 'sm' ? 18 : size === 'md' ? 30 : 60;
  const stroke = size === 'sm' ? 3 : size === 'md' ? 4 : 8;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (animatedScore / 100) * circumference;

  const getColorClass = () => {
    if (score >= 85) return styles.excellent;
    if (score >= 70) return styles.good;
    return styles.fair;
  };

  return (
    <div className={cn(styles.container, styles[size])}>
      <svg
        height={radius * 2}
        width={radius * 2}
        className={styles.svg}
      >
        <circle
          stroke="var(--color-border)"
          strokeWidth={stroke}
          fill="transparent"
          r={normalizedRadius}
          cx={radius}
          cy={radius}
          className={styles.bgCircle}
        />
        <circle
          stroke="currentColor"
          fill="transparent"
          strokeWidth={stroke}
          strokeDasharray={circumference + ' ' + circumference}
          style={{ strokeDashoffset }}
          strokeLinecap="round"
          r={normalizedRadius}
          cx={radius}
          cy={radius}
          className={cn(styles.progressCircle, getColorClass())}
        />
      </svg>
      <div className={styles.textContainer}>
        <span className={styles.value}>{animatedScore}</span>
        <span className={styles.percent}>%</span>
      </div>
    </div>
  );
}
