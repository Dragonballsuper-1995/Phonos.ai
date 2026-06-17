import React from 'react';
import { cn } from '@/lib/utils';
import styles from './FeatureChip.module.css';

interface FeatureChipProps {
  label: string;
  icon?: string;
  isSelected: boolean;
  onClick: () => void;
}

export function FeatureChip({ label, icon, isSelected, onClick }: FeatureChipProps) {
  return (
    <button
      className={cn(styles.chip, isSelected && styles.selected)}
      onClick={onClick}
      type="button"
    >
      {icon && <span className={styles.icon}>{icon}</span>}
      <span className={styles.label}>{label}</span>
      {isSelected && (
        <span className={styles.check}>✓</span>
      )}
    </button>
  );
}
