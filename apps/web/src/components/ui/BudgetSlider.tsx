'use client';

import { BUDGET_MIN, BUDGET_MAX, BUDGET_STEP } from '@/lib/constants';
import styles from './BudgetSlider.module.css';

interface BudgetSliderProps {
  value: number;
  onChange: (val: number) => void;
  label?: string;
}

const PRESETS = [15000, 25000, 40000, 60000, 100000];

export default function BudgetSlider({
  value,
  onChange,
  label = 'Maximum Budget',
}: BudgetSliderProps) {
  return (
    <div className={styles.wrapper}>
      <div className={styles.readoutBlock}>
        <span className={styles.label}>{label}</span>
        <div className={styles.amount}>
          <span className={styles.currency}>&#8377;</span>
          {value.toLocaleString('en-IN')}
        </div>
      </div>

      <div className={styles.sliderContainer}>
        <input
          type="range"
          id="budget-range-input"
          aria-label={label}
          min={BUDGET_MIN}
          max={BUDGET_MAX}
          step={BUDGET_STEP}
          value={value}
          onChange={(e) => onChange(parseInt(e.target.value, 10))}
        />
        <div className={styles.bounds}>
          <span>&#8377;{BUDGET_MIN.toLocaleString('en-IN')}</span>
          <span>&#8377;{BUDGET_MAX.toLocaleString('en-IN')}+</span>
        </div>
      </div>

      <div className={styles.presets}>
        {PRESETS.map((preset) => (
          <button
            key={preset}
            type="button"
            className={`${styles.presetBtn} ${value === preset ? styles.presetBtnActive : ''}`}
            onClick={() => onChange(preset)}
          >
            &#8377;{preset >= 100000 ? `${preset / 100000}L` : `${preset / 1000}K`}
          </button>
        ))}
      </div>
    </div>
  );
}
