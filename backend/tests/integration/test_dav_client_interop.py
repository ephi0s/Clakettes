"""Interoperability tests that drive the real ``caldav`` client against the server.

Each test talks to a throwaway ``uvicorn`` process backed by a freshly seeded
SQLite database, then asserts on what the ``icalendar`` parser reads back. The
point is to prove the CalDAV surface works for an actual client, so no test
here inspects raw HTTP bodies or XML.
"""

import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.dav import auth as dav_auth
from app.models.base import Base
from app.services.user_service import hash_password

caldav = pytest.importorskip("caldav")
icalendar = pytest.importorskip("icalendar")

BACKEND_DIR = Path(__file__).resolve().parents[2]
AGENDA_NAME = "Agenda"
FESTIVAL_NAME = "Interop Short Film Festival"
EVENT_TITLE = "Gala de inauguración del festival"
LONG_EVENT_TITLE = (
    "Proyección especial de clausura con coloquio, alfombra roja y entrega "
    "de premios del jurado internacional de la sección oficial"
)
EVENT_START = datetime(2026, 5, 1, 18, 30)


@dataclass
class InteropServer:
    """Coordinates of the temporary server and the data it was seeded with."""

    base_url: str
    principal_url: str
    token: str
    festival_name: str
    event_id: int
    long_event_id: int
    event_title: str
    long_event_title: str
    event_start: datetime
    event_end: datetime

    @property
    def event_uid(self) -> str:
        return f"event-{self.event_id}@clakettes"

    @property
    def long_event_uid(self) -> str:
        return f"event-{self.long_event_id}@clakettes"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_for_health(base_url: str, process: subprocess.Popen, log_path: Path, timeout: float = 30.0) -> None:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(
                f"uvicorn exited early with code {process.returncode}:\n{log_path.read_text(errors='replace')}"
            )
        try:
            with urllib.request.urlopen(f"{base_url}/health", timeout=2) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, OSError) as exc:
            last_error = exc
        time.sleep(0.25)
    raise RuntimeError(
        f"Server did not become ready within {timeout}s ({last_error}):\n{log_path.read_text(errors='replace')}"
    )


def _seed(database_url: str, token: str) -> dict:
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    try:
        user = models.User(
            username="interop",
            email="interop@example.com",
            password_hash=hash_password("InteropPass123!"),
            full_name="Interop User",
            is_active=True,
            dav_token_hash=dav_auth.hash_token(token),
        )
        session.add(user)
        festival = models.Festival(
            name=FESTIVAL_NAME,
            description="Festival used by the CalDAV interoperability test",
            is_active=True,
            show_in_calendar=True,
        )
        session.add(festival)
        session.commit()
        session.refresh(festival)

        main_event = models.Event(
            festival_id=festival.id,
            title=EVENT_TITLE,
            description="Opening night gala",
            event_type=models.EventType.GALA.value,
            start_date=EVENT_START,
            end_date=EVENT_START + timedelta(hours=2),
            location="Cine Ideal",
            is_active=True,
            visibility_scope=models.EventVisibilityScope.PUBLIC.value,
        )
        long_event = models.Event(
            festival_id=festival.id,
            title=LONG_EVENT_TITLE,
            event_type=models.EventType.SCREENING.value,
            start_date=EVENT_START + timedelta(days=1),
            end_date=EVENT_START + timedelta(days=1, hours=3),
            is_active=True,
            visibility_scope=models.EventVisibilityScope.PUBLIC.value,
        )
        session.add_all([main_event, long_event])
        session.commit()
        return {
            "event_id": main_event.id,
            "long_event_id": long_event.id,
        }
    finally:
        session.close()
        engine.dispose()


@pytest.fixture(scope="session")
def dav_server():
    workdir = Path(tempfile.mkdtemp(prefix="clakettes_dav_interop_"))
    db_path = workdir / "interop.db"
    rate_path = workdir / "rate_limits.db"
    log_path = workdir / "uvicorn.log"
    database_url = f"sqlite:///{db_path.as_posix()}"

    token = dav_auth.generate_token()
    ids = _seed(database_url, token)

    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"
    env = os.environ.copy()
    env.update(
        {
            "DATABASE_URL": database_url,
            "SECRET_KEY": "interop-secret-key-not-for-production",
            "APP_ENV": "development",
            "RATE_LIMITS_DB_PATH": str(rate_path),
            "TESTING": "true",
        }
    )

    info = InteropServer(
        base_url=base_url,
        principal_url=f"{base_url}/dav/{token}/",
        token=token,
        festival_name=FESTIVAL_NAME,
        event_id=ids["event_id"],
        long_event_id=ids["long_event_id"],
        event_title=EVENT_TITLE,
        long_event_title=LONG_EVENT_TITLE,
        event_start=EVENT_START.replace(tzinfo=timezone.utc),
        event_end=(EVENT_START + timedelta(hours=2)).replace(tzinfo=timezone.utc),
    )

    with open(log_path, "wb") as log_file:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--log-level",
                "warning",
            ],
            cwd=str(BACKEND_DIR),
            env=env,
            stdout=log_file,
            stderr=subprocess.STDOUT,
        )
    try:
        _wait_for_health(base_url, process, log_path)
        yield info
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)
        shutil.rmtree(workdir, ignore_errors=True)


@pytest.fixture
def dav_client(dav_server):
    client = caldav.DAVClient(url=dav_server.principal_url)
    try:
        yield client
    finally:
        client.close()


@pytest.mark.interop
def test_principal_exposes_agenda_and_festival_calendars(dav_client, dav_server):
    calendars = dav_client.principal().calendars()
    display_names = {calendar.get_display_name() for calendar in calendars}

    assert AGENDA_NAME in display_names
    assert dav_server.festival_name in display_names


@pytest.mark.interop
def test_calendar_events_parse_as_real_icalendar(dav_client, dav_server):
    calendar = dav_client.principal().calendar(name=AGENDA_NAME)
    events = calendar.events()

    components = {}
    for event in events:
        parsed = icalendar.Calendar.from_ical(event.get_data())
        for component in parsed.walk("VEVENT"):
            components[str(component["UID"])] = component

    assert dav_server.event_uid in components
    main = components[dav_server.event_uid]
    assert str(main["SUMMARY"]) == dav_server.event_title

    start = main.decoded("DTSTART")
    end = main.decoded("DTEND")
    assert isinstance(start, datetime)
    assert isinstance(end, datetime)
    assert start == dav_server.event_start
    assert end == dav_server.event_end

    assert dav_server.long_event_uid in components
    assert str(components[dav_server.long_event_uid]["SUMMARY"]) == dav_server.long_event_title


@pytest.mark.interop
def test_get_with_returned_etag_is_not_modified(dav_client, dav_server):
    calendar = dav_client.principal().calendar(name=AGENDA_NAME)

    resource_url = None
    for event in calendar.events():
        if str(event.url).endswith(f"/{dav_server.event_id}.ics"):
            resource_url = str(event.url)
            break
    assert resource_url is not None

    fresh = dav_client.request(resource_url, "GET")
    assert fresh.status == 200
    etag = fresh.headers.get("ETag")
    assert etag

    conditional = dav_client.request(resource_url, "GET", headers={"If-None-Match": etag})
    assert conditional.status == 304
    assert conditional.tree is None
