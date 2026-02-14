# API Contract

Backend endpoints for the AI Crypto Advisor. Use **GET /dashboard** for all-in-one dashboard data, or the separate endpoints per section. All dashboard and vote endpoints require JWT unless noted.

---

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/signup` | Register with email, name, and password. |
| POST | `/auth/login` | Authenticate and get JWT. |
| GET | `/users/me` | Current user (id, email, name, onboarding done). Auth required. |
| POST | `/onboarding` | Save onboarding: assets, investor type, content types. Auth required. |
| GET | `/dashboard` | Aggregated dashboard: prices, news, ai_insight, meme in one response. Auth required. |
| GET | `/dashboard/prices` | Coin prices in USD for user assets. Empty + message if no assets. Auth required. |
| GET | `/dashboard/news` | Market news filtered by user assets. Auth required. |
| GET | `/dashboard/ai-insight` | AI insight of the day (tailored by investor_type, content_types). Auth required. |
| GET | `/dashboard/meme` | One crypto meme by investor_type. 503 if none. Auth required. |
| POST | `/vote` | Cast or update vote. Auth required. |
| DELETE | `/vote` | Cancel a vote. Auth required. |

---

## Request / response details

### POST /vote

**Body:**

```json
{
  "section_type": "news",
  "item_id": "abc-123",
  "vote_type": "up"
}
```

- `section_type`: `news` | `price` | `ai` | `meme`
- `item_id`: non-empty string, max 255 chars. Frontend conventions: **news** = article URL; **price** = `symbol|value` (e.g. `BTC|95000.5`); **ai** = first 255 chars of insight text; **meme** = image URL.
- `vote_type`: `up` | `down`

**Response:** `{ "status": "ok", "action": "created" | "updated" }`

### DELETE /vote

**Body:**

```json
{
  "section_type": "news",
  "item_id": "abc-123"
}
```

**Response:** `{ "status": "ok", "action": "cancelled" }` or 404 if no vote found.

---

## Data sources

- **News:** CryptoCompare (free API). Fallback: `backend/data/static_news.json`. Each item: `title`, `url`, `source`, `published_at`, `coins`.
- **Prices:** CoinGecko (free API). Fallback: Binance API (no API key); prices refreshed every 5 minutes, prefer XXXUSD then XXXUSDT.
- **AI insight:** OpenRouter (e.g. Gemma 3). Prompt uses `investor_type` and `content_types` from preferences.
- **Meme:** JSON from `backend/data/memes.json`, categories by `investor_type`; images from Imgflip.
