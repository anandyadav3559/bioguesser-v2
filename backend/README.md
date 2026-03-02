# Backend — BioGuesser V2

Django 6 + Django REST Framework REST API and WebSocket server.

---

## 🛠️ Tech Stack

| Layer            | Technology                                 |
| ---------------- | ------------------------------------------ |
| Framework        | Django 6.0 + DRF 3.16                      |
| Auth             | JWT (SimpleJWT) + Redis session validation |
| Database         | PostgreSQL 14+                             |
| Cache / Pub-Sub  | Redis                                      |
| Real-time        | Django Channels (ASGI)                     |
| Spatial indexing | H3 Geo (Uber) — resolution 2               |
| Package runner   | `uv`                                       |

---

## ⚙️ Setup

```bash
cd backend
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# Configure environment
cp .env.example .env   # edit with your credentials

uv run manage.py migrate
uv run manage.py runserver
```

### Required `.env` variables

```ini
SECRET_KEY=change-me
DEBUG=True

DB_NAME=bio_geo_guesser
DB_USER=postgres
DB_PASSWORD=root
DB_HOST=localhost
DB_PORT=5432

REDIS_HOST=localhost
REDIS_PORT=6379

GOOGLE_CLIENT_ID=your-google-client-id
```

---

## 📂 App Structure

```
backend/
├── backend/          # settings.py, urls.py, wsgi.py, asgi.py
├── authentication/   # User model, JWT auth, Guest/Google login
├── animal/           # Animal + AnimalLocation models (managed=False)
├── game/             # Room, Player, Round, Guess, scoring engine
├── userprofile/      # UserProfile (stats per user)
└── multiplayer/      # Django Channels WebSocket consumers
```

---

## � App Dependency Graph

```mermaid
graph TD
    AUTH[authentication<br/><i>User model · JWT · sessions</i>]
    UPROF[userprofile<br/><i>UserProfile stats</i>]
    ANIMAL[animal<br/><i>Animal · AnimalLocation · Characteristics</i>]
    GAME[game<br/><i>Room · Round · Player · Guess · GameService</i>]
    MULTI[multiplayer<br/><i>WebSocket GameConsumer</i>]
    BIOEX[bioExplorer<br/><i>stub — exploration mode</i>]

    UPROF -->|OneToOne User| AUTH
    GAME -->|ForeignKey User| AUTH
    GAME -->|ForeignKey Animal| ANIMAL
    GAME -->|updates stats| UPROF
    MULTI -->|resolves User from JWT| AUTH
    BIOEX -.->|planned: reads| ANIMAL
```

---

## �🗄️ Database Schema

```mermaid
erDiagram
    users {
        UUID user_id PK
        VARCHAR username
        VARCHAR email
        VARCHAR auth_provider
        BOOLEAN is_guest
        TIMESTAMP last_active_at
    }
    user_profiles {
        UUID id PK
        UUID user_id FK
        INT games_played
        FLOAT total_score
        FLOAT high_score
    }
    animals {
        UUID id PK
        TEXT name
        TEXT scientific_name
        FLOAT max_probability
        FLOAT entropy
    }
    animal_locations {
        UUID id PK
        UUID animal_id FK
        TEXT h3_index
        FLOAT latitude
        FLOAT longitude
        INT count
    }
    rooms {
        UUID id PK
        VARCHAR room_code
        UUID host_id FK
        VARCHAR status
        INT max_rounds
    }
    players {
        UUID id PK
        UUID user_id FK
        UUID room_id FK
        FLOAT score
        BOOLEAN is_active
    }
    rounds {
        UUID id PK
        UUID room_id FK
        UUID animal_id FK
        INT round_number
        VARCHAR status
    }
    guesses {
        UUID id PK
        UUID player_id FK
        UUID round_id FK
        FLOAT latitude
        FLOAT longitude
        FLOAT score_awarded
    }

    users ||--o{ players : has
    users ||--o| user_profiles : has
    rooms ||--o{ players : contains
    rooms ||--o{ rounds : has
    rounds ||--o{ guesses : collects
    players ||--o{ guesses : submits
    animals ||--o{ rounds : used_in
    animals ||--o{ animal_locations : has
```

---

## 🔐 Authentication Flow

See [authentication/README.md](./authentication/README.md) for full endpoint documentation.

```mermaid
sequenceDiagram
    participant C as Client
    participant A as Auth API
    participant R as Redis
    participant DB as PostgreSQL

    C->>A: POST /auth/guest/ or /auth/google/
    A->>DB: Get or create User
    A->>R: SET session:{user_id} TTL=30d
    A-->>C: {access_token, refresh_token}

    Note over C,A: Subsequent requests
    C->>A: GET /... (Bearer access_token)
    A->>R: EXISTS session:{user_id}?
    alt Session valid
        A-->>C: 200 OK + data
    else Session expired / logged out
        A-->>C: 401 Unauthorized
    end
```

---

## 🎮 Game Flow

```mermaid
sequenceDiagram
    participant F as Frontend
    participant G as Game API
    participant DB as PostgreSQL

    F->>G: POST /game/create/ {time_per_round}
    G->>DB: Create Room + Player
    G-->>F: {room_code}

    loop Each Round
        F->>G: POST /game/start_round/ {room_code, animal_id}
        G->>DB: Create Round
        G-->>F: {round_number}

        F->>G: POST /game/guess/ {room_code, lat, lng}
        G->>DB: Create Guess → evaluate_round()
        Note over G: sqrt(p_guess/p_max) × 100<br/>max(prob_score, dist_score)
        G-->>F: {score_awarded, true_locations[{lat,lng,count}]}
    end
```

---

## 🔢 Scoring Formula

```
p_guess  = cell_count / total_sightings          # probability of guessed H3 cell
score_prob = sqrt(p_guess / p_max) × 100         # sqrt-dampened probability score

closest_dist = min haversine distance to any location
score_dist   = exp(−closest_dist / 1000) × 100   # exponential distance fallback

final_score = max(score_prob, score_dist)         # best of the two
final_score = clamp(final_score, 0.5, 100.0)     # floor 0.5 for real guesses
```

**Score table (examples)**

| Situation                                  | Score |
| ------------------------------------------ | ----- |
| Perfect hotspot cell                       | ~100  |
| Cell with 50% of peak density              | ~71   |
| Cell with 5% of peak density               | ~22   |
| 0 km from nearest sighting (distance path) | 100   |
| 500 km away                                | ~61   |
| 1000 km away                               | ~37   |
| Timed out (no guess)                       | 0     |

---

## 🧹 Automatic Guest Cleanup (pg_cron)

Stale guest users (inactive > 2 hours) and all their related data are purged by a scheduled PostgreSQL stored procedure. See [`delete_temp_users.sql`](./delete_temp_users.sql).

```mermaid
flowchart LR
    C[pg_cron every 30 min] --> P[cleanup_expired_guests]
    P --> D1[Delete rooms with only guests]
    D1 -->|CASCADE| D2[rounds + guesses + players]
    P --> D3[NULL host on surviving rooms]
    P --> D4[DELETE guest users]
    D4 -->|CASCADE| D5[user_profiles + players]
```
