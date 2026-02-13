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
| **Axios** | HTTP client for API calls |
| **Context API** | Auth and app state (no Redux for now) |

### External APIs & data

| Source | Use |
|--------|-----|
| **CoinGecko** | Coin prices |
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

## Documentation

- **[docs/database_schema.md](docs/database_schema.md)** — PostgreSQL schema: users, preferences, votes; ENUMs and constraints.
- **[docs/api_contract.md](docs/api_contract.md)** — API endpoints, request/response details, and data sources.
