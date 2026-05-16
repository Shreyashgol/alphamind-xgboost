# AlphaMind

**Knowledge-augmented stock forecasting with AutoML, RAG, explainable signals, and a conversational research assistant.**

AlphaMind is a full-stack financial forecasting platform that combines historical OHLCV stock data, machine-learning forecast models, local financial documents, and LLM-generated explanations. It is designed for users who want more than a chart: they want to understand *why* a forecast looks the way it does, what evidence supports it, and what questions to ask next.

> Forecast with data. Explain with context. Ask better follow-up questions.

---

## The Problem

Most stock forecasting tools stop at a number or a chart.

That leaves important questions unanswered:

- What model produced the forecast?
- Which historical signals influenced the prediction?
- What recent company or market context supports the forecast?
- How confident should a user be?
- What should the user ask next?

For students, analysts, and builders, this creates a gap between raw prediction and usable decision support.

---

## The Solution

AlphaMind bridges forecasting and research.

It uses:

- **AutoML-style model selection** across XGBoost, ARIMA, and LSTM.
- **Feature engineering** from price, volume, returns, rolling statistics, momentum, and volatility.
- **RAG retrieval** over local PDF/TXT financial documents using FAISS and sentence-transformers.
- **Groq LLM explanations** when `GROQ_API_KEY` is configured, with safe local fallbacks when it is not.
- **Conversational chat** that answers source-backed user queries and suggests better follow-up questions.
- **A modern React dashboard** with Plotly candlestick charts, confidence scoring, explanation cards, and a built-in user guide.

---

## What You Can Do

| Capability | What It Does |
| --- | --- |
| Forecast any ticker | Type any ticker symbol. Forecasting works when `backend/data/uploads/TICKER.csv` exists. |
| Compare models | Trains XGBoost, ARIMA, and LSTM candidates, then selects the lowest-RMSE model. |
| Inspect confidence | Combines model validation error and retrieved-context alignment. |
| Read explanations | Shows trend, model metrics, feature insights, confidence, and evidence. |
| Query documents | Ask questions against local financial reports and notes. |
| Get suggested questions | Chat responses include practical next questions to continue analysis. |
| Learn from the Guide page | A `/guide` page explains data setup, usage, and good questions. |

---

## Architecture

```text
AlphaMind
├── backend/                    FastAPI, ML, RAG, explanations
│   ├── core/
│   │   ├── automl_engine.py     Model training, scoring, confidence, forecasts
│   │   ├── preprocessing.py     OHLCV loading and feature engineering
│   │   ├── knowledge_augment.py Ticker-aware context retrieval
│   │   └── explanation_engine.py Groq-backed structured explanations
│   ├── models/
│   │   ├── xgboost_model.py
│   │   ├── arima_model.py
│   │   └── lstm_model.py
│   ├── rag/
│   │   ├── document_loader.py   PDF/TXT ingestion
│   │   ├── embedder.py          sentence-transformers embeddings
│   │   ├── vector_store.py      FAISS index and search
│   │   └── rag_pipeline.py      Retrieval, chat answers, suggestions
│   ├── routes/                  API endpoints
│   └── data/
│       ├── uploads/             Stock CSV files
│       └── knowledge/           PDF/TXT knowledge files
│
└── frontend/                    React + Vite + Plotly UI
    ├── src/pages/Dashboard.jsx
    ├── src/pages/Guide.jsx
    ├── src/components/QueryChat.jsx
    └── src/components/ForecastChart.jsx
```

---

## Data Requirements

### Stock CSV

Place stock files in:

```text
backend/data/uploads/
```

Use this naming pattern:

```text
NVDA.csv
AAPL.csv
MSFT.csv
```

Required columns:

```csv
Date,Open,High,Low,Close,Volume
2026-04-20,188.10,191.50,186.80,190.24,58200000
```

Column names are case-insensitive.

### Knowledge Files

Place local reports or notes in:

```text
backend/data/knowledge/
```

Supported formats:

- `.pdf`
- `.txt`

Helpful file names:

```text
NVDA_Q1_Report.pdf
AAPL_2026_Earnings.txt
TSLA_Risk_Notes.pdf
```

If the ticker appears in the file name, AlphaMind can filter context more accurately.

---

## Backend API

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/health` | GET | Health check |
| `/api/tickers` | GET | List known/uploaded tickers |
| `/api/train` | POST | Train and select the best model |
| `/api/forecast` | GET/POST | Generate forecast payload |
| `/api/explain` | GET/POST | Generate structured explanation |
| `/api/query` | POST | Ask the local knowledge base |

### Example: train

```bash
curl -X POST http://127.0.0.1:8000/api/train \
  -H "Content-Type: application/json" \
  -d '{"ticker":"AAPL"}'
