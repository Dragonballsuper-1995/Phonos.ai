'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { usePostHog } from 'posthog-js/react';
import styles from './NaturalInput.module.css';

const SAMPLE_PROMPTS = [
  'Best camera phone under ₹45,000 for travel and portrait photography',
  'Clean stock Android experience with all-day battery under ₹30,000',
  'Compact flagship smartphone with great haptics and wireless charging',
  'High FPS gaming phone with reliable cooling under ₹25,000',
];

export default function NaturalInput() {
  const router = useRouter();
  const posthog = usePostHog();
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) return;

    if (posthog) {
      posthog.capture('deep_query_submitted', {
        query_text: trimmed,
        query_length: trimmed.length,
      });
    }

    const params = new URLSearchParams({
      mode: 'deep',
      q: trimmed,
      budget: '150000',
    }).toString();

    router.push(`/results?${params}`);
  };

  const handleSelectPrompt = (promptText: string) => {
    setQuery(promptText);
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <span className="label-caps">DEEP MODE &bull; SEMANTIC REASONING</span>
        <h1 className={styles.title}>DESCRIBE YOUR REQUIREMENTS</h1>
        <p className="body-md">
          Type naturally in plain English. The backend extracts implicit hardware demands, price limits, and feature priorities automatically.
        </p>
      </div>

      <form onSubmit={handleSubmit} className={styles.inputCard}>
        <div className={styles.inputGroup}>
          <input
            type="text"
            className={styles.textInput}
            id="deep-text-input"
            aria-label="Describe what phone you are looking for"
            placeholder="e.g. Best phone under ₹40k with flagship cameras and fast charging"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoFocus
            maxLength={250}
          />
          <span className={styles.charCount}>{query.length}/250</span>
        </div>

        <div className={styles.suggestions}>
          <span className={styles.suggestionLabel}>OR TRY A PROMPT:</span>
          <div className={styles.chipsList}>
            {SAMPLE_PROMPTS.map((prompt) => (
              <button
                key={prompt}
                type="button"
                className={styles.chipBtn}
                onClick={() => handleSelectPrompt(prompt)}
              >
                &ldquo;{prompt}&rdquo;
              </button>
            ))}
          </div>
        </div>

        <div className={styles.actionRow}>
          <span className="body-sm">Uses semantic vector search across Indian models</span>
          <button
            type="submit"
            className="btn-primary"
            id="deep-submit-btn"
            disabled={!query.trim()}
            style={{ opacity: query.trim() ? 1 : 0.4 }}
          >
            START NEURAL ANALYSIS &rarr;
          </button>
        </div>
      </form>
    </div>
  );
}
