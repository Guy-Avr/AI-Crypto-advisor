# Database Schema – AI Crypto Advisor

PostgreSQL structure for the AI Crypto Advisor application. Tables are created via SQLAlchemy `Base.metadata.create_all` (no Alembic in use).

---

## Tables

### 1. users

Stores registered users.

| Column            | Type         | Constraints / Notes                    |
|-------------------|--------------|----------------------------------------|
| id                | UUID         | Primary Key, default `gen_random_uuid()` |
| email             | VARCHAR(255) | Unique, Not Null                      |
| name              | VARCHAR(255) | Not Null                              |
| hashed_password   | VARCHAR(255) | Not Null (bcrypt hashed)               |
| created_at        | TIMESTAMP    | Default `now()`                        |
| last_login        | TIMESTAMP    | Nullable                              |

**Constraints:** `UNIQUE(email)`

---

### 2. preferences

Stores onboarding answers. One row per user.

| Column         | Type           | Constraints / Notes                          |
|----------------|----------------|----------------------------------------------|
| id             | UUID           | Primary Key                                  |
| user_id        | UUID           | Unique, FK → users(id), ON DELETE CASCADE     |
| assets         | JSONB          | Not Null (e.g. `["BTC", "ETH"]`)             |
| investor_type  | investor_enum  | Not Null                                     |
| content_types  | JSONB          | Not Null (e.g. `["news", "ai", "meme"]`)     |
| created_at     | TIMESTAMP      | Default `now()`                              |
| updated_at     | TIMESTAMP      | Default `now()`, updated on change           |

**Constraints:**  
- `UNIQUE(user_id)`  
- `FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE`

---

### 3. votes

Stores user feedback (up/down) per dashboard item. One vote per (user, section, item); can be updated or cancelled (row deleted).

| Column       | Type         | Constraints / Notes                    |
|--------------|--------------|----------------------------------------|
| id           | UUID         | Primary Key                            |
| user_id      | UUID         | FK → users(id), ON DELETE CASCADE      |
| section_type | VARCHAR(20)  | Not Null (news \| price \| ai \| meme) |
| item_id      | VARCHAR(255) | Not Null (external content id)         |
| vote_type    | VARCHAR(10)  | Not Null (up \| down)                   |
| created_at   | TIMESTAMP    | Default `now()`                        |

**Constraints:**  
- `FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE`  
- `UNIQUE(user_id, section_type, item_id)` — at most one vote per user per item per section; updates replace the row, cancel deletes it.

---

## ENUMs

### investor_enum

Used in `preferences.investor_type`:

- HODLer, DayTrader, SwingTrader, LongTermInvestor, NFTCollector, DeFiFarmer

### section_type (votes)

- news, price, ai, meme

### vote_type (votes)

- up, down

---

## Data integrity

- Emails unique; investor type via ENUM; JSONB for assets and content_types.
- Unique (user_id, section_type, item_id) on votes prevents duplicate votes; same request updates existing row.
- Cascade deletes when a user is removed.

## Design notes

- UUIDs for ids; ENUMs for fixed value sets; votes stored for future personalization.
