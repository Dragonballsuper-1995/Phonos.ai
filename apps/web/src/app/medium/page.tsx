'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import styles from './medium.module.css';

export default function MediumMode() {
  const router = useRouter();
  const [budget, setBudget] = useState(40000);
  const [weights, setWeights] = useState({
    performance: 0.5,
    camera: 0.5,
    battery: 0.5,
    display: 0.5,
    value: 0.5
  });

  const handleWeightChange = (key: keyof typeof weights, value: number) => {
    setWeights(prev => ({ ...prev, [key]: value }));
  };

  const handleLaunch = () => {
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
    <div className={styles.boardContainer}>
      <div className={styles.topBar}>
        <div className={styles.sysInfo}>SYS.MODE: PARAMETER_CONTROL // ROOT</div>
        <div className={styles.sysStatus}>STATUS: STANDBY</div>
      </div>

      <div className={styles.mainGrid}>
        
        {/* Left Column: Budget & Execute */}
        <div className={styles.commandCol}>
          <div className={styles.panel}>
            <h2 className={styles.panelTitle}>MAXIMUM_ALLOCATION</h2>
            <div className={styles.budgetReadout}>
              INR_{budget.toLocaleString('en-IN')}
            </div>
            <input 
              type="range" 
              min="5000" 
              max="150000" 
              step="1000"
              value={budget}
              onChange={(e) => setBudget(parseInt(e.target.value))}
              className={styles.brutalSlider}
            />
          </div>

          <button className={styles.executeBtn} onClick={handleLaunch}>
            <span className={styles.blink}>&gt;</span> EXECUTE_QUERY
          </button>
        </div>

        {/* Right Column: Weights */}
        <div className={styles.weightsCol}>
          <h2 className={styles.panelTitle}>HEURISTIC_WEIGHTS</h2>
          <div className={styles.weightsList}>
            {Object.entries(weights).map(([key, val]) => (
              <div key={key} className={styles.weightItem}>
                <div className={styles.weightLabel}>
                  VOL_{key.toUpperCase()}
                </div>
                <div className={styles.weightControl}>
                  <input 
                    type="range" 
                    min="0" 
                    max="1" 
                    step="0.1"
                    value={val}
                    onChange={(e) => handleWeightChange(key as any, parseFloat(e.target.value))}
                    className={styles.brutalSlider}
                  />
                  <div className={styles.weightValue}>
                    {(val * 100).toFixed(0).padStart(3, '0')}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
