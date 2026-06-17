'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import gsap from 'gsap';

export function CinematicPreloader() {
  const [loading, setLoading] = useState(true);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const dummyObj = { val: 0 };
    gsap.to(dummyObj, {
      val: 100,
      duration: 2.5,
      ease: "power2.inOut",
      onUpdate: () => {
        setProgress(Math.round(dummyObj.val));
      },
      onComplete: () => {
        // Hold at 100 for a beat before opening
        setTimeout(() => setLoading(false), 500);
      }
    });
  }, []);

  return (
    <AnimatePresence>
      {loading && (
        <motion.div
          initial={{ opacity: 1 }}
          exit={{ y: "-100%" }}
          transition={{ duration: 0.8, ease: [0.76, 0, 0.24, 1] }}
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: '#000',
            color: '#fff',
            zIndex: 10000,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            fontFamily: 'var(--font-body)'
          }}
        >
          <div style={{ position: 'relative', width: '300px', height: '2px', backgroundColor: '#333' }}>
            <motion.div 
              style={{ height: '100%', backgroundColor: 'var(--accent)' }}
              initial={{ width: '0%' }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.1 }}
            />
          </div>
          <div style={{ marginTop: '20px', letterSpacing: '0.1em', fontSize: '0.9rem' }}>
            INGESTING DATA MODELS: {progress}%
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
