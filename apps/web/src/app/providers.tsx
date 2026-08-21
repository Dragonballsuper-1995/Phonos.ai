'use client'

import posthog from 'posthog-js'
import { PostHogProvider } from 'posthog-js/react'
import { useEffect } from 'react'

export function CSPostHogProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const key = process.env.NEXT_PUBLIC_POSTHOG_KEY;

      if (key && key.trim() !== '' && key !== 'undefined') {
        try {
          posthog.init(key, {
            api_host: '/ingest',
            ui_host: 'https://eu.posthog.com',
            person_profiles: 'identified_only',
            capture_pageview: false,
            autocapture: false,
            disable_session_recording: true,
            disable_surveys: true,
            advanced_disable_decide: true,
            disable_scroll_properties: true,
            opt_out_capturing_by_default: false,
            loaded: (ph) => {
              // Graceful load
            },
            on_xhr_error: () => {
              // Silently handle adblocker network interception
            },
          });
        } catch {
          // Silently ignore if client-side privacy extensions block initialization
        }
      }
    }
  }, []);

  return <PostHogProvider client={posthog}>{children}</PostHogProvider>;
}
