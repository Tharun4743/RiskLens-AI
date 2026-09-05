"""Standalone CLI script to initialize database tables and seed synthetic demo data.
Safe for production deployment: idempotent, checks if data already exists, never duplicates.
Usage:
    python scripts/seed_demo_data.py
"""
import os
import sys

# Ensure repository root is in python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT_DIR, ".env"))

from src.database.database import init_db, check_db_connection
from src.database.seed_data import seed_database_if_empty

def main():
    print("==================================================")
    print("RiskLens AI - Database Initialization & Seeding")
    print("==================================================")
    
    # 1. Verify connection
    conn_info = check_db_connection()
    print(f"Database dialect: {conn_info.get('dialect', 'unknown')}")
    print(f"PostgreSQL mode: {conn_info.get('is_postgres', False)}")
    print(f"Connection status: {conn_info.get('status', 'unknown')}")
    
    if conn_info.get("status") != "connected":
        print(f"ERROR: Cannot connect to database: {conn_info.get('error')}")
        sys.exit(1)
        
    # 2. Initialize schema
    print("\n[1/2] Verifying / Creating database schema...")
    init_db()
    print("Schema initialized successfully.")
    
    # 3. Seed demo data
    print("\n[2/2] Checking and seeding synthetic demo data...")
    seed_database_if_empty()
    
    print("\nDatabase initialization complete!")

if __name__ == "__main__":
    main()
