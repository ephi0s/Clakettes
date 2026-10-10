"""Tests for the shared agenda across festivals and its visibility settings."""

from datetime import datetime, timedelta

import pytest

from app.enums import EventVisibilityScope
from app.models.app_setting import AppSetting
from app.models.event import Event
from app.models.festival import Festival
from app.models.role import Role
from app.models.user_role import UserRole, UserRoleStatus
from app.models.user_festival import user_festival


BASE = datetime(2026, 3, 10, 18, 0, 0)


def _create_festival(db_session, name, show_in_calendar=True, is_active=True):
    festival = Festival(name=name, is_active=is_active, show_in_calendar=show_in_calendar)
    db_session.add(festival)
    db_session.commit()
    db_session.refresh(festival)
    return festival


def _create_event(db_session, festival, title, scope="public", start=BASE, is_active=True):
    event = Event(
        festival_id=festival.id,
        title=title,
        event_type="screening",
        start_date=start,
        visibility_scope=scope,
        is_active=is_active,
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    return event


def _titles(response):
    return {e["title"] for e in response.json()["events"]}


def _create_role(db_session, name="jury", hierarchy_level=2):
    role = Role(name=name, display_name=name.title(), hierarchy_level=hierarchy_level, is_active=True)
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role


def _event_payload(festival_id, title, **extra):
    return {
        "festival_id": festival_id,
        "title": title,
        "event_type": "screening",
        "start_date": BASE.isoformat(),
        **extra,
    }


class TestAgendaVisibility:
    """Tests for GET /api/calendar/agenda."""

    def test_agenda_empty_by_default(self, client):
        response = client.get("/api/calendar/agenda")
        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is True
        assert data["events"] == []

    def test_public_event_visible_anonymously(self, client, db_session):
        festival = _create_festival(db_session, "Sundance")
        _create_event(db_session, festival, "Opening")
        response = client.get("/api/calendar/agenda")
        assert response.status_code == 200
        assert _titles(response) == {"Opening"}

    def test_inactive_event_excluded(self, client, db_session):
        festival = _create_festival(db_session, "Sundance")
        _create_event(db_session, festival, "Draft", is_active=False)
        assert _titles(client.get("/api/calendar/agenda")) == set()

    def test_inactive_festival_excluded(self, client, db_session):
        festival = _create_festival(db_session, "Archived", is_active=False)
        _create_event(db_session, festival, "Old")
        assert _titles(client.get("/api/calendar/agenda")) == set()

    def test_festival_hidden_from_calendar_excluded(self, client, db_session):
        festival = _create_festival(db_session, "Hidden", show_in_calendar=False)
        _create_event(db_session, festival, "Secret fest")
        assert _titles(client.get("/api/calendar/agenda")) == set()

    def test_spans_all_visible_festivals(self, client, db_session):
        a = _create_festival(db_session, "Alpha")
        b = _create_festival(db_session, "Beta")
        _create_event(db_session, a, "Alpha night", start=BASE)
        _create_event(db_session, b, "Beta night", start=BASE + timedelta(days=1))
        response = client.get("/api/calendar/agenda")
        assert _titles(response) == {"Alpha night", "Beta night"}
        assert {f["name"] for f in response.json()["festivals"]} == {"Alpha", "Beta"}

    def test_date_range_filter(self, client, db_session):
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Day one", start=BASE)
        _create_event(db_session, festival, "Day nine", start=BASE + timedelta(days=8))
        response = client.get(
            "/api/calendar/agenda",
            params={
                "date_from": (BASE - timedelta(days=1)).isoformat(),
                "date_to": (BASE + timedelta(days=1)).isoformat(),
            },
        )
        assert _titles(response) == {"Day one"}

    def test_multiday_event_included_by_overlap(self, client, db_session):
        festival = _create_festival(db_session, "Alpha")
        event = Event(
            festival_id=festival.id,
            title="Marathon",
            event_type="screening",
            start_date=BASE,
            end_date=BASE + timedelta(days=5),
            visibility_scope="public",
            is_active=True,
        )
        db_session.add(event)
        db_session.commit()
        response = client.get(
            "/api/calendar/agenda",
            params={
                "date_from": (BASE + timedelta(days=3)).isoformat(),
                "date_to": (BASE + timedelta(days=4)).isoformat(),
            },
        )
        assert _titles(response) == {"Marathon"}

    def test_private_events_hidden_from_anonymous(self, client, db_session):
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Members only", scope=EventVisibilityScope.FESTIVAL_MEMBERS.value)
        _create_event(db_session, festival, "Public thing")
        response = client.get("/api/calendar/agenda")
        assert _titles(response) == {"Public thing"}

    def test_festival_members_see_their_event(self, client, db_session, auth_headers):
        headers, user = auth_headers
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Members only", scope=EventVisibilityScope.FESTIVAL_MEMBERS.value)
        db_session.execute(user_festival.insert().values(user_id=user.id, festival_id=festival.id))
        db_session.commit()
        assert _titles(client.get("/api/calendar/agenda", headers=headers)) == {"Members only"}

    def test_non_member_does_not_see_it(self, client, db_session, auth_headers):
        headers, user = auth_headers
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Members only", scope=EventVisibilityScope.FESTIVAL_MEMBERS.value)
        assert _titles(client.get("/api/calendar/agenda", headers=headers)) == set()

    def test_roles_scope_requires_matching_role(self, client, db_session, auth_headers):
        headers, user = auth_headers
        festival = _create_festival(db_session, "Alpha")
        role = _create_role(db_session, "jury")

        event = _create_event(db_session, festival, "Jury briefing", scope=EventVisibilityScope.ROLES.value)
        event.visibility_roles = [role]
        db_session.commit()

        # Without the role, the event stays hidden.
        assert _titles(client.get("/api/calendar/agenda", headers=headers)) == set()

        db_session.add(
            UserRole(
                user_id=user.id,
                role_id=role.id,
                festival_id=festival.id,
                status=UserRoleStatus.APPROVED.value,
            )
        )
        db_session.commit()
        assert _titles(client.get("/api/calendar/agenda", headers=headers)) == {"Jury briefing"}

    def test_pending_role_does_not_grant_access(self, client, db_session, auth_headers):
        headers, user = auth_headers
        festival = _create_festival(db_session, "Alpha")
        role = _create_role(db_session, "jury")

        event = _create_event(db_session, festival, "Jury briefing", scope=EventVisibilityScope.ROLES.value)
        event.visibility_roles = [role]
        db_session.add(UserRole(user_id=user.id, role_id=role.id, festival_id=festival.id, status="pending"))
        db_session.commit()

        assert _titles(client.get("/api/calendar/agenda", headers=headers)) == set()

    def test_roles_scope_without_selection_hides_event(self, client, db_session, auth_headers):
        headers, user = auth_headers
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Orphan briefing", scope=EventVisibilityScope.ROLES.value)
        assert _titles(client.get("/api/calendar/agenda", headers=headers)) == set()

    def test_global_role_grants_access(self, client, db_session, auth_headers):
        headers, user = auth_headers
        festival = _create_festival(db_session, "Alpha")
        role = _create_role(db_session, "producer", hierarchy_level=3)

        event = _create_event(db_session, festival, "Producer meeting", scope=EventVisibilityScope.ROLES.value)
        event.visibility_roles = [role]
        db_session.add(UserRole(user_id=user.id, role_id=role.id, festival_id=None, status=UserRoleStatus.ACTIVE.value))
        db_session.commit()

        assert _titles(client.get("/api/calendar/agenda", headers=headers)) == {"Producer meeting"}

    def test_attendees_only(self, client, db_session, auth_headers):
        headers, user = auth_headers
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Green room", scope=EventVisibilityScope.ATTENDEES_ONLY.value)
        from app.models.event import EventAttendee

        assert _titles(client.get("/api/calendar/agenda", headers=headers)) == set()
        db_session.add(EventAttendee(event_id=event.id, user_id=user.id, status="registered"))
        db_session.commit()
        assert _titles(client.get("/api/calendar/agenda", headers=headers)) == {"Green room"}

    def test_private_flag_marks_restricted_events(self, client, db_session, auth_headers):
        headers, user = auth_headers
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Members only", scope=EventVisibilityScope.FESTIVAL_MEMBERS.value)
        _create_event(db_session, festival, "Open")
        db_session.execute(user_festival.insert().values(user_id=user.id, festival_id=festival.id))
        db_session.commit()

        events = {e["title"]: e for e in client.get("/api/calendar/agenda", headers=headers).json()["events"]}
        assert events["Members only"]["is_private"] is True
        assert events["Open"]["is_private"] is False

    def test_agenda_includes_festival_name(self, client, db_session):
        festival = _create_festival(db_session, "Sitges")
        _create_event(db_session, festival, "Brigadoon")
        event = client.get("/api/calendar/agenda").json()["events"][0]
        assert event["festival_name"] == "Sitges"
        assert event["festival_id"] == festival.id


class TestCalendarDisabled:
    """The global switch hides the agenda entirely."""

    def test_disabled_returns_empty_but_flagged(self, client, db_session):
        db_session.add(AppSetting(key="calendar.enabled", value=False, value_type="boolean"))
        db_session.commit()
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Opening")

        response = client.get("/api/calendar/agenda")
        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is False
        assert data["events"] == []

    def test_public_settings_reports_flag(self, client, db_session):
        assert client.get("/api/calendar/settings").json() == {"calendar_enabled": True}

        db_session.add(AppSetting(key="calendar.enabled", value=False, value_type="boolean"))
        db_session.commit()
        assert client.get("/api/calendar/settings").json() == {"calendar_enabled": False}


class TestCalendarSettingsAdmin:
    """Tests for GET/PUT /api/calendar/admin/settings."""

    def test_requires_auth(self, client):
        assert client.get("/api/calendar/admin/settings").status_code == 401
        assert client.put("/api/calendar/admin/settings", json={"calendar_enabled": False}).status_code == 401

    def test_requires_admin(self, client, auth_headers):
        headers, _ = auth_headers
        assert client.get("/api/calendar/admin/settings", headers=headers).status_code == 403

    def test_admin_lists_all_festivals(self, client, db_session, admin_headers):
        headers, _ = admin_headers
        _create_festival(db_session, "Alpha")
        _create_festival(db_session, "Beta", show_in_calendar=False)
        response = client.get("/api/calendar/admin/settings", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["calendar_enabled"] is True
        flags = {f["name"]: f["show_in_calendar"] for f in data["festivals"]}
        assert flags == {"Alpha": True, "Beta": False}

    def test_admin_can_disable_calendar(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.put("/api/calendar/admin/settings", json={"calendar_enabled": False}, headers=headers)
        assert response.status_code == 200
        assert response.json()["calendar_enabled"] is False
        assert client.get("/api/calendar/settings").json() == {"calendar_enabled": False}

    def test_admin_can_select_visible_festivals(self, client, db_session, admin_headers):
        headers, _ = admin_headers
        alpha = _create_festival(db_session, "Alpha")
        beta = _create_festival(db_session, "Beta")

        response = client.put(
            "/api/calendar/admin/settings",
            json={"festival_ids": [alpha.id]},
            headers=headers,
        )
        assert response.status_code == 200
        flags = {f["name"]: f["show_in_calendar"] for f in response.json()["festivals"]}
        assert flags == {"Alpha": True, "Beta": False}

        # The hidden festival's events disappear from the agenda.
        _create_event(db_session, alpha, "Alpha night")
        _create_event(db_session, beta, "Beta night")
        assert _titles(client.get("/api/calendar/agenda")) == {"Alpha night"}

    def test_admin_can_restore_all_festivals(self, client, db_session, admin_headers):
        headers, _ = admin_headers
        beta = _create_festival(db_session, "Beta", show_in_calendar=False)
        alpha = _create_festival(db_session, "Alpha")
        response = client.put(
            "/api/calendar/admin/settings",
            json={"festival_ids": [alpha.id, beta.id]},
            headers=headers,
        )
        assert {f["show_in_calendar"] for f in response.json()["festivals"]} == {True}

    def test_admin_settings_reports_event_count(self, client, db_session, admin_headers):
        headers, _ = admin_headers
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "One")
        _create_event(db_session, festival, "Two")
        response = client.get("/api/calendar/admin/settings", headers=headers)
        assert response.json()["festivals"][0]["event_count"] == 2

    def test_omitted_fields_are_left_untouched(self, client, db_session, admin_headers):
        headers, _ = admin_headers
        _create_festival(db_session, "Beta", show_in_calendar=False)
        _create_festival(db_session, "Alpha")

        response = client.put("/api/calendar/admin/settings", json={"calendar_enabled": False}, headers=headers)
        flags = {f["name"]: f["show_in_calendar"] for f in response.json()["festivals"]}
        assert flags == {"Alpha": True, "Beta": False}


class TestAgendaIcsExport:
    """Tests for GET /api/calendar/agenda/export/ics."""

    def test_exports_events(self, client, db_session):
        festival = _create_festival(db_session, "Sitges")
        _create_event(db_session, festival, "Brigadoon")
        response = client.get("/api/calendar/agenda/export/ics")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/calendar")
        assert "BEGIN:VCALENDAR" in response.text
        assert "SUMMARY:Brigadoon" in response.text
        assert "END:VCALENDAR" in response.text

    def test_excludes_private_events_for_anonymous(self, client, db_session):
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Members only", scope=EventVisibilityScope.FESTIVAL_MEMBERS.value)
        assert "Members only" not in client.get("/api/calendar/agenda/export/ics").text


class TestEventVisibilityInput:
    """Festival admins set the scope when creating or editing an event."""

    def test_create_event_with_role_scope(self, client, db_session, admin_headers):
        headers, _ = admin_headers
        festival_id = client.post("/api/festivals/", json={"name": "Alpha"}, headers=headers).json()["id"]
        role = _create_role(db_session, "jury")

        response = client.post(
            f"/api/festivals/{festival_id}/events/",
            json=_event_payload(festival_id, "Jury briefing", visibility_scope="roles", visible_role_ids=[role.id]),
            headers=headers,
        )
        assert response.status_code == 201
        body = response.json()
        assert body["visibility_scope"] == "roles"
        assert body["visible_role_ids"] == [role.id]

    def test_create_event_defaults_to_public(self, client, admin_headers):
        headers, _ = admin_headers
        festival_id = client.post("/api/festivals/", json={"name": "Alpha"}, headers=headers).json()["id"]
        response = client.post(
            f"/api/festivals/{festival_id}/events/",
            json=_event_payload(festival_id, "Opening"),
            headers=headers,
        )
        assert response.status_code == 201
        body = response.json()
        assert body["visibility_scope"] == "public"
        assert body["visible_role_ids"] == []

    def test_create_event_rejects_unknown_scope(self, client, admin_headers):
        headers, _ = admin_headers
        festival_id = client.post("/api/festivals/", json={"name": "Alpha"}, headers=headers).json()["id"]
        response = client.post(
            f"/api/festivals/{festival_id}/events/",
            json=_event_payload(festival_id, "Opening", visibility_scope="nonsense"),
            headers=headers,
        )
        assert response.status_code == 422

    def test_update_event_scope_and_roles(self, client, db_session, admin_headers):
        headers, _ = admin_headers
        festival_id = client.post("/api/festivals/", json={"name": "Alpha"}, headers=headers).json()["id"]
        role = _create_role(db_session, "jury")
        event_id = client.post(
            f"/api/festivals/{festival_id}/events/",
            json=_event_payload(festival_id, "Opening"),
            headers=headers,
        ).json()["id"]

        response = client.put(
            f"/api/events/{event_id}",
            json={"visibility_scope": "roles", "visible_role_ids": [role.id]},
            headers=headers,
        )
        assert response.status_code == 200
        body = response.json()
        assert body["visibility_scope"] == "roles"
        assert body["visible_role_ids"] == [role.id]

    def test_update_event_clears_roles(self, client, db_session, admin_headers):
        headers, _ = admin_headers
        festival_id = client.post("/api/festivals/", json={"name": "Alpha"}, headers=headers).json()["id"]
        role = _create_role(db_session, "jury")
        event_id = client.post(
            f"/api/festivals/{festival_id}/events/",
            json=_event_payload(festival_id, "Opening", visible_role_ids=[role.id]),
            headers=headers,
        ).json()["id"]

        response = client.put(f"/api/events/{event_id}", json={"visible_role_ids": []}, headers=headers)
        assert response.status_code == 200
        assert response.json()["visible_role_ids"] == []

    def test_scoped_event_reaches_only_the_role_holders(self, client, db_session, admin_headers, create_user):
        from app.auth import create_session

        headers, _ = admin_headers
        festival_id = client.post("/api/festivals/", json={"name": "Alpha"}, headers=headers).json()["id"]
        role = _create_role(db_session, "jury")

        outsider, password = create_user(username="outsider", email="outsider@example.com")
        insider, _ = create_user(username="insider", email="insider@example.com")
        _, outsider_token, _ = create_session(db_session, outsider.id)
        _, insider_token, _ = create_session(db_session, insider.id)

        client.post(
            f"/api/festivals/{festival_id}/events/",
            json=_event_payload(
                festival_id,
                "Jury briefing",
                visibility_scope="roles",
                visible_role_ids=[role.id],
            ),
            headers=headers,
        )
        db_session.add(
            UserRole(
                user_id=insider.id,
                role_id=role.id,
                festival_id=festival_id,
                status=UserRoleStatus.ACTIVE.value,
            )
        )
        db_session.commit()

        insider_headers = {"Authorization": f"Bearer {insider_token}"}
        outsider_headers = {"Authorization": f"Bearer {outsider_token}"}
        assert _titles(client.get("/api/calendar/agenda", headers=insider_headers)) == {"Jury briefing"}
        assert _titles(client.get("/api/calendar/agenda", headers=outsider_headers)) == set()


class TestFestivalShowInCalendar:
    """The per-festival flag defaults to True and round-trips through the API."""

    def test_defaults_to_true(self, client, admin_headers):
        headers, _ = admin_headers
        response = client.post("/api/festivals/", json={"name": "Alpha"}, headers=headers)
        assert response.json()["show_in_calendar"] is True

    def test_update_flag(self, client, admin_headers):
        headers, _ = admin_headers
        festival_id = client.post("/api/festivals/", json={"name": "Alpha"}, headers=headers).json()["id"]
        response = client.put(f"/api/festivals/{festival_id}", json={"show_in_calendar": False}, headers=headers)
        assert response.status_code == 200
        assert response.json()["show_in_calendar"] is False


class TestIsVisibleTo:
    """Unit tests for the Python mirror of the SQL visibility rule."""

    def test_public_is_visible_to_nobody_and_everybody(self, db_session):
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        assert event.is_visible_to(None) is True

    @pytest.mark.parametrize("scope", ["festival_members", "roles", "attendees_only"])
    def test_private_scopes_hide_from_anonymous(self, db_session, scope):
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Secret", scope=scope)
        assert event.is_visible_to(None) is False


# ========================================================================
# ICS export conformance (RFC 5545 section 3.1)
# ========================================================================

MAX_OCTETS = 75
UTC_BASIC = "%Y%m%dT%H%M%SZ"
LONG_TITLE = "Sesión inaugural " + "áéíóúñ 🎬🍿 " * 20
NASTY_TITLE = "Party; Rock, Roll\\Back\nLate " + "áéíóú 🎬 " * 20
NASTY_ESCAPED = "Party\\; Rock\\, Roll\\\\Back\\nLate " + "áéíóú 🎬 " * 20


def _agenda_ics(client, db_session, festival, event, admin_headers):
    """ICS of the agenda download endpoint."""
    return client.get("/api/calendar/agenda/export/ics")


def _festival_ics(client, db_session, festival, event, admin_headers):
    """ICS of the per-festival export endpoint."""
    headers, _ = admin_headers
    return client.get(f"/api/festivals/{festival.id}/events/export/ics", headers=headers)


SURFACES = {"agenda": _agenda_ics, "festival": _festival_ics}


def _create_ics_event(db_session, festival, title="Opening", end=None, venue=None, description=None):
    """A public event carrying the given ICS-relevant fields."""
    event = _create_event(db_session, festival, title)
    event.end_date = end
    event.venue = venue
    event.short_description = description
    db_session.commit()
    db_session.refresh(event)
    return event


def _ics(client, db_session, admin_headers, surface, title="Opening", end=None, venue=None, description=None):
    """Render one event through the given builder and return the HTTP response."""
    festival = _create_festival(db_session, "Alpha")
    event = _create_ics_event(db_session, festival, title=title, end=end, venue=venue, description=description)
    response = SURFACES[surface](client, db_session, festival, event, admin_headers)
    assert response.status_code == 200
    return response


def _physical_lines(body):
    """Content lines of an ICS body exactly as they went on the wire."""
    assert body.endswith("\r\n"), "an iCalendar stream ends with CRLF"
    return body.split("\r\n")[:-1]


def unfold(body):
    """Logical content lines of an ICS body, with folded continuations rejoined."""
    lines: list[str] = []
    for physical in _physical_lines(body):
        if physical[:1] == " " and lines:
            lines[-1] += physical[1:]
        else:
            lines.append(physical)
    return lines


def _values(body, name):
    """Every unfolded value of property ``name`` in an ICS body."""
    prefix = f"{name}:"
    return [line[len(prefix) :] for line in unfold(body) if line.startswith(prefix)]


def _value(body, name):
    """The single unfolded value of property ``name`` in an ICS body."""
    values = _values(body, name)
    assert len(values) == 1, (name, values)
    return values[0]


def _unescape(value):
    """Reverse the ICS TEXT escaping of a property value."""
    out = []
    index = 0
    while index < len(value):
        char = value[index]
        if char == "\\" and index + 1 < len(value):
            out.append("\n" if value[index + 1] == "n" else value[index + 1])
            index += 2
            continue
        out.append(char)
        index += 1
    return "".join(out)


def _instant(value):
    """Parse an ICS UTC basic timestamp back into a datetime."""
    return datetime.strptime(value, UTC_BASIC)


def _blocks(body):
    """Every line of an ICS body reduced to its property name, in emission order."""
    return [line if line.startswith(("BEGIN:", "END:")) else line.split(":", 1)[0] for line in unfold(body)]


class TestExportIcsCompliance:
    """RFC 5545 conformance of the two remaining ICS builders."""

    @pytest.mark.parametrize("surface", sorted(SURFACES))
    def test_long_title_is_folded_and_unfolds_exactly(self, client, db_session, admin_headers, surface):
        body = _ics(client, db_session, admin_headers, surface, title=LONG_TITLE).text
        assert len(LONG_TITLE.encode("utf-8")) > MAX_OCTETS
        assert _value(body, "SUMMARY") == LONG_TITLE
        assert len(_physical_lines(body)) > len(unfold(body))

    @pytest.mark.parametrize("surface", sorted(SURFACES))
    def test_no_content_line_exceeds_75_octets(self, client, db_session, admin_headers, surface):
        body = _ics(
            client,
            db_session,
            admin_headers,
            surface,
            title=LONG_TITLE,
            venue="Sala " + "á" * 200,
            description="Descripción " + "🎬" * 120,
        ).text
        lengths = [len(line.encode("utf-8")) for line in _physical_lines(body)]
        assert max(lengths) <= MAX_OCTETS, sorted(lengths, reverse=True)[:3]
        assert max(lengths) >= MAX_OCTETS - 1

    @pytest.mark.parametrize("surface", sorted(SURFACES))
    def test_continuations_carry_exactly_one_leading_space(self, client, db_session, admin_headers, surface):
        body = _ics(client, db_session, admin_headers, surface, title=LONG_TITLE).text
        continuations = [line for line in _physical_lines(body) if line[:1] == " "]
        assert continuations
        assert len(_physical_lines(body)) == len(unfold(body)) + len(continuations)
        assert not any(line[:1] == " " for line in unfold(body))

    @pytest.mark.parametrize("surface", sorted(SURFACES))
    def test_multibyte_folding_never_splits_a_utf8_sequence(self, client, db_session, admin_headers, surface):
        title = "áéíóú " + "🎬🍿" * 60
        content = _ics(client, db_session, admin_headers, surface, title=title).content
        chunks = content.split(b"\r\n")[:-1]
        assert max(len(chunk) for chunk in chunks) <= MAX_OCTETS
        for chunk in chunks:
            chunk.decode("utf-8")
        assert _value(content.decode("utf-8"), "SUMMARY") == title

    @pytest.mark.parametrize("surface", sorted(SURFACES))
    def test_multibyte_title_round_trips_through_unfolding(self, client, db_session, admin_headers, surface):
        body = _ics(client, db_session, admin_headers, surface, title=LONG_TITLE).text
        assert _value(body, "SUMMARY") == LONG_TITLE
        assert _unescape(_value(body, "SUMMARY")) == LONG_TITLE

    @pytest.mark.parametrize("surface", sorted(SURFACES))
    def test_every_line_ends_crlf_without_a_trailing_blank_line(self, client, db_session, admin_headers, surface):
        content = _ics(
            client, db_session, admin_headers, surface, title=LONG_TITLE, description="Línea\ncon salto"
        ).content
        assert content.endswith(b"\r\n")
        assert not content.endswith(b"\r\n\r\n")
        assert b"\n" not in content.replace(b"\r\n", b"")
        assert b"\r" not in content.replace(b"\r\n", b"")
        lines = unfold(content.decode("utf-8"))
        assert lines[0] == "BEGIN:VCALENDAR"
        assert lines[-1] == "END:VCALENDAR"
        assert "" not in lines

    @pytest.mark.parametrize(
        "end",
        [None, BASE + timedelta(days=5), BASE, BASE - timedelta(hours=3), BASE + timedelta(seconds=1)],
        ids=["default", "multiday", "zero-length", "inverted", "minimal"],
    )
    @pytest.mark.parametrize("surface", sorted(SURFACES))
    def test_dtend_is_strictly_after_dtstart(self, client, db_session, admin_headers, surface, end):
        body = _ics(client, db_session, admin_headers, surface, end=end).text
        assert _instant(_value(body, "DTEND")) > _instant(_value(body, "DTSTART"))

    @pytest.mark.parametrize("surface", sorted(SURFACES))
    def test_multiday_event_keeps_its_exact_span(self, client, db_session, admin_headers, surface):
        body = _ics(client, db_session, admin_headers, surface, end=BASE + timedelta(days=5, hours=3)).text
        assert _value(body, "DTSTART") == "20260310T180000Z"
        assert _value(body, "DTEND") == "20260315T210000Z"

    @pytest.mark.parametrize("surface", sorted(SURFACES))
    def test_special_characters_are_escaped_and_round_trip(self, client, db_session, admin_headers, surface):
        body = _ics(client, db_session, admin_headers, surface, title=NASTY_TITLE).text
        summary = _value(body, "SUMMARY")
        assert summary == NASTY_ESCAPED
        assert _unescape(summary) == NASTY_TITLE

    @pytest.mark.parametrize("surface", sorted(SURFACES))
    def test_escaping_happens_before_folding(self, client, db_session, admin_headers, surface):
        title = NASTY_TITLE + "áéíóú 🎬 " * 20
        body = _ics(client, db_session, admin_headers, surface, title=title).text
        assert len(_physical_lines(body)) > len(unfold(body))
        assert _unescape(_value(body, "SUMMARY")) == title

    @pytest.mark.parametrize("surface", sorted(SURFACES))
    def test_a_leading_space_in_a_value_survives_folding(self, client, db_session, admin_headers, surface):
        title = " Leading space " + "é" * 100
        body = _ics(client, db_session, admin_headers, surface, title=title).text
        assert _value(body, "SUMMARY") == title
        assert len(_physical_lines(body)) > len(unfold(body))

    @pytest.mark.parametrize("surface", sorted(SURFACES))
    def test_stream_has_no_byte_order_mark(self, client, db_session, admin_headers, surface):
        content = _ics(client, db_session, admin_headers, surface, title="Acentuádo 🎬").content
        assert not content.startswith(b"\xef\xbb\xbf")
        assert content.startswith(b"BEGIN:VCALENDAR")

    def test_agenda_keeps_its_public_output_shape(self, client, db_session):
        festival = _create_festival(db_session, "Alpha")
        event = _create_ics_event(db_session, festival, title="Opening", venue="Sala 1", description="Charla")
        response = client.get("/api/calendar/agenda/export/ics")
        assert response.status_code == 200
        assert response.headers["content-disposition"] == "attachment; filename=agenda.ics"
        body = response.text
        assert unfold(body)[:4] == [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Clakettes//Agenda//ES",
            "X-WR-CALNAME:Clakettes",
        ]
        assert _value(body, "UID") == f"event-{event.id}@clakettes"
        assert _blocks(body) == [
            "BEGIN:VCALENDAR",
            "VERSION",
            "PRODID",
            "X-WR-CALNAME",
            "BEGIN:VEVENT",
            "UID",
            "DTSTAMP",
            "DTSTART",
            "DTEND",
            "SUMMARY",
            "LOCATION",
            "DESCRIPTION",
            "CATEGORIES",
            "X-APPLE-STRUCTURE-LOCATION",
            "END:VEVENT",
            "END:VCALENDAR",
        ]

    def test_festival_export_keeps_its_public_output_shape(self, client, db_session, admin_headers):
        festival = _create_festival(db_session, "Export Fest")
        event = _create_ics_event(db_session, festival, title="Opening", venue="Sala 1", description="Charla")
        response = _festival_ics(client, db_session, festival, event, admin_headers)
        assert response.status_code == 200
        assert response.headers["content-disposition"] == "attachment; filename=calendar.ics"
        body = response.text
        assert unfold(body)[:4] == [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Clakettes//Festival//ES",
            "X-WR-CALNAME:Export Fest",
        ]
        assert _value(body, "UID") == f"event-{event.id}@clakettes"
        assert _blocks(body) == [
            "BEGIN:VCALENDAR",
            "VERSION",
            "PRODID",
            "X-WR-CALNAME",
            "BEGIN:VEVENT",
            "UID",
            "DTSTAMP",
            "DTSTART",
            "DTEND",
            "SUMMARY",
            "LOCATION",
            "DESCRIPTION",
            "CATEGORIES",
            "END:VEVENT",
            "END:VCALENDAR",
        ]
