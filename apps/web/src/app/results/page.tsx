'use client';

import { Suspense, useEffect, useState, useCallback } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { usePostHog } from 'posthog-js/react';
import { api } from '@/lib/api';
import type { RecommendationResponse, RecommendedPhone } from '@/lib/types';
import LoadingState from '@/components/ui/LoadingState';
import QuerySummary from '@/components/results/QuerySummary';
import ResultsAccordion from '@/components/results/ResultsAccordion';
import styles from './results.module.css';

function ResultsContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const posthog = usePostHog();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<RecommendationResponse | null>(null);

  const mode = searchParams.get('mode') || 'easy';
  const budget = searchParams.get('budget') || '35000';
  const persona = searchParams.get('persona');
  const query = searchParams.get('q');

  const w_perf = searchParams.get('w_perf');
  const w_cam = searchParams.get('w_cam');
  const w_bat = searchParams.get('w_bat');
  const w_disp = searchParams.get('w_disp');
  const w_val = searchParams.get('w_val');

  const fetchRecommendations = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const budgetNum = parseInt(budget, 10) || 35000;
      let res: RecommendationResponse;

      if (mode === 'medium') {
        res = await api.recommendMedium({
          budget: budgetNum,
          priorities: {
            performance: parseFloat(w_perf || '0.5'),
            camera: parseFloat(w_cam || '0.5'),
            battery: parseFloat(w_bat || '0.5'),
            display: parseFloat(w_disp || '0.5'),
            value: parseFloat(w_val || '0.5'),
          },
        });
      } else if (mode === 'deep') {
        const queryText = query || 'Best smartphone overall';
        res = await api.recommendDeep({
          query: queryText,
          budget: budgetNum,
        });
      } else {
        // Easy Mode (Default)
        const personaName = persona || 'Student';
        res = await api.recommendEasy({
          persona: personaName,
          budget: budgetNum,
        });
      }

      setData(res);

      if (posthog) {
        posthog.capture('results_loaded', {
          mode,
          budget: budgetNum,
          persona,
          result_count: res.recommendations?.length || 0,
        });
      }
    } catch (err: any) {
      console.error('Failed to load recommendations:', err);
      const isFetchFail = err?.message === 'Failed to fetch' || err?.name === 'TypeError';
      setError(
        isFetchFail
          ? 'Unable to connect to Phonos.ai intelligence backend. Please verify network connectivity or that the API service is active.'
          : err.message || 'Unable to connect to Phonos.ai intelligence server. Please ensure the backend is active.'
      );
    } finally {
      setLoading(false);
    }
  }, [mode, budget, persona, query, w_perf, w_cam, w_bat, w_disp, w_val, posthog]);

  useEffect(() => {
    fetchRecommendations();
  }, [fetchRecommendations]);

  if (loading) {
    return (
      <div className={styles.pageContainer}>
        <LoadingState />
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.pageContainer}>
        <div className={styles.errorScreen}>
          <span className="label-caps" style={{ color: 'var(--color-error)' }}>
            SYSTEM COMMUNICATIONS ERROR
          </span>
          <h2 className={styles.errorTitle}>ANALYSIS ENGINE TEMPORARILY UNAVAILABLE</h2>
          <p className="body-md" style={{ maxWidth: 500 }}>
            {error}
          </p>
          <div style={{ display: 'flex', gap: 'var(--space-base)', marginTop: 'var(--space-md)' }}>
            <button
              type="button"
              className="btn-primary"
              onClick={() => fetchRecommendations()}
            >
              RETRY ANALYSIS
            </button>
            <button
              type="button"
              className="btn-secondary"
              onClick={() => router.push('/')}
            >
              RETURN TO HOME
            </button>
          </div>
        </div>
      </div>
    );
  }

  const recommendations: RecommendedPhone[] = data?.recommendations || [];

  return (
    <div className={styles.pageContainer}>
      <QuerySummary
        mode={mode}
        budget={budget}
        persona={persona}
        query={query}
        personaDetected={data?.persona_detected}
        budgetUsed={data?.budget_used}
      />

      <div className={styles.resultsHeader}>
        <span className="label-caps">RANKED VERDICTS</span>
        <h1 className={styles.pageTitle}>TOP SMARTPHONE CANDIDATES</h1>
        <p className="body-md">
          Filtered for known hardware failures, verified for Indian market pricing, and scored against your priorities.
        </p>
      </div>

      {recommendations.length === 0 ? (
        <div className={styles.emptyScreen}>
          <h2 className={styles.emptyTitle}>NO EXACT HARDWARE MATCHES FOUND</h2>
          <p className="body-md" style={{ maxWidth: 520 }}>
            No smartphones currently in the verified Indian database meet 100% of these parameters within this price ceiling.
          </p>
          <div style={{ display: 'flex', gap: 'var(--space-base)', marginTop: 'var(--space-md)' }}>
            <button
              type="button"
              className="btn-primary"
              onClick={() => router.back()}
            >
              INCREASE BUDGET OR LOOSEN CRITERIA
            </button>
          </div>
        </div>
      ) : (
        <ResultsAccordion
          initialRecommendations={recommendations}
          persona={persona || undefined}
          budget={parseInt(budget, 10) || 35000}
          mode={mode}
        />
      )}
    </div>
  );
}

export default function ResultsPage() {
  return (
    <Suspense
      fallback={
        <div className={styles.pageContainer}>
          <LoadingState />
        </div>
      }
    >
      <ResultsContent />
    </Suspense>
  );
}
