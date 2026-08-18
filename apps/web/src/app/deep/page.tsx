'use client';

import { useState, useEffect, useRef } from 'react';
import gsap from 'gsap';
import { TextPlugin } from 'gsap/TextPlugin';
import styles from './deep.module.css';
import { useRouter } from 'next/navigation';

if (typeof window !== "undefined") {
  gsap.registerPlugin(TextPlugin);
}

export default function DeepMode() {
  const router = useRouter();
  const [messages, setMessages] = useState<{role: 'ai' | 'user', text: string}[]>([]);
  const [inputValue, setInputValue] = useState('');
  
  useEffect(() => {
    // Initial AI Greeting
    const greeting = "Initialize neural handshake. What do you need? (e.g. 'A great vlogging phone with amazing battery under 50k')";
    setMessages([{ role: 'ai', text: greeting }]);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    setMessages(prev => [...prev, { role: 'user', text: inputValue }]);
    
    // Attempt to extract a budget if they typed "under 40k" or "40000"
    let budget = 150000;
    const budgetMatch = inputValue.match(/(?:under|below|max)\s*(\d+)(k|000)?/i);
    if (budgetMatch) {
      let num = parseInt(budgetMatch[1]);
      if (budgetMatch[2] && budgetMatch[2].toLowerCase() === 'k') num *= 1000;
      else if (num < 1000) num *= 1000; // e.g. "under 50" -> 50000
      budget = num;
    }

    const query = inputValue;
    setInputValue('');

    // Simulate AI thinking and redirect
    setTimeout(() => {
      setMessages(prev => [...prev, { role: 'ai', text: "Processing latent space vectors... Routing to results." }]);
      setTimeout(() => {
        router.push(`/results?mode=deep&q=${encodeURIComponent(query)}&budget=${budget}`);
      }, 1000);
    }, 500);
  };

  return (
    <div className={styles.terminalContainer}>
      <div className={styles.terminalLog}>
        {messages.map((msg, idx) => (
          <div key={idx} className={`${styles.messageLine} ${msg.role === 'ai' ? styles.aiMsg : styles.userMsg}`}>
            <span className={styles.prompt}>
              {msg.role === 'ai' ? 'SYS>' : 'USR>'}
            </span>
            <span className={styles.text}>{msg.text}</span>
          </div>
        ))}
      </div>

      <form className={styles.inputArea} onSubmit={handleSubmit}>
        <span className={styles.prompt}>USR&gt;</span>
        <input 
          type="text" 
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          className={styles.massiveInput}
          autoFocus
          spellCheck={false}
        />
        <div className={styles.cursorBlink}></div>
      </form>
    </div>
  );
}
