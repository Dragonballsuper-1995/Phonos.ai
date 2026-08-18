'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { usePostHog } from 'posthog-js/react';
import { HEURISTIC_ASPECTS, BUDGET_DEFAULT } from '@/lib/constants';
import BudgetSlider from '@/components/ui/BudgetSlider';
import styles from './WeightsPanel.module.css';

export default function WeightsPanel() {
  const router = useRouter();
  const posthog = usePostHog();

  const [budget, setBudget] = useState<number>(BUDGET_DEFAULT);
  const [weights, setWeights] = useState<Record<string, number>>({
    performance: 0.5,
    camera: 0.5,
    battery: 0.5,
    display: 0.5,
    value: 0.5,
  });

  const handleWeightChange = (key: string, val: number) => {
    setWeights((prev) => ({ ...prev, [key]: val }));
  };

  const handleEqualize = () => {
    setWeights({
      performance: 0.5,
      camera: 0.5,
      battery: 0.5,
      display: 0.5,
      value: 0.5,
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (posthog) {
      posthog.capture('medium_weights_submitted', {
        budget,
        w_perf: weights.performance,
        w_cam: weights.camera,
        w_bat: weights.battery,
        w_disp: weights.display,
        w_val: weights.value,
      });
    }

    const query = new URLSearchParams({
      mode: 'medium',
      budget: budget.toString(),
      w_perf: weights.performance.toString(),
      w_cam: weights.camera.toString(),
      w_bat: weights.battery.toString(),
      w_disp: weights.display.toString(),
      w_val: weights.value.toString(),
    }).toString();

    router.push(`/results?${query}`);
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <span className="label-caps">MEDIUM MODE &bull; PARAMETER CONTROL</span>
        <h1 className={styles.title}>FINE-TUNE YOUR PRIORITIES</h1>
        <p className="body-md">
          Adjust the heuristic sliders below to emphasize specific dimensions. The XGBoost ranker balances your inputs against real benchmark data.
        </p>
      </div>

      <form onSubmit={handleSubmit} className={styles.grid}>
        {/* Left Column: Budget & Execute */}
        <div className={styles.column}>
          <div className={styles.panelTitle}>
            <span>01 &bull; FINANCIAL ALLOCATION</span>
          </div>

          <BudgetSlider
            value={budget}
            onChange={setBudget}
            label="Maximum Target Budget"
          />

          <div className={styles.submitBlock}>
            <button
              type="submit"
              className="btn-primary"
              id="medium-execute-btn"
            >
              EXECUTE HEURISTIC SEARCH &rarr;
            </button>
            <span className="body-sm" style={{ textAlign: 'center' }}>
              Scores updated dynamically across database
            </span>
          </div>
        </div>

        {/* Right Column: Weights */}
        <div className={styles.column}>
          <div className={styles.panelTitle}>
            <span>02 &bull; ASPECT WEIGHT MULTIPLIERS</span>
            <button
              type="button"
              className={styles.equalizeBtn}
              onClick={handleEqualize}
            >
              RESET ALL TO 50%
            </button>
          </div>

          <div className={styles.weightsList}>
            {HEURISTIC_ASPECTS.map((aspect) => {
              const currentVal = weights[aspect.key] ?? 0.5;
              const percent = Math.round(currentVal * 100);

              return (
                <div key={aspect.key} className={styles.weightItem}>
                  <div className={styles.weightHeader}>
                    <span className={styles.weightLabel}>{aspect.label}</span>
                    <span className={styles.weightValue}>{percent}%</span>
                  </div>

                  <span className={styles.weightDesc}>{aspect.description}</span>

                  <div className={styles.sliderRow}>
                    <input
                      type="range"
                      id={`slider-${aspect.key}`}
                      aria-label={`${aspect.label} priority`}
                      min="0.1"
                      max="1.0"
                      step="0.05"
                      value={currentVal}
                      onChange={(e) =>
                        handleWeightChange(aspect.key, parseFloat(e.target.value))
                      }
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </form>
    </div>
  );
}
