# Backend Documentation

The backend of Bio-Geoguesser V2 is a robust REST API built with **Django** and **Django REST Framework (DRF)**. It handles user authentication, game session management, and serves animal data.

## 🛠️ Tech Stack

-   **Framework**: Django 6.0 + Django REST Framework 3.16
-   **Database**: PostgreSQL
-   **Caching & Sessions**: Redis
-   **Authentication**: JWT (JSON Web Tokens) + Custom Redis-based Session Management
-   **Task Queue**: (Optional/Planned) Celery for background tasks

## ⚙️ Setup & Installation

### 1. Prerequisites
-   Python 3.11+
-   PostgreSQL running
-   Redis running

### 2. Installation

Navigate to the `backend` directory:
```bash
cd backend
```

Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the `backend` directory. 

**Required Variables:**

```ini
# Django Settings
SECRET_KEY=your-super-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=*

# Database (PostgreSQL)
DB_NAME=bio_geo_guesser
DB_USER=postgres
DB_PASSWORD=root
DB_HOST=localhost
DB_PORT=5432

# Redis (Caching & Sessions)
REDIS_HOST=localhost
REDIS_PORT=6379

# Google OAuth (For Google Login)
GOOGLE_CLIENT_ID=your-google-client-id
```

### 4. Database Migration

Apply the database migrations to set up the schema:

```bash
python manage.py migrate
```

### 5. Create Superuser (Optional)

To access the Django Admin panel:

```bash
python manage.py createsuperuser
```

### 6. Run Server

```bash
python manage.py runserver
```
The API will be available at `http://127.0.0.1:8000/`.

## 🔐 Authentication

Authentication is handled by the `authentication` app. We use a hybrid approach:
-   **JWT**: Used for stateless API authentication.
-   **Redis Sessions**: Used to manage the validity of the JWTs. If a session is deleted from Redis, the corresponding JWT becomes invalid.

### Flows
1.  **Guest Login**: Creates a temporary user and session.
2.  **Google Login**: Verifies Google ID Token and creates/retrieves a permanent user.

See [Authentication README](./authentication/README.md) for detailed endpoint documentation.

## 📂 Project Structure

-   `backend/`: Project configuration (`settings.py`, `urls.py`).
-   `authentication/`: User auth logic, models, and views.
-   `game/`: (Planned) Game logic, rounds, and scoring.
-   `api/`: (Planned) General API endpoints.
-   `multiplayer/`: Real-time multiplayer logic using Django Channels.
