'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { PERSONAS } from '@/lib/constants';
import styles from './easy.module.css';

const slideVariants = {
  enter: { y: "100%", opacity: 0 },
  center: { y: "0%", opacity: 1 },
  exit: { y: "-100%", opacity: 0 }
};

export default function EasyMode() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [hoveredPersona, setHoveredPersona] = useState<string | null>(null);
  
  const [formData, setFormData] = useState({
    personaId: '',
    budget: 30000,
  });

  const handlePersonaSelect = (id: string) => {
    setFormData(prev => ({ ...prev, personaId: id }));
    setTimeout(() => setStep(2), 400); // Small delay for cinematic feel
  };

  const handleBudgetSubmit = () => {
    const query = new URLSearchParams({
      mode: 'easy',
      persona: formData.personaId,
      budget: formData.budget.toString(),
    }).toString();
    
    // Simulate cinematic transition
    setTimeout(() => {
      router.push(`/results?${query}`);
    }, 600);
  };

  return (
    <div className={styles.container}>
      {/* Dynamic Background based on hover */}
      <div 
        className={styles.dynamicBg}
        style={{ 
          opacity: hoveredPersona ? 0.3 : 0,
          backgroundColor: hoveredPersona 
            ? PERSONAS.find(p => p.id === hoveredPersona)?.color 
            : 'var(--accent)'
        }} 
      />

      <AnimatePresence mode="wait">
        {step === 1 && (
          <motion.div 
            key="step1"
            className={styles.stepWrapper}
            variants={slideVariants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{ duration: 0.8, ease: [0.76, 0, 0.24, 1] }}
          >
            <h1 className={`${styles.stepTitle} display-text outline-text`}>WHO ARE YOU?</h1>
            <div className={styles.personaList}>
              {PERSONAS.map((persona, idx) => (
                <div 
                  key={persona.id}
                  className={styles.personaItem}
                  onMouseEnter={() => setHoveredPersona(persona.id)}
                  onMouseLeave={() => setHoveredPersona(null)}
                  onClick={() => handlePersonaSelect(persona.id)}
                >
                  <div className={styles.personaIndex}>0{idx + 1}</div>
                  <h2 className="display-text">{persona.name}</h2>
                  <div className={styles.personaHoverLine} />
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {step === 2 && (
          <motion.div 
            key="step2"
            className={styles.stepWrapper}
            variants={slideVariants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{ duration: 0.8, ease: [0.76, 0, 0.24, 1] }}
          >
            <h1 className={`${styles.stepTitle} display-text outline-text`}>DEFINE THE LIMIT.</h1>
            <div className={styles.sliderContainer}>
              <div className={styles.budgetDisplay}>
                ₹{formData.budget.toLocaleString('en-IN')}
              </div>
              <input 
                type="range" 
                min="5000" 
                max="150000" 
                step="5000"
                value={formData.budget}
                onChange={(e) => setFormData(prev => ({ ...prev, budget: parseInt(e.target.value) }))}
                className={styles.massiveSlider}
              />
              
              <button 
                className={`${styles.magneticBtn} display-text`}
                onClick={handleBudgetSubmit}
              >
                INITIALIZE
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
