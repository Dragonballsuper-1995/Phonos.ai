<div align="center">

# PHONOS.AI
### Machine Learning-Powered Smartphone Recommender & Hardware Intelligence Engine

[![Next.js](https://img.shields.io/badge/Next.js-16.2_(Turbopack)-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-DLRM_Ranker-EB5424?style=for-the-badge&logo=xgboost&logoColor=white)](https://xgboost.readthedocs.io/)
[![SQLite](https://img.shields.io/badge/SQLite-Async_Pool-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org/)
[![PostHog](https://img.shields.io/badge/PostHog-RLHF_Telemetry-1D212A?style=for-the-badge&logo=posthog&logoColor=white)](https://posthog.com/)
[![Tests](https://img.shields.io/badge/Pytest-38%2F38_Passing-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

<br/>

> **Phonos.ai** is an end-to-end smartphone intelligence platform designed for the Indian consumer electronics market. It replaces deceptive marketing specifications with a mathematical **2-Stage Deep Learning & Ranking Model (DLRM)**, 5D hardware vector embeddings, and real-world Aspect-Based Sentiment Analysis (ABSA).

</div>

---

## Executive Overview & Problem Solved

### The Problem
The Indian smartphone market is one of the most volatile and confusing consumer electronics spaces globally. Buyers face significant challenges:
* **Deceptive Hardware Specifications:** Inflated metrics like "200 MP cameras" or "24 GB Extended RAM" frequently mask low-grade sensors, poor ISP pipeline tuning, or severe thermal throttling.
* **Rapid Release Cycles & Stale Catalogues:** Databases frequently contain unreleased global models or obsolete devices from 2021–2023 without active retail availability in India.
* **Fragmented Aspect Sentiment:** Synthesizing authentic real-world feedback requires hours of reading disparate tech forums and video transcripts.
* **Volatile Pricing (₹):** Dynamic discounts and platform-exclusive pricing across Amazon India, Flipkart, and Croma complicate value comparisons.

### The Solution
Phonos.ai addresses these challenges via an end-to-end data and ranking pipeline:
* **Stage 1 (Retrieval & Filtering):** Real-time persona vector alignment, 5D hardware spec cosine clustering, Knowledge Graph defect shielding, and strict Indian Official Catalogue verification.
* **Stage 2 (Ranking & Calibration):** XGBoost ranking model trained on canonical features, Pattern 2 Gated Aspect-Based Sentiment Analysis (ABSA), 25-point additive bonus capping, and anti-monopoly brand diversity enforcement.

---

## System Architecture

<div align="center">
  <img src="screenshots/system_architecture.png" alt="Phonos.ai System Architecture" width="850" />
</div>

<br/>

```
                                  [ User Query & Intent Inputs ]
                                (Persona / Budget / Priority Sliders)
                                                  │
                                                  ▼
                             [ Stage 1: Candidate Retrieval & Shielding ]
                     (Knowledge Graph Purging | India Catalogue | Budget Floor)
                                                  │
                         ┌────────────────────────┴────────────────────────┐
                         ▼                                                 ▼
        [ Semantic & Spec Embedding Branch ]             [ Aspect Sentiment Analysis Branch ]
         (all-MiniLM-L6-v2 + 5D HW Vector)                (Pattern 2 Gated ABSA + Aspect DB)
                         │                                                 │
                         ▼                                                 ▼
            [ 5D Hardware Spec Vectors ]                  [ Domain Utility Sentiment Gates ]
            (L2-Normalized 1,430 BLOBs)                    (Domain * [1.0 + 0.10 * ABSA])
                         │                                                 │
                         └────────────────────────┬────────────────────────┘
                                                  ▼
                                [ Feature Aligner & Canonical Matrix ]
                              (7-Feature XGBoost Schema Normalization)
                                                  │
                                                  ▼
                             [ Stage 2: 2-Stage DLRM Ranking Engine ]
                      (XGBoost ranker.xgb + 25-Pt Bonus Cap + Diversity Filter)
                                                  │
                         ┌────────────────────────┴────────────────────────┐
                         ▼                                                 ▼
          [ Top-5 Ranked Recommendations ]                  [ 5D Hardware Spec Clones ]
          (Calibrated Match Scores 50-99%)              (Similar Spec Clones & Dual Compare)
                         │                                                 │
                         └────────────────────────┬────────────────────────┘
                                                  ▼
                            [ Presentation & Closed-Loop RLHF Feedback ]
                         (Next.js Web UI <---> PostHog Telemetry & Retrainer)
```

---

## Core Features & Engineering Specifications

### 1. 2-Stage Machine Learning Recommendation Pipeline
* **Stage 1 — Vector Retrieval & Candidate Generation:**  
  Projects user intent into a 5-dimensional query vector matching the device specification vector space:
  $$\vec{q} = \left[ \omega_{\text{soc}}, \omega_{\text{camera}}, \omega_{\text{display}}, \omega_{\text{battery}}, \omega_{\text{build}} \right]$$
* **Stage 2 — XGBoost Ranking Model (`ranker.xgb`):**  
  Evaluates candidate devices across a 7-feature canonical schema:
  $$\mathbf{x} = \left[ \text{persona\_id}, \frac{\text{budget}}{\text{price}}, \frac{\text{price}}{\text{max\_price}}, \text{battery}_{\text{norm}}, \text{ram}_{\text{norm}}, \text{hz}_{\text{norm}}, \text{perf\_tier} \right]$$

### 2. Pattern 2 Gated ABSA (Aspect-Based Sentiment Analysis)
Rather than applying additive score bonuses that artificially inflate lower-tier hardware, Phonos.ai modulates hardware utility scores directly using real-world reviewer sentiment:
$$\text{DomainScore}_{\text{effective}} = \text{DomainScore}_{\text{raw}} \times \left(1.0 + 0.10 \times \text{ABSA\_Sentiment}\right)$$

```
Aspect Monitored   │ Sentiment Scale │ Modulation Range │ Contextual Output
───────────────────┼─────────────────┼──────────────────┼────────────────────────────────────────
Camera             │ [-1.0, +1.0]    │ ±10.0% Scaling   │ Reviewer Acclaim / Thermal Caution
Battery & Charging │ [-1.0, +1.0]    │ ±10.0% Scaling   │ Real-World Battery Endurance Notes
Performance / SoC  │ [-1.0, +1.0]    │ ±10.0% Scaling   │ Sustained Gaming Stability Warnings
Display & Panel    │ [-1.0, +1.0]    │ ±10.0% Scaling   │ Panel Calibration & Brightness Acclaim
Build & Materials  │ [-1.0, +1.0]    │ ±10.0% Scaling   │ Ergonomics & Durability Notes
```

### 3. 5D Hardware Vector Embeddings & Similar Spec Clones
* **Pre-Computed Database Embeddings:** 1,430 devices encoded as L2-normalized 5D float32 BLOBs directly in SQLite (`fone_master.db`).
* **Cosine Spec Similarity Engine:** Real-time $O(N)$ dot-product vector search in memory with sub-millisecond execution.
* **REST Endpoint:** `GET /api/v1/phones/{name}/similar?top_k=4&max_budget=...`
* **Similar Phones UI (`<SimilarPhones />`):** Displays match percentage badges (`98% MATCH`), brand labels, INR pricing, and direct dual-phone comparison navigation (`/compare?ids=A,B`).

### 4. Interactive Recommendation Modes

| Mode | Route | Target User | Input Mechanism |
|---|---|---|---|
| **Easy Mode** | `/easy` | General Buyers & Enthusiasts | Multi-step persona wizard (Student, Gamer, Creator, Business, Clean UI) + Budget slider |
| **Medium Mode** | `/medium` | Discerning Enthusiasts | Continuous 5D interactive sliders (Performance, Camera, Battery, Display, Build) |
| **Deep Mode** | `/deep` | Power Users | Granular constraint-based specification filtering |

### 5. Knowledge Graph & Safeguard Filters
* **Defect Purging:** Automatically excludes devices with documented hardware failure histories (e.g. motherboard failure models or severe thermal throttling chipsets).
* **Lifecycle Aging Penalty:** 2023/2024 flagships priced above ₹70,000 receive a -12.0 point lifecycle penalty to prevent older generation models from overshadowing modern sub-flagships.
* **Anti-Stacking 25-Point Bonus Cap:** Additive keyword boosts are strictly capped at 25.0 points, clamping final output scores to the $[50.0, 99.0]$ range.
* **Anti-Monopoly Brand Diversity:** Guarantees no single manufacturer occupies more than 2 slots in the top-5 recommendations.

### 6. Closed-Loop RLHF Telemetry & Retraining
* PostHog telemetry hooks capture user interactions (`buy_clicked`, `phone_rejected`, `phone_expanded`) along with full query context (`persona`, `budget`, `mode`).
* `retrain_from_rlhf.py` converts real user feedback into sample-weighted pairwise training instances to continually update the XGBoost ranker.

---

## Tech Stack

### Frontend Application (`apps/web`)
* **Core Framework:** Next.js 16 (App Router) + React 19 + TypeScript
* **Styling Architecture:** Custom CSS Modules with a Swiss Design aesthetic
* **Typography:** Cabinet Grotesk (Display Headings), Satoshi (Body Copy), JetBrains Mono (Technical Spec Matrices)
* **Telemetry & Analytics:** PostHog React SDK (`posthog-js`)

### Backend Application (`apps/api`)
* **Core Framework:** FastAPI (Python 3.11+) with asynchronous ASGI request processing
* **Machine Learning & Analytics:** XGBoost (`xgboost`), NumPy, Scikit-learn, VADER Sentiment (`nltk.sentiment.vader`)
* **Semantic Embeddings:** `sentence-transformers` (`all-MiniLM-L6-v2`)
* **Database & Persistence:** SQLite with `aiosqlite` asynchronous connection pooling
* **Knowledge Graph:** NetworkX (`networkx`)

---

## Repository Structure

```
Phonos.ai/
├── apps/
│   ├── api/
│   │   ├── app/
│   │   │   ├── db/                 # Connection pool and async SQL query layer
│   │   │   ├── models/             # Pydantic schemas (PhoneDetails, Query, Response)
│   │   │   ├── routers/            # API endpoints (recommend, phones, search, health)
│   │   │   └── services/           # ML ranker, hardware scorer, similarity, ABSA, KG
│   │   ├── data/                   # Production SQLite DB (fone_master.db) & ranker.xgb
│   │   ├── scripts/                # Data pipelines, ABSA scorer, RLHF retrainer, diagram generator
│   │   └── tests/                  # 38 granular Pytest unit, integration & edge-case tests
│   │
│   └── web/
│       ├── src/
│       │   ├── app/                # App Router (easy, medium, deep, results, phone/[slug], compare)
│       │   ├── components/         # UI modules (PhoneReport, SimilarPhones, PhoneRow, Accordion)
│       │   └── lib/                # API client, types, spec helpers
│       └── public/                 # Static assets & font definitions
│
├── screenshots/                    # High-resolution architectural and UI diagrams
├── data_engine/                    # GSMArena & YouTube sentiment scrapers
└── docker-compose.yml              # Monorepo containerization configuration
```

---

## Test Suite & Verification Results

The entire recommendation engine is covered by **38 automated unit, integration, and edge-case tests**:

```bash
cd apps/api
.venv\Scripts\pytest.exe -v tests/
```

```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.0

tests/test_recommendation_edge_cases.py (15 edge cases) ........... PASSED [ 39%]
tests/test_recommendation_engine.py (15 ML tests)      ........... PASSED [ 78%]
tests/test_official_catalogue_scraper.py (7 scraper tests) ....... PASSED [ 97%]
tests/test_health.py (1 health check)                  ........... PASSED [100%]

======================= 38 passed in 56.13s =======================
```

### Live Database Scenario Simulation
To test the engine against the live database across 10 real-world buyer profiles:

```bash
.venv\Scripts\python.exe scripts/test_engine_scenarios.py
```

```
====================================================================================================
PHONOS.AI RECOMMENDATION ENGINE — LIVE SCENARIO TEST SUITE
====================================================================================================
# SCENARIO                             │ STATUS │ TOP RECOMMENDATION               │ SCORE │ PRICE (INR)
───────────────────────────────────────┼────────┼──────────────────────────────────┼───────┼────────────
1. Ultra-Low Budget Student            │ PASS   │ Motorola Moto G 5G 2026          │ 98.4  │ Rs.    9,999
2. Mid-Range BGMI Competitive Gamer    │ PASS   │ realme Realme GT 7 Pro           │ 94.7  │ Rs.   34,999
3. 4K HDR Vlog & Reels Creator         │ PASS   │ Vivo Vivo X200 Pro Optics        │ 99.0  │ Rs.   54,999
4. Pure Clean Stock OS Purist          │ PASS   │ Motorola Edge 60 Pro             │ 92.0  │ Rs.   29,645
5. Ultra Flagship Executive            │ PASS   │ Samsung Galaxy S26 Ultra         │ 87.2  │ Rs.  124,999
6. Medium Mode 80% Battery Focus       │ PASS   │ Oppo Oppo A6 5G                  │ 99.0  │ Rs.   21,999
7. Medium Mode 80% Silicon Focus       │ PASS   │ realme Realme 16                 │ 99.0  │ Rs.   27,990
8. Hardware Spec Clones (S26 Ultra)    │ PASS   │ Samsung Galaxy F36 5G            │ 99.9  │ Rs.   21,999
9. Hardware Spec Clones (Budget 5G)    │ PASS   │ Motorola Moto G05                │ 99.6  │ Rs.    7,999
10. Tight Budget Squeeze Optimization  │ PASS   │ Oppo Oppo K13                    │ 84.0  │ Rs.   16,817
====================================================================================================
ALL 10 LIVE SCENARIOS VALIDATED SUCCESSFULLY WITHOUT ERRORS.
====================================================================================================
```

---

## Quick Start Guide

### Prerequisites
* **Node.js:** 20.x or higher
* **Python:** 3.11.x or higher
* **Git**

---

### 1. Backend Setup (FastAPI)

```bash
# Clone the repository
git clone https://github.com/Dragonballsuper-1995/Phonos.ai.git
cd Phonos.ai

# Setup virtual environment
cd apps/api
python -m venv .venv

# Activate virtual environment:
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On macOS / Linux:
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Launch FastAPI development server
uvicorn app.main:app --reload --port 8000
```
* Interactive API Documentation (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)
* Health Check Endpoint: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

### 2. Frontend Setup (Next.js)

In a separate terminal window:
```bash
cd apps/web

# Install npm dependencies
npm install

# Launch Next.js development server
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

### 3. Containerized Setup (Docker Compose)

```bash
docker compose up --build
```

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

