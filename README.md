# AI Crypto Advisor

Personalized crypto investor dashboard with onboarding, daily curated content, and feedback voting.

---

## Tech Stack

Technical choices for this project.

### Backend

| Choice | Purpose |
|--------|--------|
| **FastAPI** | Async API, automatic OpenAPI docs, type hints |
| **PostgreSQL** | Relational DB, JSONB for preferences, ENUMs |
| **SQLAlchemy** | ORM and DB access |
| **Alembic** | Migrations for schema changes |
| **JWT** (python-jose) | Stateless auth for API |
| **Passlib** (bcrypt) | Password hashing |

### Frontend

| Choice | Purpose |
|--------|--------|
| **React** (Vite) | UI, fast dev experience |
| **Axios** | HTTP client for API calls |
| **Context API** | Auth and app state (no Redux for now) |

### APIs

| Service | Use |
|---------|-----|
| **CoinGecko** | Coin data and prices |
| **CryptoCompare** | Market news (fallback: static_news.json) |
| **HuggingFace / OpenRouter** | AI insight of the day |

### Deployment

| Where | What |
|-------|------|
| **Render** | Backend + PostgreSQL |
| **Vercel** | Frontend (static / serverless) |

---

## Repo structure

- `backend/` ? FastAPI app, models, API, DB
- `frontend/` ? React (Vite) app
- `docs/` ? documentation (see below)

## Documentation

- **[docs/database_schema.md](docs/database_schema.md)** ? PostgreSQL schema: tables (users, preferences, votes), ENUMs, constraints, and design notes.
- **[docs/api_contract.md](docs/api_contract.md)** ? API endpoints and short descriptions.
