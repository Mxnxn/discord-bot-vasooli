import sqlite3 as sql
from dotenv import load_dotenv
import os

load_dotenv()
DB_NAME = os.getenv('DB_NAME')

def data_fetcher(query):
    conn = sql.connect(DB_NAME)
    cursor = conn.cursor()
    rows = cursor.execute(query).fetchall()
    conn.close()
    return rows