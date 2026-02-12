# API Contract

High-level list of backend endpoints for the AI Crypto Advisor.

---

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/signup` | Register with email, name, and password. |
| POST | `/auth/login` | Authenticate and get JWT. |
| GET | `/users/me` | Return current user (id, email, name, onboarding done). Used by frontend to show who’s logged in and whether to show onboarding. |
| POST | `/onboarding` | Save onboarding answers as user preferences (assets, investor type, content types). |
| GET | `/dashboard` | Return personalized dashboard content (news, prices, AI insight, meme) based on preferences. |
| POST | `/vote` | Store user feedback (up/down) for personalization engine. |
