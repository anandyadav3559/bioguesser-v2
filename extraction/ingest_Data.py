import os
import psycopg
from dotenv import load_dotenv
import h3
import math

load_dotenv()

# Database connection parameters
DB_NAME = os.getenv("DB_NAME", "bio_geo_guesser")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DATABASE_URL = os.getenv("db_url") 

# H3 Resolution for clustering (0-15, where 0 is global and 15 is sub-meter)
# Resolution 2 is roughly 158km edge length, good for state/large region clustering
H3_RESOLUTION = 2

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg.connect(
            DATABASE_URL,
            autocommit=True
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def create_schema(conn):
    """Creates the necessary tables in the database."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS animals (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name TEXT NOT NULL,
                scientific_name TEXT UNIQUE,
                image_url TEXT,
                max_probability DOUBLE PRECISION,
                entropy DOUBLE PRECISION,
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
            cur.execute("SELECT id, image_url FROM animals WHERE scientific_name = %s", (scientific_name,))
            res = cur.fetchone()
            
            # Extract image_url from observations_data
            image_url = None
            results = observations_data.get('results', [])
            for obs in results:
                if 'photos' in obs and len(obs['photos']) > 0:
                    image_url = obs['photos'][0].get('url')
                    if image_url:
                        image_url = image_url.replace('square', 'medium')
                        break
                elif 'taxon' in obs and obs.get('taxon', {}).get('default_photo'):
                    image_url = obs['taxon']['default_photo'].get('medium_url') or obs['taxon']['default_photo'].get('url')
                    if image_url:
                        break

            if res:
                animal_id = res[0]
                existing_img = res[1]
                if not existing_img and image_url:
                    cur.execute("UPDATE animals SET image_url = %s WHERE id = %s", (image_url, animal_id))
                    print(f"Animal {animal['name']} ({scientific_name}) already exists. Updated image_url.")
                else:
                    print(f"Animal {animal['name']} ({scientific_name}) already exists with ID {animal_id}. Skipping insert.")
                # Optional: Update characteristics if needed, or skip. Here we skip.
                return True 
            else:
                cur.execute("""
                    INSERT INTO animals (name, scientific_name, image_url)
                    VALUES (%s, %s, %s)
                    RETURNING id;
                """, (animal['name'], scientific_name, image_url))
                animal_id = cur.fetchone()[0]
                print(f"Inserted animal: {animal['name']} (ID: {animal_id}) with image: {image_url}")

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

            # Insert clusters and compute entropy
            total_sightings = 0
            valid_clusters = []
            
            for h3_idx, data in clusters.items():
                count = data['count']
                if count < 10:
                    continue  # Skip clusters with fewer than 10 data points
                
                total_sightings += count
                valid_clusters.append((h3_idx, data))

                avg_lat = data['lat_sum'] / count
                avg_lon = data['lon_sum'] / count
                
                cur.execute("""
                    INSERT INTO animal_locations (animal_id, h3_index, latitude, longitude, count)
                    VALUES (%s, %s, %s, %s, %s);
                """, (animal_id, h3_idx, avg_lat, avg_lon, count))
            
            print(f"Inserted {len(valid_clusters)} location clusters for {animal['name']}")

            if total_sightings > 0:
                p_max = 0
                entropy = 0
                for _, data in valid_clusters:
                    count = data['count']
                    p_cell = count / total_sightings
                    if p_cell > p_max:
                        p_max = p_cell
                    entropy -= p_cell * math.log(p_cell)
                
                cur.execute("""
                    UPDATE animals SET max_probability = %s, entropy = %s WHERE id = %s
                """, (p_max, entropy, animal_id))
                print(f"Computed P_max: {p_max:.4f}, Entropy: {entropy:.4f} for {animal['name']}")
    return True

import requests
import time

# ... (Previous imports and constants remain the same) ...

API_NINJAS_KEY = os.getenv("API_NINJAS_KEY")
INATURALIST_API_URL = "https://api.inaturalist.org/v1/observations"

def fetch_animal_details(animal_name):
    """Fetches animal characteristics from API Ninjas."""
    api_url = f'https://api.api-ninjas.com/v1/animals?name={animal_name}'
    try:
        response = requests.get(api_url, headers={'X-Api-Key': API_NINJAS_KEY})
        if response.status_code == 200:
            data = response.json()
            if data:
                return data # Returns a list of animals
            else:
                print(f"No details found for {animal_name}")
                return None
        else:
            print(f"Error fetching animal details: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"Exception fetching details: {e}")
        return None

def fetch_observations(scientific_name, start_page=1, per_page=200, max_pages=1, fetch_all=False):
    """Fetches observations from iNaturalist with custom pagination."""
    all_observations = []
    
    print(f"Fetching observations for {scientific_name}...")
    if fetch_all:
        print(f"Mode: Fetch until exhaustion. Starting at page {start_page}, {per_page} per page.")
    else:
        print(f"Mode: Fetch max {max_pages} pages. Starting at page {start_page}, {per_page} per page.")

    current_page = start_page
    pages_fetched = 0

    while True:
        if not fetch_all and pages_fetched >= max_pages:
            print(f"Reached max pages limit ({max_pages}).")
            break
            
        params = {
            'taxon_name': scientific_name,
            'per_page': per_page,
            'page': current_page,
            'order': 'desc',
            'order_by': 'created_at'
        }
        
        try:
            print(f"Fetching page {current_page}...")
            response = requests.get(INATURALIST_API_URL, params=params)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                if not results:
                    print(f"No more results found at page {current_page}.")
                    break
                
                all_observations.extend(results)
                pages_fetched += 1
                current_page += 1
                
                # Respect API rate limits
                time.sleep(1.0) 
            else:
                print(f"Error fetching observations: {response.status_code}")
                break
                
        except Exception as e:
            print(f"Exception fetching observations: {e}")
            break

    total_fetched = len(all_observations)
    print(f"Total observations fetched: {total_fetched}")
    return {'results': all_observations}


def remove_animal_from_file(file_path, animal_to_remove):
    """Removes the processed animal from the text file."""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        with open(file_path, 'w') as f:
            for line in lines:
                if line.strip().lower() != animal_to_remove.lower():
                    f.write(line)
        print(f"Removed {animal_to_remove} from {file_path}")
    except Exception as e:
        print(f"Error removing {animal_to_remove} from file: {e}")

def check_animal_exists(conn, animal_name):
    """Checks if an animal with the given common name already exists in the DB."""
    with conn.cursor() as cur:
        # Check by common name (case-insensitive search could be better, but strict for now)
        cur.execute("SELECT id FROM animals WHERE name ILIKE %s", (animal_name,))
        return cur.fetchone() is not None

if __name__ == "__main__":
    # --- Configuration ---
    START_PAGE = 1
    PER_PAGE = 200     # Max 200 for iNaturalist
    MAX_PAGES = 10      # How many pages to fetch if FETCH_ALL is False
    FETCH_ALL = False  # Set to True to fetch ALL available data until exhaustion
    # ---------------------

    conn = get_db_connection()
    if conn:
        create_schema(conn)
        
        # 1. Read Animal List
        try:
            with open('animals.txt', 'r') as f:
                # Store as list to iterate
                animals_to_process = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print("animals.txt not found. Please create it with animal names.")
            animals_to_process = []

        if not animals_to_process:
            print("No animals to process.")
        else:
            if FETCH_ALL:
                print(f"Configuration: Fetching ALL pages starting from {START_PAGE} ({PER_PAGE}/page)")
            else:
                print(f"Configuration: Fetching MAX {MAX_PAGES} pages starting from {START_PAGE} ({PER_PAGE}/page)")

            # Iterate over a copy so we can modify the file safely without affecting the loop
            for animal_name in animals_to_process:
                print(f"\n--- Processing {animal_name} ---")
                
                # 0. Pre-check DB
                if check_animal_exists(conn, animal_name):
                    print(f"Animal '{animal_name}' already exists in database. Skipping API calls.")
                    remove_animal_from_file('animals.txt', animal_name)
                    continue

                # A. Fetch Details
                animal_details_list = fetch_animal_details(animal_name)
                
                success = False
                if animal_details_list:
                    # API Ninjas returns a list, usually the first one is best match
                    animal_data = animal_details_list[0] 
                    scientific_name = animal_data['taxonomy']['scientific_name']
                    print(f"Scientific Name: {scientific_name}")
                    
                    # B. Fetch Observations
                    observations_data = fetch_observations(
                        scientific_name, 
                        start_page=START_PAGE, 
                        per_page=PER_PAGE, 
                        max_pages=MAX_PAGES, 
                        fetch_all=FETCH_ALL
                    )
                    
                    if observations_data.get('results'):
                         # C. Insert Data
                         # insert_animal_data returns True if successful or already exists
                         if insert_animal_data(conn, [animal_data], observations_data):
                             success = True
                    # Even if no observations, if animal inserted/exists, we might count it as done if returning True
                    elif insert_animal_data(conn, [animal_data], {'results': []}): 
                         success = True
                         print(f"No observations found for {scientific_name}, but animal processed.")
                else:
                    print(f"Skipping {animal_name} due to missing details.")
                
                # Remove from file if successful
                if success:
                    remove_animal_from_file('animals.txt', animal_name)

        conn.close()