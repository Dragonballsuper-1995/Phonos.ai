---
title: Phonos AI API
emoji: 📱
colorFrom: purple
colorTo: blue
sdk: docker
pinned: true
app_port: 7860
---

# 📱 Phonos.ai — Backend API & Machine Learning Engine

FastAPI asynchronous backend and SOTA machine learning engine powering **Phonos.ai** — the smartphone intelligence and recommendation platform for the Indian consumer market (INR / ₹).

---

## 🚀 Key Features

* **2-Stage DLRM ML Ranker**: XGBoost classifier (`ranker.xgb`) evaluating 7 canonical features with persona click/buy probability modeling.
* **5D Hardware Vector Embeddings**: $L_2$-normalized vector representations across $[ \text{SoC}, \text{Camera}, \text{Display}, \text{Battery}, \text{Build} ]$ with sub-millisecond cosine spec-clone matching.
* **Pattern 2 Gated ABSA**: Aspect-Based Sentiment Analysis from verified Indian tech reviews modulating hardware domain scores by $\pm 10\%$.
* **Knowledge Graph Defect Purging**: NetworkX directed graph filtering out known hardware failure nodes (e.g., thermal-throttling SoCs, motherboard detachment issues).
* **Multi-LLM Fallback Verifier**: Multi-pass verification chain (Nvidia NIM Llama 3.3 70B → Google Gemini 2.5 Flash → Groq GPT OSS 120B) confirming active Indian retail availability and generating expert persona pitches.
* **Official Indian Smartphone Catalogue**: 1,430+ verified devices (`fone_master.db`) with FTS5 token-prefix full-text search.

---

## 📡 API Endpoints

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Root status, API version, and route index |
| `GET` | `/health` | Health check & SQLite database connection status |
| `GET` | `/api/v1/phones` | List all phones with pagination (`limit`, `offset`) and `brand` filter |
| `GET` | `/api/v1/phones/search?q=` | Search phones by name/brand via SQLite FTS5 with live scraper fallback |
| `GET` | `/api/v1/phones/{name}` | Get detailed hardware specs for a phone by slug or model name |
| `GET` | `/api/v1/phones/{name}/similar` | 5D cosine spec clones and similar devices across price bands |
| `POST` | `/api/v1/recommend/easy` | Easy mode: Persona selection + budget slider recommendation |
| `POST` | `/api/v1/recommend/medium` | Medium mode: 5D parametric priority weights recommendation |
| `POST` | `/api/v1/recommend/deep` | Deep mode: Freeform natural language query with semantic vector search |
| `GET` | `/api/v1/compare?ids=1,2` | Side-by-side spec differential comparison matrix |

---

## 🛠️ Technology Stack

* **Framework:** FastAPI (Python 3.11 / 3.14) with async ASGI request handling
* **Database:** Embedded SQLite with `aiosqlite` pool and FTS5 full-text search
* **Machine Learning:** XGBoost (`xgboost`), Scikit-learn, NumPy
* **Vector Search:** ChromaDB with `sentence-transformers/all-MiniLM-L6-v2`
* **Sentiment Analysis:** VADER Sentiment (`nltk`)
* **Knowledge Graph:** NetworkX (`networkx`)
* **LLM Providers:** Nvidia NIM, Google GenAI SDK (`google-genai`), Groq SDK (`groq`)
* **Telemetry:** PostHog Python SDK (`posthog`)

---

## ⚙️ Environment Configuration

Create a `.env` file in `apps/api/`:

```env
# Server
ENVIRONMENT=development
PROJECT_NAME="Phonos.ai API"
API_V1_STR=/api/v1
BACKEND_CORS_ORIGINS=["http://localhost:3000","https://phonos-ai.vercel.app"]

# Database Paths
DATABASE_URL=sqlite+aiosqlite:///data/fone_master.db

# AI Provider Keys
NVIDIA_NIM_API_KEY=your_nvidia_nim_key_here
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# Telemetry
POSTHOG_API_KEY=your_posthog_key_here
POSTHOG_HOST=https://eu.i.posthog.com
```

---

## 💻 Local Development

```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch FastAPI development server
uvicorn app.main:app --reload --port 8000
```

* **Interactive Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc UI:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Testing & Validation

```bash
# Run the 38-test automated Pytest suite:
pytest -v tests/

# Run the 10 live Indian market scenario tests:
python scripts/test_engine_scenarios.py
```

---

## 📂 Key Data Files (`apps/api/data/`)

* `fone_master.db`: SQLite database with 1,430+ curated Indian market smartphones.
* `ranker.xgb`: Serialized XGBoost recommendation model.
* `verifier_cache.db`: SQLite cache storing LLM market verification results.
* `pricing_cache.db`: SQLite cache storing live retail prices.
* `chroma_db/`: Persistent ChromaDB dense vector store for semantic retrieval.
