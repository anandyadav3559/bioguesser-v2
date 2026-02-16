
import os
import json
import psycopg
from dotenv import load_dotenv
import h3

load_dotenv()

# Database connection parameters
DB_NAME = os.getenv("DB_NAME", "bio_geo_guesser")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# H3 Resolution for clustering (0-15, where 0 is global and 15 is sub-meter)
# Resolution 4 is roughly 22km edge length, good for regional clustering
H3_RESOLUTION = 4

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            autocommit=True
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def create_schema(conn):
    """Creates the necessary tables in the database."""
    with conn.cursor() as cur:
        # Create animals table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS animals (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name TEXT NOT NULL,
                scientific_name TEXT UNIQUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)

        # Create animal_characteristics table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS animal_characteristics (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                animal_id UUID REFERENCES animals(id) ON DELETE CASCADE,
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
        """)

        # Create animal_locations table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS animal_locations (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                animal_id UUID REFERENCES animals(id) ON DELETE CASCADE,
                h3_index TEXT NOT NULL,
                latitude DOUBLE PRECISION NOT NULL,
                longitude DOUBLE PRECISION NOT NULL,
                count INTEGER DEFAULT 1,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)

        # Create indexes
        cur.execute("CREATE INDEX IF NOT EXISTS idx_animal_locations_animal_id ON animal_locations(animal_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_animal_locations_h3_index ON animal_locations(h3_index);")
        
        print("Schema created successfully.")

def insert_animal_data(conn, animal_data, observations_data):
    """Inserts animal, characteristics, and location clusters."""
    with conn.cursor() as cur:
        for animal in animal_data:
            # 1. Insert Animal
            scientific_name = animal['taxonomy']['scientific_name']
            
            # Check if animal already exists to avoid duplicates (or handle upsert)
            cur.execute("SELECT id FROM animals WHERE scientific_name = %s", (scientific_name,))
            res = cur.fetchone()
            
            if res:
                animal_id = res[0]
                print(f"Animal {animal['name']} ({scientific_name}) already exists with ID {animal_id}. Skipping insert.")
                # Optional: Update characteristics if needed, or skip. Here we skip.
                continue 
            else:
                cur.execute("""
                    INSERT INTO animals (name, scientific_name)
                    VALUES (%s, %s)
                    RETURNING id;
                """, (animal['name'], scientific_name))
                animal_id = cur.fetchone()[0]
                print(f"Inserted animal: {animal['name']} (ID: {animal_id})")

            # 2. Insert Characteristics
            chars = animal.get('characteristics', {})
            cur.execute("""
                INSERT INTO animal_characteristics (
                    animal_id, prey, gestation_period, habitat, predators, 
                    average_litter_size, top_speed, lifespan, weight, length, 
                    skin_type, color, age_of_sexual_maturity, age_of_weaning
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                );
            """, (
                animal_id,
                chars.get('prey'),
                chars.get('gestation_period'),
                chars.get('habitat'),
                chars.get('predators'),
                chars.get('average_litter_size'),
                chars.get('top_speed'),
                chars.get('lifespan'),
                chars.get('weight'),
                chars.get('length'),
                chars.get('skin_type'),
                chars.get('color'),
                chars.get('age_of_sexual_maturity'),
                chars.get('age_of_weaning')
            ))
            print(f"Inserted characteristics for {animal['name']}")

            # 3. Process and Insert Location Clusters
            # Observations data is a dict with 'results' list
            clusters = {} # h3_index -> {'count': 0, 'lat_sum': 0, 'lon_sum': 0}
            
            # Filter results for this specific animal if the observations_data contains mixed data
            # Assuming 'observations_data' corresponds to the search results for this animal
            # In a real pipeline, you'd match by scientific name or ID
            
            results = observations_data.get('results', [])
            print(f"Processing {len(results)} observations for clustering...")
            
            for obs in results:
                # Check for valid location
                if obs.get('location'):
                    try:
                        lat_str, lon_str = obs['location'].split(',')
                        lat = float(lat_str)
                        lon = float(lon_str)
                        
                        # Get H3 index
                        h3_index = h3.latlng_to_cell(lat, lon, H3_RESOLUTION)
                        
                        if h3_index not in clusters:
                            clusters[h3_index] = {'count': 0, 'lat_sum': 0, 'lon_sum': 0}
                        
                        clusters[h3_index]['count'] += 1
                        clusters[h3_index]['lat_sum'] += lat
                        clusters[h3_index]['lon_sum'] += lon
                    except ValueError:
                        continue # Skip invalid location formats

            # Insert clusters
            for h3_idx, data in clusters.items():
                count = data['count']
                avg_lat = data['lat_sum'] / count
                avg_lon = data['lon_sum'] / count
                
                cur.execute("""
                    INSERT INTO animal_locations (animal_id, h3_index, latitude, longitude, count)
                    VALUES (%s, %s, %s, %s, %s);
                """, (animal_id, h3_idx, avg_lat, avg_lon, count))
            
            print(f"Inserted {len(clusters)} location clusters for {animal['name']}")

if __name__ == "__main__":
    conn = get_db_connection()
    if conn:
        create_schema(conn)
        
        # Example Usage with provided mock data structure
        # In a real scenario, you would fetch this from the APIs
        
        # example_animal_data = [...] (from user's first JSON)
        # example_observations = {...} (from user's second JSON)
        
        # For demonstration, we can load from files or just run schema creation if no data is present.
        print("Database schema initialized. Run with data to ingest.")
        
        conn.close()