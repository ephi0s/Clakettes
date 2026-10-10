"""Migrate data from SQLite development database to MariaDB production.

Usage:
    cd backend
    python -m scripts.migrate_to_production
    python -m scripts.migrate_to_production --source clakettes.db --target "mariadb+pymysql://user:pass@host:3306/db"

Requires the .env file with DATABASE_URL set for production, or pass --target explicitly.
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session
from app.config import settings
from app.models.base import Base
from app.models.user_festival import user_festival


def migrate(source_path: str, target_url: str):
    """Copy all data from SQLite source to MariaDB target."""
    source_engine = create_engine(f"sqlite:///{source_path}")
    target_engine = create_engine(target_url)

    print(f"Source: {source_path}")
    print(f"Target: {target_url}")

    Base.metadata.create_all(bind=target_engine)

    source_inspect = inspect(source_engine)
    tables = [t for t in Base.metadata.tables.keys() if t != "alembic_version"]
    print(f"Tables to migrate: {tables}")

    with Session(source_engine) as src_db, Session(target_engine) as tgt_db:
        table_order = ["users", "festivals", "shortfilms", "messages"]
        assoc_table = user_festival

        for table_name in table_order:
            if table_name not in source_inspect.get_table_names():
                print(f"  Skipping {table_name} (not in source)")
                continue

            model = Base.metadata.tables[table_name]
            rows = src_db.execute(model.select()).fetchall()
            if not rows:
                print(f"  {table_name}: 0 rows")
                continue

            # Clear target table
            tgt_db.execute(model.delete())
            tgt_db.commit()

            for row in rows:
                row_dict = dict(row._mapping)
                tgt_db.execute(model.insert().values(**row_dict))
            tgt_db.commit()
            print(f"  {table_name}: {len(rows)} rows migrated")

        # Migrate association table
        if "user_festival" in source_inspect.get_table_names():
            rows = src_db.execute(assoc_table.select()).fetchall()
            tgt_db.execute(assoc_table.delete())
            tgt_db.commit()
            for row in rows:
                tgt_db.execute(assoc_table.insert().values(**dict(row._mapping)))
            tgt_db.commit()
            print(f"  user_festival: {len(rows)} rows migrated")

    print("\nMigration complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate SQLite dev data to MariaDB production")
    parser.add_argument("--source", default="clakettes.db", help="Source SQLite database path")
    parser.add_argument("--target", default=None, help="Target MariaDB URL (defaults to DATABASE_URL from .env)")
    args = parser.parse_args()

    target = args.target or settings.DATABASE_URL
    if "sqlite" in target:
        print("ERROR: Target appears to be SQLite. Set DATABASE_URL in .env or pass --target with a MariaDB URL.")
        sys.exit(1)

    migrate(args.source, target)
