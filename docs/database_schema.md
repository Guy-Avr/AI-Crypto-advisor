# Database Schema for Crypto App

This is the database structure for our project.

## Tables

### 1. Users
This table stores everyone who signs up.

- `id`: int (primary key, auto increment)
- `email`: varchar(255) - unique, for login
- `name`: varchar(255)
- `hashed_password`: varchar(255) - we will hash this with bcrypt
- `created_at`: datetime - when they joined

### 2. Preferences
Stores what the user likes.

- `id`: int (primary key)
- `user_id`: int (foreign key to Users table)
- `assets`: text - this will be a JSON string of coins they follow (like BTC, ETH)
- `investor_type`: varchar(50) - e.g. "safe" or "risky"
- `content_types`: text - JSON string for things like "news" or "memes"
- `created_at`: datetime

### 3. Votes
For when people upvote or downvote stuff.

- `id`: int (primary key)
- `user_id`: int (foreign key)
- `section_type`: varchar(50) - can be news, price, ai, or meme
- `item_id`: varchar(100) - the ID of the post or coin
- `vote_type`: varchar(10) - "up" or "down"
- `created_at`: datetime

---
**Notes:**
- I used `int` for IDs because it's easier to manage for now.
- `assets` and `content_types` are `text` fields where we will just store JSON strings from the frontend.
- Let me know if we need more tables or if these types are okay!
