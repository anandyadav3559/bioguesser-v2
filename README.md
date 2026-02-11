# Bio-Geoguesser V2

A full-stack interactive geography guessing game where players identify animal habitats.

## 🌟 Features
- **Interactive Gameplay**: Guess the natural habitat of various animals on a map.
- **Real-time Scoring**: Get immediate feedback on your guesses.
- **Multi-Login Options**: Play as a Guest or sign in with Google.
- **Rich Data**: Facts and images sourced from iNaturalist and Wikipedia.

## 🏗️ Project Architecture

The application is composed of three main parts:

1.  **Frontend (`frontend/frontend/`)**: 
    -   Built with **React** and **Vite**.
    -   Handles the user interface, map interactions (Leaflet/Google Maps), and authentication flows.
    -   Communicates with the backend via REST API.

2.  **Backend (`backend/`)**:
    -   Built with **Django REST Framework (DRF)**.
    -   Manages game logic, user sessions, and database interactions.
    -   Uses **PostgreSQL** for persistent data (Users, Animals, Scores) and **Redis** for session management.

3.  **Data Extraction (`extraction/`)**:
    -   Python scripts to scrape and ingest animal data from iNaturalist and Wikipedia into the database.

## 🚀 Quick Start

### Prerequisites
-   **Python 3.11+**
-   **Node.js 18+**
-   **PostgreSQL**
-   **Redis**
-   **uv** (optional, for fast Python package management)

### 1. Database & Redis Setup
Ensure PostgreSQL and Redis are running.
```bash
# Example using Docker
docker run --name redis -p 6379:6379 -d redis
docker run --name postgres -e POSTGRES_PASSWORD=root -p 5432:5432 -d postgres
```

### 2. Backend Setup
```bash
cd backend
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure Environment Variables (.env)
cp .env.example .env  # (Create .env if not exists)
# Edit .env with your DB and Redis credentials

# Run Migrations
python manage.py migrate

# Start Server
python manage.py runserver
```

### 3. Frontend Setup
```bash
cd frontend/frontend
npm install

# Configure Environment Variables
# Create .env file with:
# VITE_API_BASE_URL=http://localhost:8000/api
# VITE_GOOGLE_CLIENT_ID=your-google-client-id

# Start Development Server
npm run dev
```

## 📚 Documentation

Detailed documentation for each component can be found here:

-   [**Backend Documentation**](./backend/README.md) - API endpoints, Auth flows, Django settings.
-   [**Frontend Documentation**](./frontend/frontend/README.md) - Components, State management, Build process.
-   [**Extraction Pipeline**](./extraction/README.md) - How to ingest new animal data.
-   [**Database Schema**](./docs/DATABASE.md) - SQL tables and relationships.

## 🤝 Contribution
1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.
