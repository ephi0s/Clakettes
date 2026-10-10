#!/usr/bin/env python3
"""
Export data from SQLite (development) to MariaDB (production)
Run: python export_sqlite_to_mariadb.py
"""

import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import sys


def _load_env_file(path=".env"):
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


_load_env_file()

# Load models to register them with Base
from app.database import Base  # noqa: E402
from app import models  # noqa: F401, E402

SQLITE_URL = "sqlite:///./clakettes.db"
MARIADB_URL = os.getenv("DATABASE_URL")

if not MARIADB_URL or "sqlite" in MARIADB_URL:
    print("ERROR: Set DATABASE_URL in .env to your MariaDB connection string")
    print("Example: mariadb+pymysql://user:pass@localhost:3306/clakettes_db")
    sys.exit(1)


def export_to_mariadb():
    print("Starting export from SQLite to MariaDB...")

    # Connect to both databases
    sqlite_engine = create_engine(SQLITE_URL)
    mariadb_engine = create_engine(MARIADB_URL)

    # Create all tables in MariaDB
    Base.metadata.create_all(bind=mariadb_engine)

    sqlite_session = sessionmaker(bind=sqlite_engine)()
    mariadb_session = sessionmaker(bind=mariadb_engine)()

    try:
        # Get all table names from SQLite
        inspector = inspect(sqlite_engine)
        tables = inspector.get_table_names()

        for table_name in tables:
            print(f"Exporting table: {table_name}")

            # Get data from SQLite
            result = sqlite_session.execute(f"SELECT * FROM {table_name}")
            rows = result.fetchall()
            columns = result.keys()

            if not rows:
                print(f"  No data in {table_name}")
                continue

            # Clear existing data in MariaDB table
            mariadb_session.execute(f"DELETE FROM {table_name}")

            # Insert data into MariaDB
            for row in rows:
                data = dict(zip(columns, row))
                columns_str = ", ".join(columns)
                placeholders = ", ".join([f":{col}" for col in columns])
                sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                mariadb_session.execute(sql, data)

            print(f"  Exported {len(rows)} rows")

        mariadb_session.commit()
        print("\nExport completed successfully!")

    except SQLAlchemyError as e:
        mariadb_session.rollback()
        print(f"ERROR: {e}")
        sys.exit(1)
    finally:
        sqlite_session.close()
        mariadb_session.close()


if __name__ == "__main__":
    export_to_mariadb()
