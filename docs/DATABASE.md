# Database Documentation

The project uses **PostgreSQL** for persistent storage and **Redis** for caching and session management.

## PostgreSQL Schema

### 1. `users` Table
Stores user accounts (Guest and Permanent).

| Column | Type | Description |
| :--- | :--- | :--- |
| `user_id` | UUID (PK) | Auto-generated via `gen_random_uuid()` |
| `username` | VARCHAR(100) | Unique username (guest_... / user_... / email) |
| `email` | VARCHAR(255) | Unique email (Nullable for guests) |
| `auth_provider` | VARCHAR(50) | 'guest', 'google', 'manual' |
| `is_permanent` | BOOLEAN | Legacy flag (use `is_guest` in Django) |
| `created_at` | TIMESTAMP | Creation time |

### 2. `animals` Table
Stores animal facts and metadata for the game.

| Column | Type | Description |
| :--- | :--- | :--- |
| `animal_id` | UUID (PK) | Unique ID |
| `name` | TEXT | Common name (Unique, Indexed) |
| `scientific_name` | TEXT | Scientific name (Unique) |
| `image_url` | TEXT | URL to animal image |
| `locations` | JSONB | Geographic locations |
| `fact` | TEXT | Fun fact about the animal |
| `created_at` | TIMESTAMP | Creation time |

### 3. `matches` Table
Stores game history between players.

| Column | Type | Description |
| :--- | :--- | :--- |
| `match_id` | SERIAL (PK) | Auto-increment ID |
| `player_id` | UUID (FK) | Reference to `users` |
| `opponent_id` | UUID (FK) | Reference to `users` |
| `animal_id` | UUID (FK) | Reference to `animals` |
| `player_score` | INTEGER | Score |
| `opponent_score` | INTEGER | Score |
| `created_at` | TIMESTAMP | Match time |

### 4. `match_state` Table
Tracks ongoing match status.

| Column | Type | Description |
| :--- | :--- | :--- |
| `match_id` | INT (PK, FK) | Reference to `matches` |
| `current_round` | INTEGER | Current round number |
| `is_active` | BOOLEAN | Is the match live? |
| `updated_at` | TIMESTAMP | Last update |

## Redis Usage

Redis is used primarily for **Session Management**.

-   **Key Pattern**: `session:<user_uuid>`
-   **Value**: `{"active": True}` (JSON)
-   **TTL**: 30 Days (2,592,000 seconds)
