# TruthLens 🔍
### AI-Powered Fake Review Detector for E-Commerce

> We don't just detect fake reviews — we explain them.

---

## Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Frontend   | Next.js 14 · TypeScript · Framer Motion · Recharts |
| Backend    | FastAPI · Python 3.11               |
| Scraping   | Playwright · BeautifulSoup4         |
| Detection  | TF-IDF cosine similarity · NumPy anomaly detection |
| AI Verdict | **OpenRouter** (Mixtral 8x7B default) |
| Caching    | Redis                               |
| Deploy     | Vercel (frontend) · Render/Railway/Docker (backend) |

---

## Quick Start (Docker Compose)

```bash
# 1. Clone the repo
git clone https://github.com/you/truthlens.git
cd truthlens

# 2. Set up backend environment
cp backend/.env.example backend/.env
# → Edit backend/.env and add your API keys (see below)

# 3. Set up frontend environment
cp frontend/.env.local.example frontend/.env.local
# → NEXT_PUBLIC_API_URL=http://localhost:8000 (default is fine locally)

# 4. Launch everything
docker compose up --build
```

Frontend → http://localhost:3000  
Backend  → http://localhost:8000  
API Docs → http://localhost:8000/docs

---

## Manual Setup (No Docker)

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Copy and fill in .env
cp .env.example .env

# Run
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

npm install

# Copy and fill in .env.local
cp .env.local.example .env.local

npm run dev
```

---

## API Keys — Where to Get Them

### 1. OpenRouter (Required for AI Verdict)

1. Sign up at https://openrouter.ai
2. Go to **Keys** → **Create Key**
3. Copy the key (starts with `sk-or-`)
4. Add to `backend/.env`:
   ```
   OPENROUTER_API_KEY=sk-or-your-key-here
   OPENROUTER_MODEL=mistralai/mixtral-8x7b-instruct
   ```

**Free models you can use on OpenRouter:**
- `mistralai/mixtral-8x7b-instruct` (recommended)
- `meta-llama/llama-3-8b-instruct`
- `google/gemma-3-12b-it`
- `deepseek/deepseek-chat`

> **No OpenRouter key?** The app works without it —
> it falls back to a rule-based verdict automatically.

---

### 2. HuggingFace Token (Optional — for advanced NLP)

1. Sign up at https://huggingface.co
2. Go to **Settings → Access Tokens → New token**
3. Add to `backend/.env`:
   ```
   HF_TOKEN=hf_your-token-here
   ```

> The app uses a lightweight local keyword-based fallback
> if HF models are not loaded, so this is optional.

---

### 3. Redis (Optional — for caching)

**Local (default):** Redis runs automatically via Docker Compose.

**Cloud options:**
- [Redis Cloud](https://redis.com/try-free/) — free 30MB tier
- [Upstash](https://upstash.com/) — free serverless Redis

Add to `backend/.env`:
```
REDIS_URL=redis://your-host:port/0
```

> Without Redis the app works fine — caching is simply skipped.

---

## API Reference

### `POST /analyze`

Analyze a product page for fake reviews.

**Request:**
```json
{ "url": "https://www.amazon.com/dp/B0XXXXXXX" }
```

**Response:**
```json
{
  "success": true,
  "product_title": "Amazing Gadget Pro",
  "total_reviews_analyzed": 87,
  "trust_score": 42,
  "risk_level": "caution",
  "verdict": "Likely manipulated reviews detected",
  "flags": [
    {
      "title": "High review similarity (68%)",
      "detail": "...",
      "severity": "high"
    }
  ],
  "dna": {
    "similarity_percent": 68.0,
    "duplicate_count": 24,
    "cluster_count": 5,
    "pattern_notes": ["..."]
  },
  "charts": {
    "review_timeline": [{ "label": "2024-01", "value": 4 }],
    "rating_distribution": [{ "label": "5★", "value": 71 }],
    "sentiment_breakdown": [
      { "label": "Positive", "value": 82.0 },
      { "label": "Neutral",  "value": 10.0 },
      { "label": "Negative", "value": 8.0 }
    ]
  },
  "sentiment_summary": "...",
  "explanation": "Many reviews appear repetitive...",
  "cached": false
}
```

### `DELETE /analyze/cache?url=<url>`

Invalidate cached result for a given URL.

### `GET /health`

Returns `{ "status": "ok" }`.

Full Swagger docs at `/docs` when running locally.

---

## Deployment

### Frontend → Vercel

```bash
cd frontend
npx vercel --prod
# Set NEXT_PUBLIC_API_URL to your backend URL in Vercel dashboard
```

### Backend → Render

1. New Web Service → connect your GitHub repo → Root: `backend`
2. Build command: `pip install -r requirements.txt && playwright install chromium`
3. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables from `.env` in Render dashboard

### Backend → Railway

```bash
cd backend
railway up
# Set environment variables in Railway dashboard
```

---

## Project Structure

```
truthlens/
├── docker-compose.yml
├── backend/
│   ├── main.py                  ← FastAPI app factory
│   ├── config.py                ← Settings (pydantic-settings)
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example             ← Copy to .env and fill in keys
│   ├── models/
│   │   └── schemas.py           ← All Pydantic request/response models
│   ├── routers/
│   │   └── analyze.py           ← POST /analyze endpoint
│   ├── services/
│   │   ├── scraper.py           ← Playwright + BS4 scraper
│   │   ├── detector.py          ← TF-IDF, spike detection, patterns
│   │   ├── openrouter.py        ← OpenRouter AI verdict
│   │   └── cache.py             ← Redis caching
│   └── utils/
│       └── response_builder.py  ← Assembles final API response
└── frontend/
    ├── package.json
    ├── next.config.mjs
    ├── tailwind.config.ts
    ├── tsconfig.json
    ├── .env.local.example       ← Copy to .env.local
    └── src/
        ├── app/
        │   ├── layout.tsx
        │   ├── page.tsx         ← Main page
        │   ├── page.module.css
        │   └── globals.css      ← Dark theme + all shared styles
        ├── components/
        │   ├── SearchBar.tsx
        │   ├── ScanLoader.tsx
        │   ├── TrustScore.tsx
        │   ├── VerdictCard.tsx
        │   ├── RedFlags.tsx
        │   ├── ReviewDNA.tsx
        │   ├── Charts.tsx
        │   └── AIExplanation.tsx
        ├── hooks/
        │   └── useScan.ts       ← Scan state machine + step animation
        ├── services/
        │   └── api.ts           ← Axios wrapper for backend
        └── types/
            └── review.ts        ← All TypeScript types
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Playwright install fails | Run `playwright install-deps chromium` |
| No reviews found | Try the direct product page URL (not search) |
| OpenRouter 401 | Check your API key in `.env` |
| Redis connection refused | Start Redis or set `REDIS_URL=` (empty disables cache) |
| CORS errors | Add your frontend URL to `ALLOWED_ORIGINS` in `.env` |
| Scraping blocked | Enable proxy in `.env`: `USE_PROXY=true`, `PROXY_URL=...` |

---

Built for hackathon · Production-ready architecture
