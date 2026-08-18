'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { usePostHog } from 'posthog-js/react';
import { PERSONAS, BUDGET_DEFAULT } from '@/lib/constants';
import BudgetSlider from '@/components/ui/BudgetSlider';
import styles from './PersonaFlow.module.css';

export default function PersonaFlow() {
  const router = useRouter();
  const posthog = usePostHog();
  const [step, setStep] = useState<1 | 2>(1);
  const [selectedPersona, setSelectedPersona] = useState<string>('student');
  const [budget, setBudget] = useState<number>(BUDGET_DEFAULT);

  const handleSelectPersona = (id: string, name: string) => {
    setSelectedPersona(id);
    if (posthog) {
      posthog.capture('persona_selected', {
        persona_id: id,
        persona_name: name,
      });
    }
    setStep(2);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (posthog) {
      posthog.capture('budget_set', {
        mode: 'easy',
        persona: selectedPersona,
        budget_amount: budget,
      });
    }

    const query = new URLSearchParams({
      mode: 'easy',
      persona: selectedPersona,
      budget: budget.toString(),
    }).toString();

    router.push(`/results?${query}`);
  };

  const currentPersonaObj = PERSONAS.find((p) => p.id === selectedPersona) || PERSONAS[0];

  return (
    <div className={styles.container}>
      {step === 1 ? (
        <div role="region" aria-label="Step 1: Choose Persona">
          <div className={styles.stepHeader}>
            <span className={`label-caps ${styles.stepIndicator}`}>EASY MODE &bull; STEP 01 OF 02</span>
            <h1 className={styles.stepTitle}>WHO ARE YOU?</h1>
            <p className={styles.stepSubtitle}>
              Select your primary lifestyle profile. The engine will weight hardware benchmarks and feature priorities accordingly.
            </p>
          </div>

          <div className={styles.personaList}>
            {PERSONAS.map((persona, index) => (
              <button
                key={persona.id}
                type="button"
                className={styles.personaRow}
                onClick={() => handleSelectPersona(persona.id, persona.name)}
                id={`persona-option-${persona.id}`}
              >
                <span className={styles.personaIndex}>0{index + 1}</span>
                <div className={styles.personaContent}>
                  <span className={styles.personaName}>{persona.name}</span>
                  <span className={styles.personaDesc}>{persona.description}</span>
                </div>
                <span className={styles.personaAction}>SELECT &rarr;</span>
              </button>
            ))}
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} role="region" aria-label="Step 2: Set Budget">
          <div className={styles.stepHeader}>
            <span className={`label-caps ${styles.stepIndicator}`}>EASY MODE &bull; STEP 02 OF 02</span>
            <h1 className={styles.stepTitle}>SET YOUR LIMIT.</h1>
            <p className={styles.stepSubtitle}>
              Define your maximum financial allocation in Indian Rupees. We will only return models that deliver maximum value within this ceiling.
            </p>
          </div>

          <div className={styles.budgetCard}>
            <div className={styles.selectedSummary}>
              <div className={styles.selectedTag}>
                <span className="label-caps">PROFILE:</span>
                <span className={styles.selectedPersonaName}>{currentPersonaObj.name}</span>
              </div>
              <button
                type="button"
                className={styles.backBtn}
                onClick={() => setStep(1)}
              >
                &larr; CHANGE PROFILE
              </button>
            </div>

            <BudgetSlider
              value={budget}
              onChange={setBudget}
              label="Maximum Budget Allocation"
            />

            <div className={styles.actionRow}>
              <button
                type="button"
                className="btn-secondary"
                onClick={() => setStep(1)}
              >
                &larr; BACK
              </button>

              <button
                type="submit"
                className="btn-primary"
                id="easy-submit-btn"
              >
                ANALYZE BEST MATCHES &rarr;
              </button>
            </div>
          </div>
        </form>
      )}
    </div>
  );
}
