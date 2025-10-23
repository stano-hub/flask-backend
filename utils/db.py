import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# ==========================
# 🔌 Database Configuration
# ==========================
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in .env file")

# ==========================
# 🔄 Connection Pool Setup
# ==========================
try:
    connection_pool = pool.SimpleConnectionPool(
        minconn=1,
        maxconn=10,
        dsn=DATABASE_URL,
        sslmode="require"
    )

    if connection_pool:
        print("✅ PostgreSQL connection pool created successfully.")

except Exception as e:
    print("❌ Error creating PostgreSQL connection pool:", str(e))
    connection_pool = None


# ==========================
# 🧹 Cleanup Function
# ==========================
def close_all_connections():
    if connection_pool:
        connection_pool.closeall()
        print("🔒 All PostgreSQL connections closed.")
