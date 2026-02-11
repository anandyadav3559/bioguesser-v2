# Backend Documentation

The backend is built with **Django 6.0** and **Django REST Framework**.

## Tech Stack
-   **Framework**: Django 6.0 + DRF 3.16
-   **Database**: PostgreSQL (via `psycopg`)
-   **Cache/Session**: Redis (via `django-redis`)
-   **Authentication**: JWT (`simplejwt`) + Custom Session Management

## Setup

1.  **Environment Variables**:
    Create a `.env` file in the root directory (or backend root) with:
    ```env
    SECRET_KEY=your-secret-key
    DEBUG=True
    ALLOWED_HOSTS=*
    DB_NAME=bio_geo_guesser
    DB_USER=root
    DB_PASSWORD=root
    DB_HOST=localhost
    DB_PORT=5432
    REDIS_HOST=localhost
    REDIS_PORT=6379
    GOOGLE_CLIENT_ID=your-google-client-id
    ```

2.  **Dependencies**:
    ```bash
    pip install -r requirements.txt
    # OR using uv
    uv pip install -r requirements.txt
    ```

3.  **Run Server**:
    ```bash
    python manage.py runserver
    ```

## Application Structure

-   **`backend/`**: Core project settings (`settings.py`, `urls.py`, `wsgi.py`).
-   **`authentication/`**: Custom authentication logic (Guest, Google OAuth, Session Management).
-   **`manage.py`**: Django management script.

## Key Features

-   **CORS**: Configured to allow frontend origins (`http://localhost:5173`).
-   **Redis Sessions**: User sessions (Guest & Permanent) are stored in Redis with a 30-day TTL.
-   **Google OAuth**: Integated verification of Google ID tokens.
