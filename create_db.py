import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

try:
    # Connect to default 'postgres' database to create a new one
    conn = psycopg2.connect(user="postgres", password="Deroco86*", host="localhost", port="5432")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    cur.execute("CREATE DATABASE pos_2026_db;")
    print("Database created successfully")
    
except psycopg2.errors.DuplicateDatabase:
    print("Database already exists")
except Exception as e:
    print(f"Error creating database: {e}")
finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()
