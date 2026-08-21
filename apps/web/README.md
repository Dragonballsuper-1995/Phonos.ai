# 📱 Phonos.ai — Frontend Web Application

The modern, editorial Swiss Design user interface for **Phonos.ai**, built on **Next.js 16 (App Router)**, **React 19**, **TypeScript**, and pure **Vanilla CSS Modules**.

---

## 🎨 Design System & Aesthetic (`DESIGN.md`)

Phonos.ai uses a precision intelligence surface inspired by classic Swiss editorial typography and warm tactile materials:

* **Canvas:** `#F0EDE6` (Warm Off-White Paper Grain)
* **Surface:** `#F7F4EF` / Surface Elevated: `#FDFCFA`
* **Ink / Primary Text:** `#1A1916` (Deep Charcoal Ink)
* **Body Text:** `#3C3A35`
* **Muted:** `#7A7669`
* **Hairline Borders:** `#D8D3C8` (Subtle 1px boundaries, no heavy drop shadows)
* **Accent:** `#E8420A` (Charged Vermilion)
* **Verified Badge:** `#1A7A4A` (Indian Market Verified Green)
* **Typography:**
  * **Display / Hero Headings:** `Barlow Condensed` / `Cabinet Grotesk` (Tight tracking, heavy weight)
  * **Body / UI:** `DM Sans` / `Satoshi` (High legibility)
  * **Data / Code / Spec Matrices:** `JetBrains Mono`

---

## 🧭 Discovery Modes & Routes

| Route | Mode | Description |
| :--- | :--- | :--- |
| `/` | **Landing Page** | Editorial hero (*"STOP GUESSING. START KNOWING."*), discovery mode selectors, trust statistics, and live intelligence ticker |
| `/easy` | **Easy Mode** | 2-step setup wizard: Select lifestyle persona (Student, Gamer, Creator, Business, Photography, Clean OS) + set INR budget via slider |
| `/medium` | **Medium Mode** | 5D parametric slider deck: Granular weight sliders for Performance, Camera, Battery, Display, and Build |
| `/deep` | **Deep Mode** | Minimalist terminal-style natural language interface for freeform and conversational queries |
| `/results` | **Results Deck** | Ranked top recommendations, calibrated match score bars, India Verified badges, expandable spec matrices, and `<SimilarPhones />` clones |
| `/phone/[slug]` | **Phone Intelligence Report** | Comprehensive device dossier with 50+ deep hardware specs, 5D vector radar, and spec-clone comparisons |
| `/compare` | **Side-by-Side Compare** | Direct multi-device hardware differential matrix |

---

## 🧩 Key Components (`src/components/`)

* **`<LoadingState />`**: Progressive 5-stage recommendation pipeline visualizer (Shielding → Embedding → Gating → Ranking → Verifying).
* **`<SimilarPhones />`**: 5D cosine spec-clone recommendations matching hardware profiles across price tiers.
* **`<PhoneReport />` / `<ResultsAccordion />`**: High-density hardware dossier categorizing Processor, Display, Cameras, Battery, and Ingress Protection.
* **`<ScoreBar />`**: Calibrated match score bars with Vermilion highlights for top-ranked recommendations.
* **`<VerifiedBadge />`**: India retail validation badge with hoverable verification rationale.
* **`<BudgetSlider />`**: Real-time slider with Indian Rupee (₹ / INR) formatting and tier snapping.

---

## 🛡️ PostHog First-Party Reverse Proxy

To ensure telemetry integrity and prevent ad-blockers from dropping analytics, `next.config.ts` proxies PostHog requests directly through the application origin:

```typescript
// next.config.ts
async rewrites() {
  return [
    {
      source: "/ingest/static/:path*",
      destination: "https://eu-assets.i.posthog.com/static/:path*",
    },
    {
      source: "/ingest/:path*",
      destination: "https://eu.i.posthog.com/:path*",
    },
    {
      source: "/ingest/decide",
      destination: "https://eu.i.posthog.com/decide",
    },
  ];
}
```

---

## ⚙️ Environment Variables

Create `.env.local` in `apps/web/`:

```env
# Backend API Base URL (auto-sanitized, no trailing slashes)
NEXT_PUBLIC_API_URL=http://localhost:8000

# PostHog Telemetry (Optional for local dev)
NEXT_PUBLIC_POSTHOG_KEY=your_posthog_project_key
NEXT_PUBLIC_POSTHOG_HOST=http://localhost:3000/ingest
```

---

## 💻 Getting Started

```bash
# 1. Install dependencies
npm install

# 2. Run the Next.js development server
npm run dev

# 3. Build for production (Turbopack)
npm run build

# 4. Start production server
npm run start
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

---

## 📋 Next.js 16 & React 19 Architectural Rules

1. **Awaited Dynamic Route Params:** In Next.js 16, route parameters (`params` and `searchParams`) are asynchronous promises. Always use `await params` or wrap client components consuming `useSearchParams()` inside `<Suspense>` boundaries.
2. **API Base URL Sanitization:** `src/lib/api.ts` automatically strips trailing slashes from `NEXT_PUBLIC_API_URL` to prevent malformed endpoint routes.
3. **No UI Kit Bloat:** Pure Vanilla CSS Modules and CSS custom properties only.
