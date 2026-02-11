# Bio-Geoguesser V2

A full-stack web application designed for interactive geography guessing games.

## Project Structure

-   **`backend/`**: Django REST Framework API.
-   **`frontend/frontend/`**: React + Vite frontend application.
-   **`database/`**: PostgreSQL schema definitions.
-   **`extraction/`**: Data ingestion and processing scripts.
-   **`authentication/`**: (Inside backend) Handles Guest and Google OAuth login + Redis sessions.

## Quick Start

### Prerequisites
-   Python 3.13+
-   Node.js 18+
-   PostgreSQL
-   Redis

### 1. Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Set up .env variables (DB, REDIS, SECRET_KEY, GOOGLE_CLIENT_ID)
python manage.py migrate
python manage.py runserver
```

### 2. Frontend Setup

```bash
cd frontend/frontend
npm install
# Set up .env variables (VITE_API_BASE_URL, VITE_GOOGLE_CLIENT_ID)
npm run dev
```

### 3. Database Setup

Using Docker or local Postgres:
```bash
psql -U postgres -d bio_geo_guesser -f database/create_db.pgsql
```

## Documentation

-   [Backend Documentation](./backend/README.md)
-   [Frontend Documentation](./frontend/frontend/README.md)
-   [API Reference](./docs/API.md)
-   [Database Schema](./docs/DATABASE.md)
