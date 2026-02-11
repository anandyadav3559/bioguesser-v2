# Data Extraction Pipeline

Scripts and tools to ingest animal data from external sources (iNaturalist, Wikipedia) into the Bio-Geoguesser database.

## 📋 Overview

The extraction pipeline performs the following steps:
1.  **Read List**: Reads a list of animal names from `animals.txt`.
2.  **Fetch Data**:
    -   Queries **iNaturalist API** for observation data (images, locations, scientific names).
    -   Queries **Wikipedia API** for a short fact about the animal.
3.  **Process**: Normalizes the data and prepares it for insertion.
4.  **Ingest**: Inserts the data into the PostgreSQL database, handling duplicates.

## ⚙️ Setup

### 1. Prerequisites
-   Python 3.11+
-   PostgreSQL database running

### 2. Environment Variables
Create a `.env` file in the `extraction/` directory:

```ini
DB_NAME=bio_geo_guesser
DB_USER=postgres
DB_PASSWORD=root
DB_HOST=localhost
DB_PORT=5432
```

### 3. Dependencies
Install the required Python packages:

```bash
# Using pip
pip install psycopg[binary] aiohttp python-dotenv wikipedia-api

# OR using uv
uv pip install psycopg[binary] aiohttp python-dotenv wikipedia-api
```

## 🏃 Usage

### 1. Prepare Animal List
Edit `animals.txt` and add the names of animals you want to ingest, one per line.
```text
Panthera leo
Aptenodytes forsteri
Loxodonta africana
```

### 2. Run Ingestion Script
Execute the script to start the process:

```bash
python ingest_Data.py
```

> **Note:** The script will clear the contents of `animals.txt` after a successful run to prevent double-processing.

## 🗄️ Database Schema

Data is inserted into the `animals` table:

| Column | Type | Description |
|--------|------|-------------|
| `animal_id` | UUID | Primary Key |
| `name` | TEXT | Common Name |
| `scientific_name` | TEXT | Scientific Name (Unique) |
| `image_url` | TEXT | URL to animal image |
| `locations` | JSONB | Array of lat/lon coordinates |
| `fact` | TEXT | Fun fact description |
