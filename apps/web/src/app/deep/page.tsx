'use client';

import { useState, useEffect, useRef } from 'react';
import gsap from 'gsap';
import { TextPlugin } from 'gsap/TextPlugin';
import styles from './deep.module.css';

if (typeof window !== "undefined") {
  gsap.registerPlugin(TextPlugin);
}

export default function DeepMode() {
  const [messages, setMessages] = useState<{role: 'ai' | 'user', text: string}[]>([]);
  const [inputValue, setInputValue] = useState('');
  const aiTextRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    // Initial AI Greeting
    const greeting = "Initialize neural handshake. Define your parameters.";
    setMessages([{ role: 'ai', text: greeting }]);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    setMessages(prev => [...prev, { role: 'user', text: inputValue }]);
    setInputValue('');

    // Simulate AI thinking and responding
    setTimeout(() => {
      setMessages(prev => [...prev, { role: 'ai', text: "Processing latent space vectors... Waitlist active. Check back soon." }]);
    }, 1000);
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
