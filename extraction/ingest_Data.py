# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "psycopg[binary]",
#     "aiohttp",
#     "python-dotenv",
#     "wikipedia-api",
# ]
# ///

import logging
import uuid
import asyncio
import aiohttp
import psycopg
from psycopg.types.json import Json
import os
import dotenv
import wikipediaapi

dotenv.load_dotenv()

# ===================== LOGGING CONFIG =====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ===================== CONFIG =====================

INATURALIST_URL = "https://api.inaturalist.org/v1/observations"

PER_PAGE = 200
MAX_PAGES = 10
TARGET_POINTS = 1000
ROUND_DECIMALS = 3

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

# The user_agent is required by Wikipedia's terms of service
wiki = wikipediaapi.Wikipedia(
    user_agent='BioGeoguesserProject/1.0 (contact: [EMAIL_ADDRESS])',
    language='en',
    extract_format=wikipediaapi.ExtractFormat.WIKI
)

# ===================== DB HELPERS =====================

async def get_db_conn():
    conn = await psycopg.AsyncConnection.connect(**DB_CONFIG)
    return conn

async def animal_exists(conn, scientific_name):
    async with conn.cursor() as cur:
        await cur.execute(
            """
            SELECT 1 FROM animals
            WHERE scientific_name = %s
            LIMIT 1;
            """,
            (scientific_name,)
        )
        return await cur.fetchone() is not None

async def insert_animal(conn, animal_id, name, scientific_name, image_url, locations, fact):
    async with conn.cursor() as cur:
        await cur.execute(
            """
            INSERT INTO animals (
                animal_id,
                name,
                scientific_name,
                image_url,
                locations,
                fact
            )
            VALUES (%s, %s, %s, %s, %s, %s);
            """,
            (
                animal_id,
                name,
                scientific_name,
                image_url,
                Json(locations),
                fact
            )
        )
    await conn.commit()

# ===================== INGESTION HELPERS =====================

async def fetch_inaturalist_page(session, query, page):
    """Fetch a single page of results from iNaturalist API."""
    params = {
        "quality_grade": "research",
        "photos": "true",
        "geo": "true",
        "captive": "false",
        "per_page": str(PER_PAGE),
        "taxon_name": query,
        "page": str(page)
    }
    
    logger.info(f"Page {page}: Fetching from {INATURALIST_URL}?")
    try:
        async with session.get(INATURALIST_URL, params=params) as resp:
            resp.raise_for_status()
            return await resp.json()
    except aiohttp.ClientError as e:
        logger.error(f"Error fetching page {page}: {e}")
        return None

def extract_taxon_info(result):
    """Extract scientific and common name from a result."""
    taxon = result.get("taxon")
    if not taxon:
        return None, None
    
    scientific_name = taxon.get("name")
    common_name = taxon.get("preferred_common_name") or scientific_name
    return scientific_name, common_name

def extract_location(result):
    """Extract latitude and longitude from a result."""
    coords = result.get("geojson", {}).get("coordinates")
    if not coords:
        return None
    
    lon, lat = coords
    return round(lat, ROUND_DECIMALS), round(lon, ROUND_DECIMALS)

def extract_image_url(result):
    """Extract the first medium-sized image URL."""
    photos = result.get("photos", [])
    if photos:
        return photos[0]["url"].replace("square", "medium")
    return None

def get_wiki_fact(scientific_name):
    try:
        page = wiki.page(scientific_name)
        if page.exists():
            # Get the first two sentences of the summary
            summary = page.summary.split('. ')
            fact = ". ".join(summary[:2]) + "."
            return fact
        return f"{scientific_name} is a fascinating species found in diverse ecosystems."
    except Exception as e:
        logger.error(f"Wiki lookup failed: {e}")
        return "Species data currently being updated."

# ===================== MAIN INGESTION =====================

async def ingest_animal(input_name):
    """
    input_name:
      - can be common name (any language)
      - or scientific name
      - treated ONLY as a search hint
    """
    logger.info(f"Starting ingestion for input_name='{input_name}'")
    
    conn = await get_db_conn()
    
    unique_points = set()
    locations = []
    image_url = None
    scientific_name = None
    common_name = None
    page = 1
    
    try:
        async with aiohttp.ClientSession() as session:
            while len(unique_points) < TARGET_POINTS and page <= MAX_PAGES:
                data = await fetch_inaturalist_page(session, input_name, page)
                if not data:
                    break
                    
                results = data.get("results", [])
                logger.info(f"Page {page}: Found {len(results)} results")
                
                if not results:
                    logger.info(f"Page {page}: No results found. Stopping pagination.")
                    break
                
                new_points = 0
                
                for r in results:
                    # Identify Taxon (only need to do this once per animal)
                    if scientific_name is None:
                        s_name, c_name = extract_taxon_info(r)
                        if not s_name:
                            continue
                            
                        scientific_name = s_name
                        common_name = c_name
                        

                        # Check DB for duplicates
                        if await animal_exists(conn, scientific_name):
                            logger.info(f"SKIP: Scientific name '{scientific_name}' already exists in DB")
                            return
                        
                        logger.info(f"Resolved Taxon: Common='{common_name}', Scientific='{scientific_name}'")
                        
                        # Get Fact
                        fact = get_wiki_fact(scientific_name)
                        logger.info(f"Fetched fact: {fact[:50]}...")

                    # Extract Location
                    loc = extract_location(r)
                    if not loc:
                        continue
                    
                    lat, lon = loc
                    if loc in unique_points:
                        continue
                    
                    unique_points.add(loc)
                    locations.append({"lat": lat, "lon": lon})
                    new_points += 1
                    
                    # Extract Image (only need one)
                    if image_url is None:
                        image_url = extract_image_url(r)
                    
                    if len(unique_points) >= TARGET_POINTS:
                        break
                
                # Saturation detection
                if new_points < 10:
                    logger.warning(f"Saturation reached at page {page} with only {new_points} new points. Stopping.")
                    break
                
                page += 1

        if not locations or not scientific_name:
            logger.error(f"FAIL: No usable data found for '{input_name}'. Locations: {len(locations)}, Scientific Name: {scientific_name}")
            return
            
        if image_url is None:
            image_url = "https://via.placeholder.com/800x600.jpg"
            
        animal_id = str(uuid.uuid4())
        
        await insert_animal(conn, animal_id, common_name, scientific_name, image_url, locations, fact)
        
        logger.info(
            f"DONE: Inserted '{common_name}' ({scientific_name}) with {len(locations)} points. "
            f"Image URL: {image_url}"
        )
        
    finally:
        if conn:
            await conn.close()


async def safe_ingest(semaphore, name):
    async with semaphore:
        try:
            await ingest_animal(name)
        except Exception as e:
            logger.error(f"Error processing {name}: {e}")

async def main(animals):
    # Limit max concurrent tasks to avoid hammering API/DB
    # iNaturalist asks for < 1 request/second ideally, but bursts are okay.
    # We will limit to 3 concurrent generic tasks.
    semaphore = asyncio.Semaphore(3)

    await asyncio.gather(
        *(safe_ingest(semaphore, a) for a in animals)
    )

if __name__ == "__main__":
    animals = []
    with open("animals.txt",'r+') as f:
        animals = f.read().splitlines()
        f.truncate(0)
    asyncio.run(main(animals))