```

### Example: forecast

```bash
curl "http://127.0.0.1:8000/api/forecast?ticker=AAPL&horizon=7"
```

### Example: chat query

```bash
curl -X POST http://127.0.0.1:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "NVDA",
    "question": "What risks could weaken the forecast?",
    "recency_days": 90
  }'
```

---

## Local Setup

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn main:app --reload
```

Backend runs on:

```text
http://127.0.0.1:8000
```

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend runs on:

```text
http://127.0.0.1:5173
```

### 3. Optional Groq Setup

Add your Groq key to `backend/.env`:

```bash
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

Without a key, AlphaMind still works with local fallback explanations and answers.

---

## Docker Compose

```bash
docker compose up --build
```

Services:

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://127.0.0.1:5173`

---

## How to Use the App

1. Open the dashboard.
2. Type a ticker symbol.
3. Choose a forecast horizon between 1 and 30 trading days.
4. Click **Refresh Pipeline**.
5. Review:
   - predicted price
   - trend
   - confidence
   - selected model
   - candlestick chart
   - explanation
   - retrieved evidence
6. Use the chat to ask follow-up questions.
7. Open **Guide** in the navbar if you need usage help.

Good chat prompts:

- What are the strongest upside drivers for NVDA?
- What risks could weaken the forecast?
- Which retrieved sources support this answer?
- How does the forecast align with the retrieved context?
- What files should I add to analyze this ticker better?

---

## Testing

Backend:

```bash
backend/.venv/bin/python -m pytest backend/tests
```

Frontend:

```bash
cd frontend
npm run build
```

---

## Free Deployment Guide

The recommended no-paid-instance setup is:

```text
Vercel Free
  React/Vite frontend

Hugging Face Spaces Free CPU
  FastAPI backend in Docker
  ML models, RAG, FAISS, sample CSVs, sample PDFs
```

Why this setup?

- Vercel is very good for free static React/Vite deployments.
- Hugging Face Spaces supports Docker apps and exposes port `7860` by default.
- AlphaMind needs more memory than many tiny free API hosts because it uses `torch`, `xgboost`, `sentence-transformers`, and `faiss-cpu`.

Free-tier limitation:

- Files written at runtime on a free Hugging Face Space can disappear when the Space restarts.
- The sample CSV/PDF files committed in this repository will work.
- For permanent user uploads later, add Hugging Face persistent storage or external storage.

### Deployment Files Included

| File | Purpose |
| --- | --- |
| `Dockerfile` | Builds and runs the FastAPI backend on Hugging Face Spaces. |
| `.dockerignore` | Keeps local envs, caches, Node modules, and build outputs out of the Docker image. |
| `frontend/vercel.json` | Makes React Router routes like `/guide` work after Vercel deployment. |
| `backend/.env.production.example` | Production backend environment template. |
| `frontend/.env.example` | Local and Vercel frontend environment template. |

### Step 1: Deploy Backend on Hugging Face Spaces

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces).
2. Click **Create new Space**.
3. Choose:
   - **Space name:** `alphamind-api`
   - **SDK:** Docker
   - **Hardware:** Free CPU
   - **Visibility:** Public or Private
4. Connect this GitHub repository or manually push the repository files to the Space.
5. Make sure the Space uses the root `Dockerfile`.

The backend Dockerfile exposes:

```text
7860
```

The container starts with:

```bash
uvicorn main:app --host 0.0.0.0 --port 7860
```

### Step 2: Add Hugging Face Space Variables

In the Space page:

1. Open **Settings**.
2. Add these environment variables:

```bash
APP_ENV=production
APP_NAME=AlphaMind
API_HOST=0.0.0.0
API_PORT=7860
GROQ_MODEL=llama-3.3-70b-versatile
CORS_ORIGINS=https://your-vercel-app.vercel.app
```

3. Add this as a secret:

```bash
GROQ_API_KEY=your_groq_key_here
```

You can leave `GROQ_API_KEY` empty while testing. The app will use local fallback answers.

### Step 3: Test Backend

After the Space finishes building, open:

```text
https://your-space-name.hf.space/health
```

Expected response:

```json
{"status":"ok"}
```

Then test:

```text
https://your-space-name.hf.space/api/tickers
```

### Step 4: Deploy Frontend on Vercel

