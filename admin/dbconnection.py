import psycopg
import dotenv
dotenv.load_dotenv()   
import os

db = os.getenv("db_url")
conn = psycopg.connect(db)

print(conn)
