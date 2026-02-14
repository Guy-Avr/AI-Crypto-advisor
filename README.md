# AI Crypto Advisor

Personalized crypto investor dashboard with onboarding, daily curated content, and feedback voting.

---

## Tech Stack

### Backend

| Choice | Purpose |
|--------|--------|
| **FastAPI** | Async API, automatic OpenAPI docs, type hints |
| **PostgreSQL** | Relational DB, JSONB for preferences, ENUMs |
| **SQLAlchemy** | ORM and DB access |
| **JWT** (python-jose) | Stateless auth for API |
| **Passlib** (bcrypt) | Password hashing |

Schema is created via `Base.metadata.create_all` (no Alembic migrations in this repo).

### Frontend

| Choice | Purpose |
|--------|--------|
| **React** (Vite) | UI, fast dev experience |
| **React Router** | Routes, auth guards, Login/Register/Onboarding/Dashboard |
| **Axios** | HTTP client for API calls |
| **Context API** | Auth and app state (no Redux for now) |

### External APIs & data

| Source | Use |
|--------|-----|
| **CoinGecko** | Coin prices (fallback: Binance API, no key) |
| **CryptoCompare** | Market news (fallback: `backend/data/static_news.json`) |
| **OpenRouter** | AI insight of the day (e.g. Gemma 3) |
| **Imgflip** | Meme image URLs; meme list in `backend/data/memes.json` by investor type |

### Deployment

| Where | What |
|-------|------|
| **Render** | Backend + PostgreSQL |
| **Vercel** | Frontend (static / serverless) |

---

## Repo structure

- `backend/` — FastAPI app, models, API, DB
- `backend/data/` — JSON: `static_news.json`, `memes.json`
- `frontend/` — React (Vite) app
- `docs/` — documentation (see below)

## Run locally

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL 14+**

### 1) Start PostgreSQL

- Install PostgreSQL (e.g. 15/16) and make sure the service is running.
- Create a database (and optionally a dedicated user).

Example using `psql`:

```bash
psql -U postgres
```

Then run:

```sql
CREATE DATABASE ai_crypto_advisor;
-- Optional:
-- CREATE USER ai_crypto_user WITH PASSWORD 'your_password';
-- GRANT ALL PRIVILEGES ON DATABASE ai_crypto_advisor TO ai_crypto_user;
```

Alternatively, you can do the same in **pgAdmin** (Create Database → `ai_crypto_advisor`).

### 2) Backend (FastAPI)

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `backend/.env` (copy from `backend/.env.example`) and set at least:

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST=localhost`
- `POSTGRES_PORT=5432`
- `POSTGRES_DB`
- `SECRET_KEY` (long random string for JWT)
- `OPENROUTER_API_KEY` (optional; otherwise AI insight may fall back to static text)

Run the API:

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: `http://localhost:8000/docs`

### 3) Frontend (Vite)

```bash
cd frontend
npm install
```

Create `frontend/.env` (copy from `frontend/.env.example`) and set:

- `VITE_API_BASE_URL=http://localhost:8000`

Run the UI:

```bash
npm run dev
```

Open: `http://localhost:5173`

## Documentation

- **[docs/database_schema.md](docs/database_schema.md)** — PostgreSQL schema: users, preferences, votes; ENUMs and constraints.
- **[docs/api_contract.md](docs/api_contract.md)** — API endpoints, request/response details, and data sources.
