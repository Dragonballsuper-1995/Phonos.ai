import React from 'react';
import { cn } from '@/lib/utils';
import styles from './PersonaCard.module.css';
import { Persona } from '@/lib/types';

interface PersonaCardProps {
  persona: Persona;
  isSelected: boolean;
  onClick: () => void;
}

export function PersonaCard({ persona, isSelected, onClick }: PersonaCardProps) {
  return (
    <button
      className={cn(styles.card, isSelected && styles.selected)}
      onClick={onClick}
      type="button"
    >
      <div className={styles.icon}>{persona.icon}</div>
      <h3 className={styles.name}>{persona.name}</h3>
      <p className={styles.description}>{persona.description}</p>
      
      {isSelected && (
        <div className={styles.checkWrapper}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className={styles.checkIcon}>
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
        </div>
      )}
    </button>
  );
}
