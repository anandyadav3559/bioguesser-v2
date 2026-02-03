# BioGeoguesser Extraction Pipeline

This project ingests animal observation data from iNaturalist and facts from Wikipedia into a PostgreSQL database.

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- `uv` (recommended for dependency management and running scripts)

## Setup & Running

### 1. Database Setup
Start the PostgreSQL database using Docker Compose before running any scripts.

```bash
cd extraction
docker-compose up -d
```

### 2. Environment Variables
Ensure you have a `.env` file in the `extraction` directory with the following variables:
```
DB_NAME=bio_geo_guesser
DB_USER=root
DB_PASSWORD=root
DB_HOST=localhost
DB_PORT=5432
```

### 3. Ingestion Script
The script `ingest_Data.py` reads a list of animals, fetches data, and stores it in the database.

**Animals Input (`animals.txt`):**
- Add animal names (scientific or common) to `animals.txt`, one per line.
- **Note:** The script **clears this file** after reading it to ensure animals are processed only once.

**Run the script:**
Using `uv` (handles dependencies automatically):
```bash
uv run ingest_Data.py
```

Or manually:
```bash
pip install psycopg[binary] aiohttp python-dotenv wikipedia-api
python ingest_Data.py
```

## Database Schema

The data is stored in the `animals` table in the `bio_geo_guesser` database.

```sql
CREATE TABLE animals (
    animal_id        UUID PRIMARY KEY,
    name             TEXT UNIQUE NOT NULL,      -- Common name
    scientific_name  TEXT UNIQUE NOT NULL,      -- Scientific name
    image_url        TEXT NOT NULL,             -- URL to a medium-sized image
    locations        JSONB,                     -- List of {"lat": ..., "lon": ...} objects
    fact             TEXT                       -- Short fact from Wikipedia
);
```
