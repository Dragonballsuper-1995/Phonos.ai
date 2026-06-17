import React from 'react';
import { cn } from '@/lib/utils';
import styles from './StepIndicator.module.css';

interface StepIndicatorProps {
  currentStep: number;
  totalSteps: number;
}

export function StepIndicator({ currentStep, totalSteps }: StepIndicatorProps) {
  return (
    <div className={styles.container}>
      <div className={styles.text}>
        <span>Step {currentStep} of {totalSteps}</span>
      </div>
      <div className={styles.track}>
        <div 
          className={styles.fill} 
          style={{ width: `${(currentStep / totalSteps) * 100}%` }}
        />
      </div>
      <div className={styles.dots}>
        {Array.from({ length: totalSteps }).map((_, i) => (
          <div 
            key={i} 
            className={cn(
              styles.dot,
              i + 1 === currentStep && styles.activeDot,
              i + 1 < currentStep && styles.completedDot
            )} 
          />
        ))}
      </div>
    </div>
  );
}
