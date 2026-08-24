'use client';

import React, { useState, useRef } from 'react';
import Link from 'next/link';
import { usePostHog } from 'posthog-js/react';
import { api } from '@/lib/api';
import type { RecommendedPhone } from '@/lib/types';
import { cleanPhoneName } from '@/lib/specHelpers';
import ScoreBar from '@/components/ui/ScoreBar';
import VerifiedBadge from '@/components/ui/VerifiedBadge';
import BenchmarkBadge from '@/components/ui/BenchmarkBadge';
import styles from './DeepStreamView.module.css';

const SAMPLE_PROMPTS = [
  'Best camera phone under ₹45,000 for portrait photography and 4K video',
  'Clean stock Android experience with all-day battery under ₹30,000',
  'Compact flagship smartphone with great haptics and wireless charging',
  'High FPS gaming phone with reliable cooling for BGMI under ₹25,000',
];

interface ClarificationQuestion {
  id: string;
  question: string;
  options: string[];
}

export default function DeepStreamView() {
  const posthog = usePostHog();
  const [query, setQuery] = useState('');
  const [budget, setBudget] = useState(150000);
  const [isStreaming, setIsStreaming] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [reasoningText, setReasoningText] = useState('');
  const [clarifications, setClarifications] = useState<ClarificationQuestion[]>([]);
  const [selectedClarifications, setSelectedClarifications] = useState<Record<string, string>>({});
  const [recommendations, setRecommendations] = useState<RecommendedPhone[]>([]);
  const abortControllerRef = useRef<AbortController | null>(null);

  const startStream = async (queryText: string, currentBudget: number = budget, extraClarifications?: Record<string, string>) => {
    const trimmed = queryText.trim();
    if (!trimmed) return;

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const controller = new AbortController();
    abortControllerRef.current = controller;

    setIsStreaming(true);
    setStatusMessage('Connecting to neural reasoning copilot...');
    setReasoningText('');
    setClarifications([]);
    setRecommendations([]);

    if (posthog) {
      posthog.capture('deep_stream_initiated', {
        query: trimmed,
        budget: currentBudget,
        clarifications: extraClarifications,
      });
    }

    try {
      let combinedQuery = trimmed;
      if (extraClarifications && Object.keys(extraClarifications).length > 0) {
        const extraText = Object.values(extraClarifications).join('. ');
        combinedQuery = `${trimmed}. User preferences: ${extraText}`;
      }

      const stream = api.streamDeepRecommend(
        {
          query: combinedQuery,
          budget: currentBudget,
        },
        controller.signal
      );

      for await (const { event, data } of stream) {
        if (event === 'status') {
          setStatusMessage(data.message || 'Processing...');
        } else if (event === 'token') {
          setReasoningText((prev) => prev + (data.token || ''));
        } else if (event === 'questions') {
          if (Array.isArray(data.questions)) {
            setClarifications(data.questions);
          }
        } else if (event === 'recommendations') {
          if (Array.isArray(data.recommendations)) {
            setRecommendations(data.recommendations);
          }
        } else if (event === 'done') {
          setIsStreaming(false);
          setStatusMessage('Analysis complete.');
        }
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        console.warn('Stream notice:', err);
        setStatusMessage('Stream interrupted. Fallback completed.');
      }
      setIsStreaming(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSelectedClarifications({});
    startStream(query, budget);
  };

  const handleSelectPrompt = (promptText: string) => {
    setQuery(promptText);
    setSelectedClarifications({});
    startStream(promptText, budget);
  };

  const handleClarificationSelect = (questionId: string, option: string) => {
    const updated = { ...selectedClarifications, [questionId]: option };
    setSelectedClarifications(updated);
    // Instant re-stream with refined preferences
    startStream(query, budget, updated);
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <span className="label-caps">DEEP MODE &bull; REAL-TIME STREAMING COPILOT</span>
        <h1 className={styles.title}>CONVERSATIONAL HARDWARE ARCHITECT</h1>
        <p className="body-md">
          Ask in natural English. Watch our neural copilot analyze hardware constraints, query scientific benchmarks (DxOMark, Geekbench, VCX), and synthesize expert purchasing advice in real time.
        </p>
      </div>

      {/* Input Box */}
      <form onSubmit={handleSubmit} className={styles.inputCard}>
        <div className={styles.inputGroup}>
          <input
            type="text"
            className={styles.textInput}
            id="deep-text-input"
            aria-label="Describe what phone you are looking for"
            placeholder="e.g. Best camera phone under ₹45,000 for travel and portrait photography"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={isStreaming}
            maxLength={250}
          />
        </div>

        <div className={styles.chipsList}>
          <span className="label-caps" style={{ width: '100%', fontSize: 10 }}>QUICK PROMPTS:</span>
          {SAMPLE_PROMPTS.map((prompt) => (
            <button
              key={prompt}
              type="button"
              className={styles.chipBtn}
              onClick={() => handleSelectPrompt(prompt)}
              disabled={isStreaming}
            >
              &ldquo;{prompt}&rdquo;
            </button>
          ))}
        </div>

        <div className={styles.actionRow}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span className="label-caps" style={{ fontSize: 10 }}>MAX BUDGET:</span>
            <input
              type="number"
              min={10000}
              max={250000}
              step={5000}
              value={budget}
              onChange={(e) => setBudget(Number(e.target.value))}
              style={{
                background: 'var(--color-canvas)',
                border: '1px solid var(--color-hairline)',
                color: 'var(--color-ink)',
                padding: '4px 8px',
                fontFamily: 'var(--font-mono)',
                fontSize: 12,
                width: 100,
              }}
            />
          </div>

          <button
            type="submit"
            className="btn-primary"
            id="deep-submit-btn"
            disabled={!query.trim() || isStreaming}
            style={{ opacity: query.trim() && !isStreaming ? 1 : 0.5 }}
          >
            {isStreaming ? 'STREAMING REASONING...' : 'RUN DEEP ANALYSIS →'}
          </button>
        </div>
      </form>

      {/* Streaming Copilot Reasoning Box */}
      {(isStreaming || reasoningText) && (
        <section className={styles.streamingCard} aria-label="Streaming Neural Reasoning">
          <div className={styles.statusRow}>
            {isStreaming && <span className={styles.pulsingDot} />}
            <span>{statusMessage}</span>
          </div>

          {reasoningText && (
            <div className={styles.reasoningText}>
              {reasoningText}
              {isStreaming && <span className={styles.blinkingCursor} />}
            </div>
          )}

          {/* Interactive Clarification Questions */}
          {clarifications.length > 0 && (
            <div className={styles.clarificationSection}>
              <div className={styles.clarificationHeader}>
                <span>💡 REFINE YOUR REQUIREMENTS</span>
              </div>
              {clarifications.map((q) => (
                <div key={q.id} className={styles.questionCard}>
                  <span className={styles.questionTitle}>{q.question}</span>
                  <div className={styles.optionsRow}>
                    {q.options.map((opt) => {
                      const isSelected = selectedClarifications[q.id] === opt;
                      return (
                        <button
                          key={opt}
                          type="button"
                          className={`${styles.optionChip} ${isSelected ? styles.optionChipSelected : ''}`}
                          onClick={() => handleClarificationSelect(q.id, opt)}
                        >
                          {isSelected ? `✓ ${opt}` : opt}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {/* Ranked Recommendations List */}
      {recommendations.length > 0 && (
        <section className={styles.resultsSection} aria-label="Deep Mode Recommendations">
          <div className={styles.resultsHeader}>
            <span className="label-caps">TOP VERIFIED ARCHITECTURAL CHOICES ({recommendations.length})</span>
            <Link href="/" className={styles.homeBtn} id="deep-home-btn">
              <span>&larr;</span> HOME
            </Link>
          </div>

          {recommendations.map((item, idx) => {
            const phone = item.phone;
            const brand = phone.brand || 'Unknown';
            const name = cleanPhoneName(phone.fullName || phone.name || phone.model || '', brand);
            const isTopRank = idx === 0;

            return (
              <div key={phone.id || idx} className={styles.recCard}>
                <div className={styles.recTopRow}>
                  <div className={styles.phoneMeta}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <span className="label-caps">{brand}</span>
                      {item.ai_verified && <VerifiedBadge />}
                    </div>
                    <h2 className={styles.recName}>{brand} {name}</h2>
                    <span className={styles.recPrice}>
                      ₹{phone.price ? phone.price.toLocaleString('en-IN') : 'N/A'}
                    </span>
                  </div>

                  <div style={{ width: 180 }}>
                    <span className="label-caps" style={{ fontSize: 10, display: 'block', marginBottom: 4 }}>
                      {Math.round(item.score)}% COMPATIBILITY
                    </span>
                    <ScoreBar score={item.score} isTopRank={isTopRank} />
                  </div>
                </div>

                {/* Benchmark Badges */}
                {(phone.dxomark_camera_score || phone.geekbench_multi || phone.antutu_v10_score || phone.gsmarena_battery_hours || phone.vcx_camera_score) && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                    {phone.dxomark_camera_score && (
                      <BenchmarkBadge type="dxomark-camera" value={phone.dxomark_camera_score} />
                    )}
                    {phone.vcx_camera_score && (
                      <BenchmarkBadge type="vcx" value={phone.vcx_camera_score} />
                    )}
                    {phone.geekbench_multi && (
                      <BenchmarkBadge type="geekbench" value={phone.geekbench_multi} />
                    )}
                    {phone.antutu_v10_score && (
                      <BenchmarkBadge type="antutu" value={phone.antutu_v10_score} />
                    )}
                    {phone.gsmarena_battery_hours && (
                      <BenchmarkBadge type="battery" value={phone.gsmarena_battery_hours} />
                    )}
                  </div>
                )}

                {/* Match Reasons */}
                {item.match_reasons && item.match_reasons.length > 0 && (
                  <ul className={styles.recReasonsList}>
                    {item.match_reasons.map((r, rIdx) => (
                      <li key={rIdx} className={styles.recReasonItem}>
                        <span style={{ color: '#00F0FF', fontWeight: 'bold' }}>&bull;</span>
                        <span>{r}</span>
                      </li>
                    ))}
                  </ul>
                )}

                {/* Actions */}
                <div className={styles.recActionsRow}>
                  {phone.slug && (
                    <Link href={`/phone/${phone.slug}`} className="btn-primary" style={{ fontSize: 12, padding: '8px 16px' }}>
                      INSPECT FULL SPEC REPORT &rarr;
                    </Link>
                  )}
                  {phone.id && (
                    <Link href={`/compare?ids=${phone.id}`} className="btn-secondary" style={{ fontSize: 12, padding: '8px 16px' }}>
                      COMPARE MODEL
                    </Link>
                  )}
                </div>
              </div>
            );
          })}
        </section>
      )}
    </div>
  );
}
