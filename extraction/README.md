# Extraction Pipeline

The extraction pipeline populates the BioGuesser database with animal data. It fetches species characteristics from [API Ninjas](https://api-ninjas.com/) and real-world observation records from [iNaturalist](https://www.inaturalist.org/), clusters the observations into H3 hexagonal cells, and inserts everything into PostgreSQL.

---

## Files

| File                 | Description                                           |
| -------------------- | ----------------------------------------------------- |
| `ingest_Data.py`     | Main ingestion script                                 |
| `animals.txt`        | Line-separated list of animal common names to process |
| `docker-compose.yml` | Spins up a local PostgreSQL instance for development  |

---

## Data Flow

```
animals.txt
    │
    ▼
fetch_animal_details()          ← API Ninjas (characteristics)
    │
    ▼
fetch_observations()            ← iNaturalist (GPS sightings)
    │
    ▼
H3 clustering (resolution 2)    ← ~158 km edge-length cells
    │
    ▼
insert_animal_data()            ← PostgreSQL (determines table based on --staging)
    │
    ├─► (Production Mode)  ➔ animals / animal_characteristics / animal_locations
    └─► (Staging Mode)     ➔ staging_animals / staging_animal_characteristics / staging_animal_locations
```

---

## Database Schema Created

The script creates three tables if they don't exist. If run with the `--staging` flag, it creates prepended tables (e.g., `staging_animals`) with an extra `status` column to hold data for administrative review.

### `animals` / `staging_animals`

| Column            | Type               | Notes                                                        |
| ----------------- | ------------------ | ------------------------------------------------------------ |
| `id`              | `UUID`             | Auto-generated PK                                            |
| `name`            | `TEXT`             | Common name                                                  |
| `scientific_name` | `TEXT UNIQUE`      | Used as deduplication key                                    |
| `image_url`       | `TEXT`             | Extracted from iNaturalist observation photos                |
| `max_probability` | `DOUBLE PRECISION` | Maximum H3 cell sighting probability (used for game scoring) |
| `entropy`         | `DOUBLE PRECISION` | Shannon entropy of sighting distribution                     |

### `animal_characteristics`

All biology fields from API Ninjas: `prey`, `habitat`, `predators`, `top_speed`, `lifespan`, `weight`, `length`, `skin_type`, `color`, `gestation_period`, `average_litter_size`, `age_of_sexual_maturity`, `age_of_weaning`.

### `animal_locations`

| Column      | Type               | Notes                                        |
| ----------- | ------------------ | -------------------------------------------- |
| `h3_index`  | `TEXT`             | H3 cell identifier at resolution 2           |
| `latitude`  | `DOUBLE PRECISION` | Average latitude of observations in the cell |
| `longitude` | `DOUBLE PRECISION` | Average longitude                            |
| `count`     | `INTEGER`          | Number of sightings in this cell             |

**Indexes**: `animal_id`, `h3_index`

---

## H3 Clustering

Observations from iNaturalist are bucketed into [H3](https://h3geo.org/) hexagonal cells at **resolution 2** (edge length ≈ 158 km). This balances geographic precision with dataset size.

- Cells with **fewer than 10 observations** are discarded (noise filter)
- Each valid cluster stores the **average lat/lng** of all observations in the cell

After inserting clusters, `max_probability` and Shannon `entropy` are computed per animal:

```python
p_cell = count / total_sightings
entropy -= p_cell * log(p_cell)
p_max = max(p_cell for all cells)
```

These values drive the scoring algorithm in `game.services.GameService.evaluate_round()`.

---

## Configuration

Set via `.env` file or environment variables:

| Variable         | Default           | Description                                            |
| ---------------- | ----------------- | ------------------------------------------------------ |
| `DB_NAME`        | `bio_geo_guesser` | PostgreSQL database name                               |
| `DB_USER`        | `postgres`        | DB user                                                |
| `DB_PASSWORD`    | `root`            | DB password                                            |
| `DB_HOST`        | `localhost`       | DB host                                                |
| `DB_PORT`        | `5432`            | DB port                                                |
| `API_NINJAS_KEY` | _(required)_      | API key from [api-ninjas.com](https://api-ninjas.com/) |

Script-level constants (edit in `ingest_Data.py`):

| Constant        | Default | Description                               |
| --------------- | ------- | ----------------------------------------- |
| `START_PAGE`    | `1`     | iNaturalist pagination start              |
| `PER_PAGE`      | `200`   | Observations per page (max 200)           |
| `MAX_PAGES`     | `10`    | Pages to fetch when `FETCH_ALL=False`     |
| `FETCH_ALL`     | `False` | Set `True` to exhaust all available pages |
| `H3_RESOLUTION` | `2`     | H3 grid resolution                        |

---

## Running the Pipeline

```bash
# 1. Start the database (if using Docker)
cd extraction/
docker compose up -d

# 2. Add animal names to animals.txt (one per line)
echo "Lion" >> animals.txt
echo "African Elephant" >> animals.txt

# 3. Run ingestion (Production)
python ingest_Data.py

# OR Run ingestion into Staging (Admin Review required)
python ingest_Data.py --staging
```

The script is **resumable**: it checks if an animal already exists in the DB before making API calls, and removes successfully processed animals from `animals.txt` so re-runs skip them.

---

## Rate Limiting

- iNaturalist: `time.sleep(1.0)` between page requests
- API Ninjas: one request per animal (no pagination needed)

---

## Dependencies

```
psycopg       # PostgreSQL driver (psycopg3)
h3            # H3 hexagonal indexing
python-dotenv # .env loading
requests      # HTTP client
```

Install with: `uv sync` or `pip install psycopg h3 python-dotenv requests`
