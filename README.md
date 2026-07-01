# TruthLens 🔍 

### **AI-Powered Fake Review Detector for E-Commerce**
> *We don't just flag suspicious reviews — we analyze their DNA and explain why they shouldn't be trusted.*

---

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js 14](https://img.shields.io/badge/Next.js%2014-000000?style=for-the-badge&logo=nextdotjs)](https://nextjs.org/)
[![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge&logo=playwright)](https://playwright.dev/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker)](https://www.docker.com/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-7C3AED?style=for-the-badge)](https://openrouter.ai/)

TruthLens is a full-stack, production-ready AI application designed for e-commerce shoppers in India. It scrapes product reviews, performs analytical anomaly detection using statistical models, and aggregates findings with an LLM-powered verdict to explain review manipulation patterns in plain, understandable language.

---

## 🚀 Production Optimizations (Recent Fixes)

To ensure high availability and flawless deployments on **Render (Free Tier)** and **Vercel**, we implemented the following production optimizations:

* **⚡ Lightweight Docker Footprint**: Stripped heavy, unused libraries (e.g., PyTorch, Celery, Pandas) from the backend. This reduced the Docker container size from **~2.5GB to ~200MB**, allowing successful builds on Render's free tier without hitting the 10-minute timeout or the 512MB RAM Out-Of-Memory (OOM) threshold.
* **🛡️ CORS Preflight Alignment**: Standardized all frontend endpoints (specifically `POST /analyze/`) to include a trailing slash. This directly matches FastAPI's route registration pattern and prevents the browser's CORS preflight request (`OPTIONS`) from failing with a `405 Method Not Allowed` redirect error.
* **🔄 Auto-Warm-Up Routine**: Configured a proactive warm-up request to the `/health` endpoint upon page load to automatically wake up the sleeping Render backend instance before a user runs a scan, avoiding frontend query timeouts.

---

## ✨ Key Features

1. **📊 Advanced Review DNA Analysis**: Extracts textual features, clusters reviews, and detects similarity using TF-IDF and cosine similarity to spot duplicate, templated, or bot-generated reviews.
2. **📈 Anomaly & Spike Detection**: Maps review frequency over a timeline to find unnatural spikes (typical of coordinated review bombing or fake review campaigns).
3. **🎭 Sentiment Mismatch Engine**: Flags cases where reviews have 5-star ratings but express highly negative sentiments (or vice versa), pointing to automated bot errors.
4. **🤖 LLM-Powered Verdicts**: Integrates with OpenRouter (using Llama-3/Mixtral models) to construct human-readable trust summaries, listing exact red flags and explanation.
5. **⚡ Smart Caching**: Integrated with Upstash Redis to cache scan results for 6 hours per URL, minimizing scraper runs and API costs.
6. **📱 Clean Responsive UI**: Built with Next.js, Framer Motion, and Recharts, offering smooth glassmorphic animations and dark-mode charts.

---

## 🛠️ Tech Stack & Architecture

```mermaid
graph TD
    A[Next.js 14 Frontend] -->|POST /analyze/| B[FastAPI Gateway]
    B -->|Check Cache| C[(Upstash Redis Cache)]
    B -->|Fallback/No Cache| D[Playwright Scraper]
    D -->|Scrapes Reviews| E[Indian Fashion Sites]
    B -->|Review DNA Engine| F[TF-IDF & Cosine Similarity]
    B -->|AI Analysis| G[OpenRouter API]
    G -->|Llama 3 / Mixtral Verdict| B
    B -->|Return Trust Report| A
```

| Layer | Technologies Used |
| :--- | :--- |
| **Frontend** | Next.js 14 (App Router), TypeScript, TailwindCSS, Framer Motion, Recharts, Axios |
| **Backend** | FastAPI, Pydantic, SlowAPI (Rate Limiting), Loguru |
| **Scraping** | Playwright (Headless Chromium), BeautifulSoup4, Lxml |
| **Analysis** | Scikit-Learn (TF-IDF & Cosine Similarity), NumPy |
| **AI Engine** | OpenRouter API (Fallback to rule-based verdicts if offline) |
| **Cache & DB**| Redis (Upstash) |

---

## 🎯 Supported Platforms
TruthLens is optimized to run scans on major **Indian fashion, lifestyle, and beauty e-commerce sites**:
* 🛍️ **Myntra**
* 🛍️ **Ajio**
* 🛍️ **Nykaa Fashion**
* 🛍️ **The Souled Store**
* 🛍️ **Snitch**
* 🛍️ **Bewakoof**
* 🛍️ **Bonkers Corner**
* 🛍️ **Tata CLiQ Fashion**

---

## ⚙️ Quick Start (Docker Compose)

The easiest way to run the entire stack locally is using Docker Compose:

```bash
# 1. Clone the repository
git clone https://github.com/KAMESH101/Truthlens.git
cd Truthlens

# 2. Configure Backend Env variables
cp backend/.env.example backend/.env
# Open backend/.env and add your OpenRouter API key and Redis URL (if caching is desired)

# 3. Configure Frontend Env variables
cp frontend/.env.local.example frontend/.env.local
# (Defaults to http://localhost:8000 which works out of the box)

# 4. Build and run containers
docker compose up --build
```

* **Frontend:** [http://localhost:3000](http://localhost:3000)
* **Backend API:** [http://localhost:8000](http://localhost:8000)
* **Interactive OpenAPI Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔧 Manual Setup (Without Docker)

### 🐍 Backend setup
```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env           # Configure API keys here
uvicorn main:app --reload --port 8000
```

### ⚡ Frontend setup
```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

---

## 🔑 Environment Variables Reference

### Backend (`/backend/.env`)
| Variable | Description | Example |
| :--- | :--- | :--- |
| `OPENROUTER_API_KEY` | API key from [OpenRouter](https://openrouter.ai) | `sk-or-v1-xxxx...` |
| `OPENROUTER_MODEL` | The LLM model identifier | `meta-llama/llama-3-8b-instruct` |
| `REDIS_URL` | Redis URL for caching (optional) | `rediss://default:pass@host:port` |
| `SCRAPER_API_KEY` | Proxy/ScraperAPI key (optional) | `dfd81567cdfd4...` |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma separated) | `http://localhost:3000,https://...` |

### Frontend (`/frontend/.env.local`)
| Variable | Description | Example |
| :--- | :--- | :--- |
| `NEXT_PUBLIC_API_URL`| The root URL of the running backend API | `https://truthlens-backend-tw72.onrender.com` |

---

## 📈 API Reference

### `POST /analyze/`
Submits a product page URL for scraping, text matching, and AI review analysis.

* **Request Body:**
  ```json
  {
    "url": "https://www.myntra.com/tshirts/roadster/roadster-men-black-cotton-pure-tshirt/23784766/buy"
  }
  ```

* **Response Preview:**
  ```json
  {
    "success": true,
    "product_title": "Roadster Men Black Cotton Pure T-Shirt",
    "total_reviews_analyzed": 50,
    "trust_score": 85,
    "risk_level": "safe",
    "verdict": "Reviews appear organic and genuine",
    "flags": [],
    "dna": {
      "similarity_percent": 12.4,
      "duplicate_count": 0,
      "cluster_count": 1,
      "pattern_notes": ["Low similarity across reviews."]
    },
    "charts": {
      "review_timeline": [],
      "rating_distribution": [],
      "sentiment_breakdown": []
    },
    "sentiment_summary": "Highly positive product feedback.",
    "explanation": "No patterns of coordination or duplicate texts were found.",
    "cached": false,
    "demo_mode": false
  }
  ```

### `DELETE /analyze/cache`
Invalidates the Redis cache for a specific product URL.
* **Query Parameter:** `url=<encoded-product-url>`

### `GET /health`
Verifies backend service availability.
* **Response:** `{"status": "ok"}`

---

## 📁 Project Structure

```
truthlens/
├── backend/
│   ├── main.py                  ← FastAPI entry point and middleware config
│   ├── config.py                ← Application settings (Pydantic Settings)
│   ├── requirements.txt         ← Clean, optimized Python dependencies
│   ├── Dockerfile               ← Multi-stage system dependencies + Playwright config
│   ├── routers/
│   │   └── analyze.py           ← Analyze POST, Cache DELETE, Health endpoints
│   ├── services/
│   │   ├── scraper.py           ← Scrapers for supported e-commerce domains
│   │   ├── detector.py          ← Analytical engines (TF-IDF, Cosine Sim, Anomaly)
│   │   ├── openrouter.py        ← LLM structured verdict calls
│   │   └── cache.py             ← Redis connection & cache management
│   └── utils/
│       └── response_builder.py  ← Final schema builder
└── frontend/
    ├── package.json
    ├── next.config.mjs
    └── src/
        ├── app/                 ← Next.js page routers & layouts
        ├── components/          ← Interactive UI components (Charts, RedFlags, score dial)
        ├── hooks/               ← custom useScan scanner state machine Hook
        ├── services/            ← Axios client wrapper
        └── types/               ← TypeScript schemas matching backend models
```

---

## 🛡️ Troubleshooting

| Issue | Cause | Resolution |
| :--- | :--- | :--- |
| **CORS Blocked error** | Trailing slash missing on API calls or mismatch in `ALLOWED_ORIGINS` | Ensure frontend points to `/analyze/` (with trailing slash) and `ALLOWED_ORIGINS` in `.env` is configured. |
| **Playwright installation fails** | Missing system browser libraries | Run `playwright install-deps chromium` (or use Docker). |
| **No Reviews Found** | Page layout changed or incorrect URL path | Ensure you paste the direct product page link rather than search results. |
| **Render Timeout on Wakeup** | Server sleeping due to Free Tier inactivity | Wait 50-60 seconds for the first scan, or refresh the page to let the auto-warmup finish. |

---
*Created for the Itzfizz Internship Project Showcase.*
