import os
import psycopg
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

def get_conn():
    url = os.getenv("db_url") #or os.getenv("db_url")
    if not url:
        raise RuntimeError("No DATABASE_URL or db_url found in environment")
    return psycopg.connect(url)
