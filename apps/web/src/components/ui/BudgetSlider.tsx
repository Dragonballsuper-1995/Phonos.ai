'use client';

import React, { useState, useEffect } from 'react';
import { formatPrice } from '@/lib/utils';
import { cn } from '@/lib/utils';
import styles from './BudgetSlider.module.css';

interface BudgetSliderProps {
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  className?: string;
}

const PRESETS = [
  { label: 'Under ₹15K', value: 15000 },
  { label: '₹15K - 25K', value: 25000 },
  { label: '₹25K - 40K', value: 40000 },
  { label: '₹40K+', value: 80000 },
];

export function BudgetSlider({ 
  value, 
  onChange, 
  min = 5000, 
  max = 150000, 
  step = 1000,
  className 
}: BudgetSliderProps) {
  const [localValue, setLocalValue] = useState(value);

  useEffect(() => {
    setLocalValue(value);
  }, [value]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = parseInt(e.target.value, 10);
    setLocalValue(newValue);
    onChange(newValue);
  };

  const percentage = ((localValue - min) / (max - min)) * 100;

  return (
    <div className={cn(styles.container, className)}>
      <div className={styles.header}>
        <span className={styles.label}>Max Budget</span>
        <span className={styles.value}>{formatPrice(localValue)}</span>
      </div>
      
      <div className={styles.sliderWrapper}>
        <div 
          className={styles.trackFill} 
          style={{ width: `${percentage}%` }}
        />
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={localValue}
          onChange={handleChange}
          className={styles.slider}
        />
      </div>
      
      <div className={styles.presets}>
        {PRESETS.map((preset) => (
          <button
            key={preset.label}
            className={cn(styles.presetBtn, localValue === preset.value && styles.activePreset)}
            onClick={() => {
              setLocalValue(preset.value);
              onChange(preset.value);
            }}
            type="button"
          >
            {preset.label}
          </button>
        ))}
      </div>
    </div>
  );
}
