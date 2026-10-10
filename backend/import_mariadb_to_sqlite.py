#!/usr/bin/env python3
"""
Import data from MariaDB (production) to SQLite (development)
Run: python import_mariadb_to_sqlite.py
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

SQLITE_URL = "sqlite:///./clakettes.db"
MARIADB_URL = os.getenv("DATABASE_URL")

if not MARIADB_URL or "sqlite" in MARIADB_URL:
    print("ERROR: Set DATABASE_URL in .env to your MariaDB connection string")
    print("Example: mariadb+pymysql://user:pass@localhost:3306/clakettes_db")
    sys.exit(1)


def import_to_sqlite():
    print("Starting import from MariaDB to SQLite...")

    # Connect to both databases
    mariadb_engine = create_engine(MARIADB_URL)
    sqlite_engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})

    mariadb_session = sessionmaker(bind=mariadb_engine)()
    sqlite_session = sessionmaker(bind=sqlite_engine)()

    try:
        # Get all table names from MariaDB
        inspector = inspect(mariadb_engine)
        tables = inspector.get_table_names()

        for table_name in tables:
            print(f"Importing table: {table_name}")

            # Get data from MariaDB
            result = mariadb_session.execute(f"SELECT * FROM {table_name}")
            rows = result.fetchall()
            columns = result.keys()

            if not rows:
                print(f"  No data in {table_name}")
                continue

            # Drop and recreate table in SQLite
            sqlite_session.execute(f"DROP TABLE IF EXISTS {table_name}")

            # Create table in SQLite based on MariaDB schema
            create_table_sql = _get_create_table_sql(mariadb_engine, table_name)
            # Adapt MariaDB SQL to SQLite
            create_table_sql = _adapt_to_sqlite(create_table_sql)
            sqlite_session.execute(create_table_sql)

            # Insert data into SQLite
            for row in rows:
                data = dict(zip(columns, row))
                columns_str = ", ".join(columns)
                placeholders = ", ".join([f":{col}" for col in columns])
                sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                sqlite_session.execute(sql, data)

            print(f"  Imported {len(rows)} rows")

        sqlite_session.commit()
        print("\nImport completed successfully!")

    except SQLAlchemyError as e:
        sqlite_session.rollback()
        print(f"ERROR: {e}")
        sys.exit(1)
    finally:
        mariadb_session.close()
        sqlite_session.close()


def _get_create_table_sql(engine, table_name):
    """Get CREATE TABLE statement from MariaDB"""
    result = engine.execute(f"SHOW CREATE TABLE {table_name}")
    row = result.fetchone()
    return row[1] if row else ""


def _adapt_to_sqlite(sql):
    """Convert MariaDB CREATE TABLE to SQLite-compatible syntax"""
    # Remove MariaDB-specific syntax
    replacements = [
        ("AUTO_INCREMENT", "AUTOINCREMENT"),
        ("INT(", "INTEGER("),
        ("BIGINT(", "INTEGER("),
        ("DATETIME", "TEXT"),
        ("TIMESTAMP", "TEXT"),
        ("VARCHAR", "TEXT"),
        ("ENGINE=InnoDB", ""),
        ("DEFAULT CURRENT_TIMESTAMP", "DEFAULT CURRENT_TIMESTAMP"),
        ("ON UPDATE CURRENT_TIMESTAMP", ""),
        ("CHARSET=utf8mb4", ""),
        ("COLLATE=utf8mb4_unicode_ci", ""),
    ]
    for old, new in replacements:
        sql = sql.replace(old, new)
    return sql


if __name__ == "__main__":
    import_to_sqlite()
