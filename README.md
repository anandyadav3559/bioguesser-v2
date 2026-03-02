# 🌍 BioGuesser V2

A full-stack probabilistic animal-habitat guessing game. Players are shown an animal and must pin its likely habitat on a world map. Scores are calculated based on real sighting-probability distributions sourced from iNaturalist.

---

## 🏗️ Architecture Overview

```mermaid
graph TD
    U[User / Browser] -->|HTTPS REST| B[Django Backend :8000]
    U -->|WebSocket wss://| WS[Django Channels]
    B -->|ORM| PG[(PostgreSQL)]
    B -->|Cache / Sessions| RD[(Redis)]
    WS -->|Channel Layer| RD
    EX[Extraction Pipeline] -->|psycopg| PG

    subgraph Frontend [React + Vite :5173]
        U
    end
    subgraph Backend [Django 6 + DRF]
        B
        WS
    end
```

---

## 🗺️ Module Dependency Map

```mermaid
graph LR
    subgraph Frontend ["Frontend (React + Vite)"]
        LP[LoginPage]
        HP[HomePage]
        GM[GameMenu]
        GP[GamePlay]
        ML[MapLibreMap]
        UP[UserProfile]
    end

    subgraph Backend ["Backend (Django)"]
        AUTH[authentication]
        GAME[game]
        ANIMAL[animal]
        UPROF[userprofile]
        MULTI[multiplayer]
    end

    subgraph Infra ["Infrastructure"]
        PG[(PostgreSQL)]
        RD[(Redis)]
    end

    EX[Extraction Pipeline]

    LP -->|POST /auth/guest, /google| AUTH
    HP -->|POST /game/create, /start_round| GAME
    GP -->|POST /game/guess| GAME
    GM -->|GET /animal/batch| ANIMAL
    UP -->|GET /auth/me| AUTH
    ML -.->|renders true_locations| GAME

    GAME --> ANIMAL
    GAME --> UPROF
    GAME --> PG
    AUTH --> PG
    AUTH --> RD
    UPROF --> PG
    ANIMAL --> PG
    MULTI --> RD

    EX -->|psycopg INSERT| PG
```

---

## 📦 Repository Structure

```
geoguesser-v2/
├── README.md                  ← You are here
├── backend/                   ← Django REST API
│   ├── authentication/        ← JWT auth, Guest & Google login
│   ├── game/                  ← Rooms, rounds, scoring engine
│   ├── animal/                ← Animal & location models
│   ├── userprofile/           ← Per-user stats
│   ├── multiplayer/           ← WebSocket consumers (Django Channels)
│   └── backend/               ← Django settings, urls, asgi/wsgi
├── frontend/frontend/         ← React + Vite SPA
│   └── src/
│       ├── pages/             ← HomePage, LoginPage
│       └── components/        ← GameMenu, GamePlay, AnimalCard, MapLibreMap, UserProfile
└── extraction/                ← iNaturalist data ingestion scripts
```

---

## ⚡ Quick Start

### Prerequisites

| Tool       | Version              |
| ---------- | -------------------- |
| Python     | 3.11+                |
| Node.js    | 18+                  |
| PostgreSQL | 14+                  |
| Redis      | 6+                   |
| uv         | latest (recommended) |

### 1. Databases

```bash
# Docker (quickest)
docker run --name postgres -e POSTGRES_PASSWORD=root -p 5432:5432 -d postgres
docker run --name redis -p 6379:6379 -d redis
```

### 2. Backend

```bash
cd backend
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
cp .env.example .env          # fill in DB / Redis / Google credentials
uv run manage.py migrate
uv run manage.py runserver
```

### 3. Frontend

```bash
cd frontend/frontend
npm install
# create .env with VITE_API_BASE_URL=http://localhost:8000/api
npm run dev
```

### 4. Data Ingestion _(optional — seed animals)_

```bash
cd extraction
uv pip install psycopg[binary] aiohttp python-dotenv h3
# add animal names to animals.txt, then:
uv run ingest_Data.py
```

---

## 🔗 Module Documentation

| Module           | README                                                                 |
| ---------------- | ---------------------------------------------------------------------- |
| Backend (core)   | [backend/README.md](./backend/README.md)                               |
| Authentication   | [backend/authentication/README.md](./backend/authentication/README.md) |
| Multiplayer (WS) | [backend/multiplayer/README.md](./backend/multiplayer/README.md)       |
| Frontend         | [frontend/frontend/README.md](./frontend/frontend/README.md)           |
| Data Extraction  | [extraction/README.md](./extraction/README.md)                         |
