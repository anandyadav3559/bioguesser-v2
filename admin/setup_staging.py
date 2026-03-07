"""
Run once to create the three staging tables.
  python setup_staging.py
"""
from db import get_conn

SQL = """
CREATE TABLE IF NOT EXISTS staging_animals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    scientific_name TEXT UNIQUE,
    image_url TEXT,
    max_probability DOUBLE PRECISION,
    entropy DOUBLE PRECISION,
    status TEXT NOT NULL DEFAULT 'pending',   -- pending | approved | rejected
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS staging_animal_characteristics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    animal_id UUID REFERENCES staging_animals(id) ON DELETE CASCADE,
    prey TEXT,
    gestation_period TEXT,
    habitat TEXT,
    predators TEXT,
    average_litter_size TEXT,
    top_speed TEXT,
    lifespan TEXT,
    weight TEXT,
    length TEXT,
    skin_type TEXT,
    color TEXT,
    age_of_sexual_maturity TEXT,
    age_of_weaning TEXT
);

CREATE TABLE IF NOT EXISTS staging_animal_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    animal_id UUID REFERENCES staging_animals(id) ON DELETE CASCADE,
    h3_index TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    count INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_staging_locations_animal_id ON staging_animal_locations(animal_id);
CREATE INDEX IF NOT EXISTS idx_staging_animals_status ON staging_animals(status);
"""

if __name__ == "__main__":
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(SQL)
        conn.commit()
    print("✅ Staging tables created successfully.")
