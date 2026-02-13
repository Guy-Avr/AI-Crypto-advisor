# API Contract

High-level list of backend endpoints for the AI Crypto Advisor. Each dashboard section is loaded separately.

---

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/signup` | Register with email, name, and password. |
| POST | `/auth/login` | Authenticate and get JWT. |
| GET | `/users/me` | Return current user (id, email, name, onboarding done). Used by frontend to show who's logged in and whether to show onboarding. |
| POST | `/onboarding` | Save onboarding answers as user preferences (assets, investor type, content types). |
| GET | `/dashboard/prices` | Coin prices in USD for the user's chosen assets. Requires onboarding with at least one asset. |
| GET | `/dashboard/news` | Market news filtered by user assets. Requires "news" in content_types. |
| GET | `/dashboard/ai-insight` | AI insight of the day. Requires "ai" in content_types. |
| GET | `/dashboard/meme` | Fun crypto meme. Requires "meme" in content_types. |
| POST | `/vote` | Store user feedback (up/down) for personalization engine. |

**News:** Sourced from CryptoCompare (free API); on failure, fallback to `static_news.json`. Each news item includes: `title`, `url`, `source` (CryptoCompare), `published_at`, `coins` (list of related coin symbols, e.g. `["BTC","ETH"]`).