1. Go to [Vercel](https://vercel.com).
2. Click **Add New Project**.
3. Import this GitHub repository.
4. Configure:

```text
Framework Preset: Vite
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

5. Add this Vercel environment variable:

```bash
VITE_API_URL=https://your-space-name.hf.space
```

6. Deploy.

### Step 5: Update Backend CORS

After Vercel gives you a frontend URL, copy it.

Example:

```text
https://alphamind-xgboost.vercel.app
```

Go back to Hugging Face Space settings and update:

```bash
CORS_ORIGINS=https://alphamind-xgboost.vercel.app
```

Restart the Space.

### Step 6: Final Smoke Test

Open the Vercel URL and test:

1. Dashboard loads.
2. `AAPL` pipeline runs.
3. Candlestick chart renders.
4. Explanation card appears.
5. Chat answers a question.
6. `/guide` route opens directly in the browser.

### Useful Production URLs

```text
Frontend:
https://your-vercel-app.vercel.app

Backend:
https://your-space-name.hf.space

Health:
https://your-space-name.hf.space/health

Tickers:
https://your-space-name.hf.space/api/tickers
```

### Official Docs

- [Hugging Face Docker Spaces](https://huggingface.co/docs/hub/en/spaces-sdks-docker)
- [Hugging Face Spaces configuration](https://huggingface.co/docs/hub/spaces-config-reference)
- [Vercel Vite deployment](https://vercel.com/docs/frameworks/frontend/vite)

## Render Free Backend Deployment

If you deploy the backend on Render free, use the native Python service configuration below. This repo includes a `render.yaml`, but the manual dashboard settings are listed here so you can fix an existing service.

### Why the Original Render Build Failed

Your log shows three issues:

1. Render selected **Python 3.14.3** because no version was pinned.
2. `torch>=2.0.0` on Python 3.14 pulled massive CUDA packages, making the build huge and slow.
3. The start command used `--port 7860`, but Render web services should bind to Render's `$PORT`.
4. The app built the FAISS/sentence-transformer index during FastAPI startup, so Render could not detect an open port quickly.

This repo now fixes those by:

- pinning Python with `backend/.python-version`
- slimming production dependencies in `backend/requirements.txt`
- moving optional heavy local dependencies to `backend/requirements-dev.txt`
- removing blocking RAG indexing from app startup
- adding `render.yaml`

### Correct Render Settings

Create or edit your Render Web Service:

```text
Runtime: Python 3
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

Environment variables:

```bash
PYTHON_VERSION=3.11.9
APP_ENV=production
API_HOST=0.0.0.0
CORS_ORIGINS=https://your-vercel-app.vercel.app
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=your_groq_key_here
```

Do **not** set:

```bash
API_PORT=7860
```

For Render, always let the start command use `$PORT`.

### After Redeploy

Test:

```text
https://your-render-service.onrender.com/health
```

Expected:

```json
{"status":"ok"}
```

Then test:

```text
https://your-render-service.onrender.com/api/tickers
```

### Render Free Limitations

Render free web services spin down after inactivity. First request after sleep can be slow. The filesystem is ephemeral, so uploaded/generated files should not be treated as permanent unless you move to a paid persistent disk or external storage.

---

## Troubleshooting

### `Ticker data not found`

Add a matching CSV:

```text
backend/data/uploads/TICKER.csv
```

Example:

```text
backend/data/uploads/NVDA.csv
```

### Chat has weak answers

Add better local knowledge files:

```text
backend/data/knowledge/NVDA_Q1_Report.pdf
backend/data/knowledge/NVDA_Risk_Notes.txt
```

### FAISS or embedding model fails

AlphaMind automatically falls back to lexical search when vector retrieval is unavailable.

### XGBoost/OpenMP errors on macOS

Install OpenMP:

```bash
brew install libomp
```

The project also pins XGBoost to single-threaded execution for more stable local runs.

### React shows API errors from `127.0.0.1:5173/api/...`

Set:

```bash
VITE_API_URL=http://127.0.0.1:8000
```

Then restart the frontend dev server.

### Vercel `/guide` route shows 404 on refresh

Make sure `frontend/vercel.json` exists and the Vercel project root directory is set to `frontend`.

### Hugging Face Space fails during Docker build

Common causes:

- Free CPU build is still installing large packages. Wait for the build logs.
- `torch` and `sentence-transformers` can take time to install.
- If the build runs out of resources, temporarily remove `torch` or reduce ML dependencies for demo-only deployment.

### Hugging Face backend works but frontend cannot call it

Check both sides:

```bash
# Vercel environment variable
VITE_API_URL=https://your-space-name.hf.space

# Hugging Face environment variable
CORS_ORIGINS=https://your-vercel-app.vercel.app
```

Then redeploy Vercel and restart the Hugging Face Space.

---

## Project Status

AlphaMind currently includes:

- real model training and selection
- local RAG retrieval
- Groq-backed explanations and chat when configured
- fallback explanations and lexical retrieval
- dynamic ticker input
- guide page
- backend tests
- production frontend build

Future improvements:

- live market data ingestion
- user upload flow for CSV/PDF files
- persisted trained models
- authentication
- async training jobs
- Docker production image
- chart-level annotation of retrieved events

---

## Disclaimer

AlphaMind is an educational and research assistant. It is not financial advice. Forecasts can be wrong, historical patterns may not repeat, and users should verify all outputs before making decisions.
