# Database Schema – AI Crypto Advisor

This document describes the PostgreSQL database structure for the AI Crypto Advisor application.

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

Stores onboarding answers and personalization. Each user has exactly one preferences row.

| Column         | Type           | Constraints / Notes                          |
|----------------|----------------|----------------------------------------------|
| id             | UUID           | Primary Key                                  |
| user_id        | UUID           | Unique, FK → users(id), ON DELETE CASCADE     |
| assets         | JSONB          | Not Null (e.g. `["BTC", "ETH"]`)             |
| investor_type  | investor_enum  | Not Null                                     |
| content_types  | JSONB          | Not Null (e.g. `["news", "ai", "memes"]`)    |

**Constraints:**  
- `UNIQUE(user_id)` (one-to-one with users)  
- `FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE`

---

### 3. votes

Stores user feedback (up/down) on dashboard content, for future personalization.

| Column       | Type         | Constraints / Notes                    |
|--------------|--------------|----------------------------------------|
| id           | UUID         | Primary Key                            |
| user_id      | UUID         | FK → users(id), ON DELETE CASCADE      |
| section_type | VARCHAR(20)  | Not Null (news / price / ai / meme)    |
| item_id      | VARCHAR(255) | Not Null (external content identifier) |
| vote_type    | VARCHAR(10)  | Not Null (up / down)                   |
| created_at   | TIMESTAMP    | Default `now()`                        |

**Constraints:**  
- `FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE`  
- `UNIQUE(user_id, section_type, item_id)` (no duplicate votes per user per item)

---

## ENUMs

### investor_enum

Allowed investor archetypes (used in `preferences.investor_type`):

- HODLer  
- DayTrader  
- SwingTrader  
- LongTermInvestor  
- NFTCollector  
- DeFiFarmer  

### section_type (votes)

Allowed values for `votes.section_type` (dashboard sections):

- news  
- price  
- ai  
- meme  

### vote_type (votes)

Allowed values for `votes.vote_type`:

- up  
- down  

---

## Data integrity

- Emails are unique so we don’t get duplicate accounts.
- Investor type is enforced in the DB via the ENUM.
- JSONB is used for multi-value fields (assets, content types) so we can query and filter later.
- The composite unique on votes prevents voting twice on the same item.
- Cascade deletes keep the data clean when a user is removed.

## Design notes

- UUIDs avoid predictable IDs.
- ENUM keeps investor types under control.
- JSONB gives flexibility for filtering and personalization.
- Stored votes can be used later to improve recommendations.
