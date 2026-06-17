'use client';

import React, { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import styles from './ScoreBar.module.css';

interface ScoreBarProps {
  label: string;
  score: number; // 0 to 100
  colorMap?: {
    high?: string;
    mid?: string;
    low?: string;
  };
}

export function ScoreBar({ label, score, colorMap }: ScoreBarProps) {
  const [width, setWidth] = useState(0);

  useEffect(() => {
    // Animate on mount
    const timer = setTimeout(() => {
      setWidth(score);
    }, 100);
    return () => clearTimeout(timer);
  }, [score]);

  const getColorClass = () => {
    if (score >= 80) return styles.high;
    if (score >= 60) return styles.mid;
    return styles.low;
  };

  // Inline style for custom colors if provided
  const customColorStyle = colorMap ? {
    backgroundColor: score >= 80 ? colorMap.high : score >= 60 ? colorMap.mid : colorMap.low
  } : {};

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <span className={styles.label}>{label}</span>
        <span className={styles.score}>{score}/100</span>
      </div>
      <div className={styles.track}>
        <div 
          className={cn(styles.fill, !colorMap && getColorClass())}
          style={{ 
            width: `${width}%`,
            ...customColorStyle
          }}
        />
      </div>
    </div>
  );
}
