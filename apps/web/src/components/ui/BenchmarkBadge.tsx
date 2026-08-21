import React from 'react';
import styles from './BenchmarkBadge.module.css';

export type BenchmarkType = 'dxomark-camera' | 'dxomark-display' | 'vcx' | 'geekbench' | 'antutu' | 'battery';

interface BenchmarkBadgeProps {
  type: BenchmarkType;
  value: number;
  label?: string;
  className?: string;
}

export default function BenchmarkBadge({ type, value, label, className = '' }: BenchmarkBadgeProps) {
  let displayLabel = label;
  let typeClass = styles.dxomark;
  let icon = '★';

  switch (type) {
    case 'dxomark-camera':
      typeClass = styles.dxomark;
      displayLabel = displayLabel || `DxOMark ${Math.round(value)}`;
      icon = '📷';
      break;
    case 'dxomark-display':
      typeClass = styles.dxomark;
      displayLabel = displayLabel || `DxO Display ${Math.round(value)}`;
      icon = '🖥️';
      break;
    case 'vcx':
      typeClass = styles.vcx;
      displayLabel = displayLabel || `VCX ${Math.round(value)}★`;
      icon = '🔬';
      break;
    case 'geekbench':
      typeClass = styles.geekbench;
      displayLabel = displayLabel || `GB6 ${value.toLocaleString()}`;
      icon = '⚡';
      break;
    case 'antutu':
      typeClass = styles.antutu;
      displayLabel = displayLabel || `AnTuTu ${(value / 1000000).toFixed(1)}M`;
      icon = '🚀';
      break;
    case 'battery':
      typeClass = styles.battery;
      displayLabel = displayLabel || `${value.toFixed(1)}h AUS`;
      icon = '🔋';
      break;
  }

  return (
    <span
      className={`${styles.badge} ${typeClass} ${className}`}
      title={`${type.toUpperCase()} Lab Score: ${value}`}
    >
      <span className={styles.icon}>{icon}</span>
      <span>{displayLabel}</span>
    </span>
  );
}
