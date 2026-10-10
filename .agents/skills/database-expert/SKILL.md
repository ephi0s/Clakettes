---
name: database-expert
description: Expert guidance for Clakettes database layer. Covers dual SQLite (dev) / MariaDB (prod) setup, Alembic migrations, export/import scripts between environments, 30+ SQLAlchemy models with inheritance from BaseModel, model patterns (id, created_at, updated_at, relationships), enum types shared via app.enums, and migration gotchas between SQLite and MariaDB. Use when working with models, migrations, or data transfer.
metadata:
  model: models/gemini-3.1-pro-preview
  last_modified: Tue, 23 Jun 2026 01:43:00 GMT
---
# Database Expert

## Dual Database Setup

- **Dev**: SQLite (`sqlite:///./clakettes.db`) — zero config, `check_same_thread=False`, `StaticPool`
- **Prod**: MariaDB via `DATABASE_URL` env var — `pool_size=10`, `max_overflow=20`, `pool_pre_ping=True`, `pool_recycle=3600`
- `DATABASE_URL` set in `backend/.env` or passed as environment variable

## Session

Managed in `app/database.py`:
```python
engine = create_engine(settings.DATABASE_URL, **engine_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```
Dependency: `get_db()` — yields session, rolls back on exception, always closes.

## Models

30+ SQLAlchemy models in `backend/app/models/` (23 model files). Key model files:

| File | Notable Models |
|------|---------------|
| `festival.py` | Festival |
| `user.py` | User |
| `shortfilm.py` | ShortFilm |
| `message.py` | Message |
| `channel.py` | Channel, ChannelMember |
| `committee.py` | Committee, CommitteeMember |
| `event.py` | Event, EventTicketType, EventSeat, EventReservation, EventAttendee |
| `role.py` | Role, FestivalRole, RoleDependency, RoleConflict |
| `role_group.py` | RoleGroup, RoleGroupMembership |
| `role_delegation.py` | RoleDelegation |
| `role_transition.py` | RoleTransition |
| `registration.py` | RegistrationForm, RegistrationFormSection, RegistrationFormSectionRole/Tag, RegistrationFormLink, FestivalRegistration, RegistrationSectionSelection |
| `participant_tag.py` | ParticipantTag, FestivalParticipantTag |
| `user_role.py` | UserRole, UserParticipantTag |
| `user_alias.py` | UserAlias |
| `user_session.py` | UserSession |
| `user_key.py` | UserKey |
| `notification.py` | Notification |
| `award.py` | Award |
| `validation_rule.py` | ValidationRule, ValidationRuleGroup, validation_rule_group_rules |
| `location.py` | Location |

All models inherit from `BaseModel` (`app/models/base.py`):
```python
class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
```

Enums (RoleScope, UserRoleStatus, EventType, etc.) live in `app/enums.py` — shared across models, schemas, and services.

## Migrations

- `alembic upgrade head` from `backend/`
- Config: `backend/alembic.ini` — default `sqlite:///./clakettes.db`, override via `DATABASE_URL`
- Docker: `docker compose run --rm backend alembic upgrade head`
- Test migration: `start.bat --test-migration` — MariaDB + migrate + validate + cleanup

## Export/Import

- `export_sqlite_to_mariadb.py` — dev → prod
- `import_mariadb_to_sqlite.py` — prod → dev

## SQLite ↔ MariaDB Gotchas

| SQLite | MariaDB |
|--------|---------|
| `INTEGER PRIMARY KEY` | `INT AUTO_INCREMENT` |
| `TEXT` | `TEXT`/`VARCHAR` (prefer VARCHAR for indexed) |
| `DATETIME` stored as text | Native `DATETIME` |
| No ENUM | ENUM (use strings in SQLite) |
| `Boolean` as 0/1 | `BOOLEAN`/`TINYINT` |

## Seed Data

On first startup, `main.py` creates tables and seeds admin: username `admin`, password `setup`, role `admin`.
