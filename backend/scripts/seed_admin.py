"""Seed the database with an admin user and optional sample data.

Usage:
    cd backend
    python -m scripts.seed_admin
    python -m scripts.seed_admin --with-sample-data
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.festival import Festival
from app.models.shortfilm import ShortFilm
from app.services.user_service import hash_password


ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@clakettes.com"
ADMIN_PASSWORD = "setup"
ADMIN_ROLE = "admin"


def seed_admin():
    """Create the admin user if it doesn't exist."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == ADMIN_USERNAME).first()
        if existing:
            print(f"Admin user '{ADMIN_USERNAME}' already exists (id={existing.id})")
            return existing

        admin = User(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password_hash=hash_password(ADMIN_PASSWORD),
            full_name="Administrator",
            role=ADMIN_ROLE,
            bio="Platform administrator for Clakettes",
            is_active=True,
            is_public=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"Admin user created: {ADMIN_USERNAME} / {ADMIN_PASSWORD} (id={admin.id})")
        return admin
    finally:
        db.close()


def seed_sample_data(admin_user):
    """Create sample festivals, users, and short films for testing."""
    db = SessionLocal()
    try:
        if db.query(Festival).count() > 0:
            print("Sample data already exists, skipping.")
            return

        festivals = [
            Festival(
                name="Festival de Cine de Donostia",
                description="San Sebastián International Film Festival",
                location="San Sebastián, España",
                latitude=43.3183,
                longitude=-1.9812,
                is_active=True,
                website="https://www.sansebastianfestival.com",
            ),  # noqa: E501
            Festival(
                name="Cannes Shorts",
                description="Short film section of the Festival de Cannes",
                location="Cannes, Francia",
                latitude=43.5528,
                longitude=7.0174,
                is_active=True,
                website="https://www.festival-cannes.com",
            ),  # noqa: E501
            Festival(
                name="Venice Days",
                description="Independent sidebar of the Venice Film Festival",
                location="Venecia, Italia",
                latitude=45.4408,
                longitude=12.3155,
                is_active=True,
            ),  # noqa: E501
            Festival(
                name="Berlinale Shorts",
                description="Short film competition at the Berlin International Film Festival",
                location="Berlín, Alemania",
                latitude=52.5200,
                longitude=13.4050,
                is_active=False,
            ),  # noqa: E501
            Festival(
                name="Cortometrajes Latinos",
                description="Latin American short film festival",
                location="Buenos Aires, Argentina",
                latitude=-34.6037,
                longitude=-58.3816,
                is_active=True,
            ),  # noqa: E501
        ]
        db.add_all(festivals)
        db.commit()

        sample_users = [
            User(
                username="maria_director",
                email="maria@example.com",
                password_hash=hash_password("Password1!"),
                full_name="María García",
                role="director",
                bio="Directora de cine independiente",
                is_public=True,
                latitude=40.4168,
                longitude=-3.7038,
            ),  # noqa: E501
            User(
                username="carlos_editor",
                email="carlos@example.com",
                password_hash=hash_password("Password1!"),
                full_name="Carlos López",
                role="editor",
                bio="Editor de vídeo y post-producción",
                is_public=True,
                latitude=41.3874,
                longitude=2.1686,
            ),  # noqa: E501
            User(
                username="ana_screenwriter",
                email="ana@example.com",
                password_hash=hash_password("Password1!"),
                full_name="Ana Martínez",
                role="screenwriter",
                bio="Guionista de cortometrajes",
                is_public=True,
                latitude=37.3891,
                longitude=-5.9845,
            ),  # noqa: E501
        ]
        db.add_all(sample_users)
        db.commit()

        db_admin = db.query(User).filter(User.username == ADMIN_USERNAME).first()
        db_maría = db.query(User).filter(User.username == "maria_director").first()
        db_carlos = db.query(User).filter(User.username == "carlos_editor").first()

        films = [
            ShortFilm(
                title="El Último Amanecer",
                description="Cortometraje sobre la memoria histórica",
                duration=15,
                user_id=db_maría.id,
                festival_id=festivals[0].id,
                is_public=True,
                tags="drama,histórico,memoria",
            ),  # noqa: E501
            ShortFilm(
                title="Luces de Neón",
                description="Thriller urbano en blanco y negro",
                duration=22,
                user_id=db_maría.id,
                is_public=True,
                tags="thriller,urbano,bn",
            ),  # noqa: E501
            ShortFilm(
                title="Despertar",
                description="Pieza experimental sobre el fluir del tiempo",
                duration=8,
                user_id=db_carlos.id,
                festival_id=festivals[1].id,
                is_public=True,
                tags="experimental,tiempo,artístico",
            ),  # noqa: E501
            ShortFilm(
                title="Café para Dos",
                description="Comedia romántica ambientada en un café de Madrid",
                duration=12,
                user_id=db_carlos.id,
                is_public=True,
                tags="comedia,romántico,madrid",
            ),  # noqa: E501
            ShortFilm(
                title="Raíces",
                description="Documental sobre agricultura urbana",
                duration=30,
                user_id=db_admin.id,
                is_public=True,
                tags="documental,agricultura,urbano",
            ),  # noqa: E501
        ]
        db.add_all(films)
        db.commit()
        print(f"Sample data created: {len(festivals)} festivals, {len(sample_users)} users, {len(films)} short films")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed admin user and sample data")
    parser.add_argument(
        "--with-sample-data", action="store_true", help="Also create sample festivals, users, and films"
    )  # noqa: E501
    args = parser.parse_args()

    admin = seed_admin()
    if args.with_sample_data and admin:
        seed_sample_data(admin)
