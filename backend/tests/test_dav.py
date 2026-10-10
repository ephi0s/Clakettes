"""Tests for the read-only CalDAV server and the token API that feeds it."""

import asyncio
import base64
from datetime import datetime, timedelta
from inspect import signature
import os
import re
import xml.etree.ElementTree as ET

import pytest
from starlette.requests import Request
from starlette.responses import Response

from app.dav.auth import generate_token, hash_token, principal_to_user_id
from app.dav.constants import (
    AGENDA_COLLECTION,
    DAV_ALLOW,
    DAV_COMPLIANCE,
    DAV_MAX_EVENTS,
    FESTIVAL_PREFIX,
    SYNC_TOKEN_PREFIX,
)
from app.dav.xmlbuild import q
from app.config import settings
from app.enums import EventVisibilityScope, UserRoleStatus
from app.main import DAV_PREFIX, RateLimitMiddleware
from app.models.app_setting import AppSetting
from app.models.event import Event, EventAttendee
from app.models.festival import Festival
from app.models.role import Role
from app.models.user import User
from app.models.user_festival import user_festival
from app.models.user_role import UserRole
from app.routers.dav import WRITE_METHODS


BASE = datetime(2026, 3, 10, 18, 0, 0)
UTC_BASIC = "%Y%m%dT%H%M%SZ"
NS_DECL = 'xmlns:D="DAV:" xmlns:C="urn:ietf:params:xml:ns:caldav"'
READ_METHODS = {"OPTIONS", "GET", "HEAD", "PROPFIND", "REPORT"}


def _create_festival(db_session, name, show_in_calendar=True, is_active=True):
    festival = Festival(name=name, is_active=is_active, show_in_calendar=show_in_calendar)
    db_session.add(festival)
    db_session.commit()
    db_session.refresh(festival)
    return festival


def _create_event(db_session, festival, title, scope="public", start=BASE, end=None, is_active=True):
    event = Event(
        festival_id=festival.id,
        title=title,
        event_type="screening",
        start_date=start,
        end_date=end,
        visibility_scope=scope,
        is_active=is_active,
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    return event


def _titles(body):
    """Set of SUMMARY values in an ICS body."""
    return {line[len("SUMMARY:") :] for line in body.split("\r\n") if line.startswith("SUMMARY:")}


def _uids(body):
    """Set of UID values in an ICS body."""
    return {line[len("UID:") :] for line in body.split("\r\n") if line.startswith("UID:")}


def _calendar_titles(multistatus_body):
    """SUMMARY values of every calendar-data element inside a multistatus body."""
    root = ET.fromstring(multistatus_body.encode("utf-8"))
    titles = set()
    for element in root.iter(q("C", "calendar-data")):
        titles |= _titles(element.text or "")
    return titles


def _create_role(db_session, name="jury", hierarchy_level=2):
    role = Role(name=name, display_name=name.title(), hierarchy_level=hierarchy_level, is_active=True)
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role


def _subscriber(db_session, create_user, username="subscriber"):
    """A user holding an active DAV token, with the plaintext returned."""
    user, _ = create_user(username=username, email=f"{username}@example.com")
    return user, _attach_token(db_session, user)


def _attach_token(db_session, user):
    """Store a fresh token hash for ``user`` and return the plaintext."""
    raw = generate_token()
    user.dav_token_hash = hash_token(raw)
    db_session.commit()
    return raw


def _basic(raw, password=""):
    """HTTP Basic header whose user name is the DAV token."""
    encoded = base64.b64encode(f"{raw}:{password}".encode()).decode()
    return {"Authorization": f"Basic {encoded}"}


def _bearer(raw):
    return {"Authorization": f"Bearer {raw}"}


def _home(token):
    return f"/dav/{token}/calendars/"


def _collection(token, name):
    return f"/dav/{token}/calendars/{name}/"


def _resource(token, name, event_id):
    return f"/dav/{token}/calendars/{name}/{event_id}.ics"


def _feed(token, name):
    return f"/dav/{token}/calendars/{name}.ics"


def _dav(client, method, url, body=None, depth=None):
    """Send a DAV request, adding Depth and the XML content type when needed."""
    headers = {}
    if depth is not None:
        headers["Depth"] = depth
    if body is not None:
        headers["Content-Type"] = "application/xml"
    return client.request(method, url, content=body, headers=headers)


def _propfind(client, url, depth=0, body=None):
    return _dav(client, "PROPFIND", url, body=body, depth=str(depth))


def _report(client, url, body, depth=1):
    return _dav(client, "REPORT", url, body=body, depth=str(depth))


def _xml(root, inner=""):
    return f'<?xml version="1.0" encoding="utf-8"?><{root} {NS_DECL}>{inner}</{root}>'


def _propfind_body(inner):
    return _xml("D:propfind", inner)


def _propfind_props(*props):
    """A PROPFIND body naming the given property elements."""
    return _xml("D:propfind", f"<D:prop>{''.join(props)}</D:prop>")


def _query_body(inner=""):
    props = "<D:getetag/><C:calendar-data/>"
    return _xml("C:calendar-query", f"<D:prop>{props}</D:prop>{inner}")


def _multiget_body(hrefs):
    props = "<D:getetag/><C:calendar-data/>"
    links = "".join(f"<D:href>{href}</D:href>" for href in hrefs)
    return _xml("C:calendar-multiget", f"<D:prop>{props}</D:prop>{links}")


def _sync_body(token=None, level="1"):
    props = "<D:getetag/><C:calendar-data/>"
    given = f"<D:sync-token>{token}</D:sync-token>" if token else ""
    return _xml("D:sync-collection", f"<D:sync-level>{level}</D:sync-level>{given}<D:prop>{props}</D:prop>")


def _time_range(start, end):
    attrs = f'start="{start.strftime(UTC_BASIC)}" end="{end.strftime(UTC_BASIC)}"'
    return (
        f'<C:filter><C:comp-filter name="VCALENDAR"><C:comp-filter name="VEVENT"><C:time-range {attrs}/>'
        "</C:comp-filter></C:comp-filter></C:filter>"
    )


def _responses(body):
    """Parse a multistatus body into its ``<D:response>`` children."""
    root = ET.fromstring(body.encode("utf-8"))
    assert root.tag == q("D", "multistatus"), root.tag
    return list(root)


def _hrefs(body):
    return [(element.text or "") for element in ET.fromstring(body.encode("utf-8")).iter(q("D", "href"))]


def _responses_for(body):
    return [(response.find(q("D", "href")).text or "") for response in _responses(body)]


def _event_hrefs(body):
    return sorted(href for href in _responses_for(body) if href.endswith(".ics"))


def _response_for(body, suffix):
    for response in _responses(body):
        href = response.find(q("D", "href"))
        if href is not None and (href.text or "").endswith(suffix):
            return response
    return None


def _propstat(response, status_prefix="HTTP/1.1 200"):
    for propstat in response.findall(q("D", "propstat")):
        status = propstat.find(q("D", "status"))
        if status is not None and (status.text or "").startswith(status_prefix):
            return propstat.find(q("D", "prop"))
    return None


def _prop(response, qname, status_prefix="HTTP/1.1 200"):
    prop = _propstat(response, status_prefix)
    return None if prop is None else prop.find(qname)


def _prop_text(response, qname, status_prefix="HTTP/1.1 200"):
    element = _prop(response, qname, status_prefix)
    return None if element is None else (element.text or "")


def _link(response, qname):
    element = _prop(response, qname)
    href = None if element is None else element.find(q("D", "href"))
    return None if href is None else (href.text or "")


def _prop_names(response, status_prefix="HTTP/1.1 200"):
    prop = _propstat(response, status_prefix)
    return [] if prop is None else [element.tag for element in prop]


def _sync_token(body):
    for response in _responses(body):
        element = response.find(q("D", "sync-token"))
        if element is not None:
            return element.text
    return None


def _count_events(db_session):
    return db_session.query(Event).count()


class TestDavAuth:
    """Tests for the token and Basic/Bearer credentials guarding /dav."""

    def test_root_propfind_without_credential_is_challenged(self, client):
        response = client.request("PROPFIND", "/dav/", headers={"Depth": "0"})
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == 'Basic realm="Clakettes"'

    def test_root_propfind_with_a_bad_token_is_challenged(self, client):
        response = client.request("PROPFIND", "/dav/whatever", headers=_bearer("nope"))
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == 'Basic realm="Clakettes"'

    def test_unknown_token_in_the_principal_path_is_rejected(self, client):
        response = client.get(_feed("nosuchdavtoken", AGENDA_COLLECTION))
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == 'Basic realm="Clakettes"'

    def test_freshly_generated_token_is_rejected(self, client, create_user, db_session):
        user, _ = create_user()
        _attach_token(db_session, user)
        response = client.get(_feed(generate_token(), AGENDA_COLLECTION))
        assert response.status_code == 401

    def test_user_id_principal_without_authorization_is_rejected(self, client, create_user, db_session):
        user, raw = _subscriber(db_session, create_user)
        response = client.get(_feed(f"u{user.id}", AGENDA_COLLECTION))
        assert response.status_code == 401
        assert raw not in response.text

    def test_user_id_principal_with_basic_token_authenticates(self, client, create_user, db_session):
        user, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Opening")
        response = client.get(_feed(f"u{user.id}", AGENDA_COLLECTION), headers=_basic(raw))
        assert response.status_code == 200
        assert _titles(response.text) == {"Opening"}

    def test_user_id_principal_with_bearer_token_authenticates(self, client, create_user, db_session):
        user, raw = _subscriber(db_session, create_user)
        response = client.get(_feed(f"u{user.id}", AGENDA_COLLECTION), headers=_bearer(raw))
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/calendar")

    def test_basic_password_is_ignored(self, client, create_user, db_session):
        user, raw = _subscriber(db_session, create_user)
        response = client.get(_feed(f"u{user.id}", AGENDA_COLLECTION), headers=_basic(raw, "ignored"))
        assert response.status_code == 200

    def test_token_of_another_user_cannot_use_this_principal(self, client, create_user, db_session):
        owner, raw = _subscriber(db_session, create_user, username="owner")
        other, _ = create_user(username="other", email="other@example.com")
        response = client.get(_feed(f"u{other.id}", AGENDA_COLLECTION), headers=_basic(raw))
        assert response.status_code == 401
        assert owner.id != other.id

    def test_inactive_user_token_is_rejected(self, client, create_user, db_session):
        user, raw = _subscriber(db_session, create_user)
        user.is_active = False
        db_session.commit()
        assert client.get(_feed(raw, AGENDA_COLLECTION)).status_code == 401

    def test_inactive_user_id_principal_is_rejected(self, client, create_user, db_session):
        user, raw = _subscriber(db_session, create_user)
        user.is_active = False
        db_session.commit()
        assert client.get(_feed(f"u{user.id}", AGENDA_COLLECTION), headers=_basic(raw)).status_code == 401

    def test_hash_token_is_a_stable_sha256(self):
        assert hash_token("abc") == hash_token("abc")
        assert hash_token("abc") != hash_token("abd")
        assert hash_token("") == ""
        assert len(hash_token("abc")) == 64
        assert re.fullmatch(r"[0-9a-f]{64}", hash_token(generate_token()))

    def test_generated_token_is_url_safe_and_never_a_principal(self):
        tokens = [generate_token() for _ in range(25)]
        assert len(set(tokens)) == 25
        for token in tokens:
            assert re.fullmatch(r"[A-Za-z0-9_-]{43}", token), token
            assert principal_to_user_id(token) is None
            assert re.fullmatch(r"u\d+", token) is None


class TestDavOptions:
    """Tests for OPTIONS advertisement of the DAV compliance classes."""

    def test_root_options_needs_no_credential(self, client):
        response = client.options("/dav/")
        assert response.status_code == 200
        assert response.headers["dav"] == DAV_COMPLIANCE
        assert "calendar-access" in response.headers["dav"]
        assert "3" in response.headers["dav"]
        assert "extended-mkcol" in response.headers["dav"]

    def test_root_options_advertises_the_read_only_method_set(self, client):
        response = client.options("/dav/")
        assert set(response.headers["allow"].split(", ")) == READ_METHODS
        assert response.headers["ms-author-via"] == "DAV"
        assert response.content == b""

    def test_collection_options_repeats_the_advertisement(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        response = client.options(_collection(raw, AGENDA_COLLECTION))
        assert response.status_code == 200
        assert response.headers["dav"] == DAV_COMPLIANCE
        assert set(response.headers["allow"].split(", ")) == READ_METHODS

    def test_options_ignores_an_unknown_principal(self, client):
        response = client.options(_collection("not-a-real-token", "festival-999"))
        assert response.status_code == 200
        assert "calendar-access" in response.headers["dav"]


class TestDavPropfind:
    """Tests for PROPFIND over principals, calendar homes, collections and resources."""

    def test_collection_depth_zero_returns_one_response(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Opening")
        response = _propfind(client, _collection(raw, AGENDA_COLLECTION), depth=0)
        assert response.status_code == 207
        assert response.headers["content-type"].startswith("application/xml")
        assert len(_responses(response.text)) == 1

    def test_collection_properties_at_depth_zero(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        response = _propfind(client, _collection(raw, AGENDA_COLLECTION), depth=0)
        collection = _responses(response.text)[0]
        assert collection.find(q("D", "href")).text == _collection(raw, AGENDA_COLLECTION)
        resourcetype = _prop(collection, q("D", "resourcetype"))
        assert resourcetype.find(q("D", "collection")) is not None
        assert resourcetype.find(q("C", "calendar")) is not None
        assert _prop_text(collection, q("D", "displayname")) == "Agenda"
        assert _prop_text(collection, q("D", "getetag")).startswith('"')
        assert _prop_text(collection, q("D", "sync-token")).startswith(SYNC_TOKEN_PREFIX)
        comps = _prop(collection, q("C", "supported-calendar-component-set"))
        assert comps.find(q("C", "comp")).get("name") == "VEVENT"

    def test_collection_depth_one_lists_every_event(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        first = _create_event(db_session, festival, "Opening")
        second = _create_event(db_session, festival, "Brigadoon", start=BASE + timedelta(days=1))
        response = _propfind(client, _collection(raw, AGENDA_COLLECTION), depth=1)
        assert response.status_code == 207
        assert _event_hrefs(response.text) == [
            _resource(raw, AGENDA_COLLECTION, first.id),
            _resource(raw, AGENDA_COLLECTION, second.id),
        ]

    def test_resource_properties_at_depth_zero(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        response = _propfind(client, _resource(raw, AGENDA_COLLECTION, event.id), depth=0)
        assert response.status_code == 207
        resource = _responses(response.text)[0]
        assert _prop(resource, q("D", "resourcetype")) is not None
        assert len(_prop(resource, q("D", "resourcetype"))) == 0
        assert _prop_text(resource, q("D", "getetag")).startswith('W/"')
        assert _prop_text(resource, q("D", "getcontenttype")) == "text/calendar; charset=utf-8; component=vevent"
        assert int(_prop_text(resource, q("D", "getcontentlength"))) > 0
        assert "SUMMARY:Opening" in _prop_text(resource, q("C", "calendar-data"))

    def test_unknown_collection_is_not_found(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        response = _propfind(client, _collection(raw, "nonsense"), depth=0)
        assert response.status_code == 404

    def test_visible_festival_collection_is_listed(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Opening")
        name = f"{FESTIVAL_PREFIX}{festival.id}"
        response = _propfind(client, _collection(raw, name), depth=1)
        assert response.status_code == 207
        assert _responses_for(response.text)[0] == _collection(raw, name)
        assert len(_event_hrefs(response.text)) == 1
        collection = _responses(response.text)[0]
        assert _prop_text(collection, q("D", "displayname")) == "Alpha"

    def test_hidden_festival_collection_is_not_found(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Hidden", show_in_calendar=False)
        response = _propfind(client, _collection(raw, f"{FESTIVAL_PREFIX}{festival.id}"), depth=0)
        assert response.status_code == 404

    def test_missing_festival_collection_is_not_found(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        response = _propfind(client, _collection(raw, f"{FESTIVAL_PREFIX}4242"), depth=0)
        assert response.status_code == 404

    def test_principal_exposes_itself_and_its_home(self, client, create_user, db_session):
        user, raw = _subscriber(db_session, create_user)
        response = _propfind(client, f"/dav/{raw}/", depth=0)
        assert response.status_code == 207
        principal = _responses(response.text)[0]
        assert principal.find(q("D", "href")).text == f"/dav/{raw}/"
        assert _link(principal, q("D", "current-user-principal")) == f"/dav/{raw}/"
        assert _link(principal, q("C", "calendar-home-set")) == _home(raw)
        assert _prop_text(principal, q("D", "displayname")) == "Test User"

    def test_calendar_home_depth_one_lists_collections_only(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Opening")
        response = _propfind(client, _home(raw), depth=1)
        assert response.status_code == 207
        assert _responses_for(response.text) == [
            _home(raw),
            _collection(raw, AGENDA_COLLECTION),
            _collection(raw, f"{FESTIVAL_PREFIX}{festival.id}"),
        ]
        assert not [href for href in _responses_for(response.text) if href.endswith(".ics")]

    def test_calendar_home_depth_zero_lists_nothing_else(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        _create_festival(db_session, "Alpha")
        response = _propfind(client, _home(raw), depth=0)
        assert _responses_for(response.text) == [_home(raw)]

    def test_propname_reports_every_property_without_values(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        response = _propfind(client, _collection(raw, AGENDA_COLLECTION), depth=0, body=_propfind_body("<D:propname/>"))
        assert response.status_code == 207
        prop = _propstat(_responses(response.text)[0])
        names = [element.tag for element in prop]
        assert {
            q("D", "displayname"),
            q("D", "getetag"),
            q("D", "sync-token"),
            q("D", "getcontenttype"),
            q("C", "supported-calendar-component-set"),
        } <= set(names)
        for element in prop:
            assert not (element.text or "").strip()
            assert len(element) == 0, f"{element.tag} must be reported by name only"
        assert all((prop.find(name).text or "") == "" for name in names)

    def test_unknown_property_lands_in_a_404_propstat(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        body = _propfind_props("<D:displayname/>", "<D:no-such-property/>")
        response = _propfind(client, _collection(raw, AGENDA_COLLECTION), depth=0, body=body)
        assert response.status_code == 207
        collection = _responses(response.text)[0]
        assert _prop_text(collection, q("D", "displayname")) == "Agenda"
        assert q("D", "no-such-property") in _prop_names(collection, "HTTP/1.1 404")
        assert q("D", "no-such-property") not in _prop_names(collection, "HTTP/1.1 200")

    def test_no_trailing_slash_is_served_without_redirecting(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        urls = [
            _collection(raw, AGENDA_COLLECTION).rstrip("/"),
            _home(raw).rstrip("/"),
            f"/dav/{raw}",
            _collection(raw, f"{FESTIVAL_PREFIX}{festival.id}").rstrip("/"),
            _resource(raw, AGENDA_COLLECTION, event.id),
        ]
        for url in urls:
            response = _propfind(client, url, depth=1)
            assert response.status_code == 207, url
            assert response.status_code not in (301, 307, 308), url

    def test_every_href_is_an_absolute_dav_path(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Opening")
        for url, depth in [(_home(raw), 1), (_collection(raw, AGENDA_COLLECTION), 1)]:
            response = _propfind(client, url, depth=depth)
            hrefs = _responses_for(response.text)
            assert hrefs
            assert all(href.startswith("/dav/") for href in hrefs)
            assert all(raw in href for href in hrefs)

    def test_calendar_disabled_hides_every_collection(self, client, create_user, db_session):
        db_session.add(AppSetting(key="calendar.enabled", value=False, value_type="boolean"))
        db_session.commit()
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Opening")
        response = _propfind(client, _home(raw), depth=1)
        assert response.status_code == 207
        assert _responses_for(response.text) == [_home(raw)]

    def test_calendar_disabled_makes_the_agenda_collection_not_found(self, client, create_user, db_session):
        db_session.add(AppSetting(key="calendar.enabled", value=False, value_type="boolean"))
        db_session.commit()
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Opening")
        response = _propfind(client, _collection(raw, AGENDA_COLLECTION), depth=1)
        assert response.status_code == 404
        assert "Opening" not in response.text

    def test_malformed_propfind_body_is_rejected(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        response = _propfind(client, _collection(raw, AGENDA_COLLECTION), depth=0, body="<D:propfind><oops>")
        assert response.status_code == 400
        assert response.status_code < 500


class TestDavVisibility:
    """The DAV surface applies the same Event.visibility_scope rules as the agenda."""

    def test_public_event_is_visible_through_the_collection(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        response = _propfind(client, _collection(raw, AGENDA_COLLECTION), depth=1)
        assert _event_hrefs(response.text) == [_resource(raw, AGENDA_COLLECTION, event.id)]

    def test_festival_members_event_is_hidden_from_an_outsider(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Members only", scope=EventVisibilityScope.FESTIVAL_MEMBERS.value)
        _create_event(db_session, festival, "Public thing")
        response = _propfind(client, _collection(raw, AGENDA_COLLECTION), depth=1)
        assert len(_event_hrefs(response.text)) == 1
        assert "Members only" not in response.text

    def test_festival_members_event_is_visible_to_a_member(self, client, create_user, db_session):
        user, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Members only", scope=EventVisibilityScope.FESTIVAL_MEMBERS.value)
        db_session.execute(user_festival.insert().values(user_id=user.id, festival_id=festival.id))
        db_session.commit()
        response = _propfind(client, _collection(raw, AGENDA_COLLECTION), depth=1)
        assert _event_hrefs(response.text) == [_resource(raw, AGENDA_COLLECTION, event.id)]

    def test_roles_scope_needs_an_active_role_in_the_festival(self, client, create_user, db_session):
        user, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        role = _create_role(db_session, "jury")
        event = _create_event(db_session, festival, "Jury briefing", scope=EventVisibilityScope.ROLES.value)
        event.visibility_roles = [role]
        db_session.commit()

        assert _event_hrefs(_propfind(client, _collection(raw, AGENDA_COLLECTION), depth=1).text) == []

        db_session.add(
            UserRole(
                user_id=user.id,
                role_id=role.id,
                festival_id=festival.id,
                status=UserRoleStatus.APPROVED.value,
            )
        )
        db_session.commit()
        response = _propfind(client, _collection(raw, AGENDA_COLLECTION), depth=1)
        assert _event_hrefs(response.text) == [_resource(raw, AGENDA_COLLECTION, event.id)]

    def test_pending_role_does_not_grant_access(self, client, create_user, db_session):
        user, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        role = _create_role(db_session, "jury")
        event = _create_event(db_session, festival, "Jury briefing", scope=EventVisibilityScope.ROLES.value)
        event.visibility_roles = [role]
        db_session.add(
            UserRole(
                user_id=user.id,
                role_id=role.id,
                festival_id=festival.id,
                status=UserRoleStatus.PENDING.value,
            )
        )
        db_session.commit()
        response = _propfind(client, _collection(raw, AGENDA_COLLECTION), depth=1)
        assert _event_hrefs(response.text) == []

    def test_global_role_grants_access(self, client, create_user, db_session):
        user, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        role = _create_role(db_session, "producer", hierarchy_level=3)
        event = _create_event(db_session, festival, "Producer meeting", scope=EventVisibilityScope.ROLES.value)
        event.visibility_roles = [role]
        db_session.add(UserRole(user_id=user.id, role_id=role.id, festival_id=None, status=UserRoleStatus.ACTIVE.value))
        db_session.commit()
        response = _propfind(client, _collection(raw, AGENDA_COLLECTION), depth=1)
        assert _event_hrefs(response.text) == [_resource(raw, AGENDA_COLLECTION, event.id)]

    def test_roles_scope_without_selected_roles_hides_the_event(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Orphan briefing", scope=EventVisibilityScope.ROLES.value)
        response = _propfind(client, _collection(raw, AGENDA_COLLECTION), depth=1)
        assert _event_hrefs(response.text) == []

    def test_attendees_only_needs_an_attendee_row(self, client, create_user, db_session):
        user, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Green room", scope=EventVisibilityScope.ATTENDEES_ONLY.value)
        assert _event_hrefs(_propfind(client, _collection(raw, AGENDA_COLLECTION), depth=1).text) == []
        db_session.add(EventAttendee(event_id=event.id, user_id=user.id, status="registered"))
        db_session.commit()
        response = _propfind(client, _collection(raw, AGENDA_COLLECTION), depth=1)
        assert _event_hrefs(response.text) == [_resource(raw, AGENDA_COLLECTION, event.id)]

    def test_hidden_attendee_does_not_grant_access(self, client, create_user, db_session):
        user, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Green room", scope=EventVisibilityScope.ATTENDEES_ONLY.value)
        db_session.add(EventAttendee(event_id=event.id, user_id=user.id, status="registered", is_hidden=True))
        db_session.commit()
        response = _propfind(client, _collection(raw, AGENDA_COLLECTION), depth=1)
        assert _event_hrefs(response.text) == []

    def test_attendee_of_another_user_does_not_grant_access(self, client, create_user, db_session):
        other, _ = create_user(username="other", email="other@example.com")
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Green room", scope=EventVisibilityScope.ATTENDEES_ONLY.value)
        db_session.add(EventAttendee(event_id=event.id, user_id=other.id, status="registered"))
        db_session.commit()
        response = _propfind(client, _collection(raw, AGENDA_COLLECTION), depth=1)
        assert _event_hrefs(response.text) == []

    def test_private_event_is_absent_from_the_ics_feed(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Members only", scope=EventVisibilityScope.FESTIVAL_MEMBERS.value)
        _create_event(db_session, festival, "Public thing")
        body = client.get(_feed(raw, AGENDA_COLLECTION)).text
        assert _titles(body) == {"Public thing"}

    def test_private_resource_is_not_found_for_an_outsider(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Members only", scope=EventVisibilityScope.FESTIVAL_MEMBERS.value)
        response = _propfind(client, _resource(raw, AGENDA_COLLECTION, event.id), depth=0)
        assert response.status_code == 404

    def test_private_resource_is_not_found_on_get_for_an_outsider(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Members only", scope=EventVisibilityScope.FESTIVAL_MEMBERS.value)
        assert client.get(_resource(raw, AGENDA_COLLECTION, event.id)).status_code == 404

    def test_private_resource_is_served_to_a_member(self, client, create_user, db_session):
        user, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Members only", scope=EventVisibilityScope.FESTIVAL_MEMBERS.value)
        db_session.execute(user_festival.insert().values(user_id=user.id, festival_id=festival.id))
        db_session.commit()
        response = client.get(_resource(raw, AGENDA_COLLECTION, event.id))
        assert response.status_code == 200
        assert "Members only" in response.text

    def test_inactive_event_is_hidden(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Draft", is_active=False)
        response = _propfind(client, _collection(raw, AGENDA_COLLECTION), depth=1)
        assert _event_hrefs(response.text) == []

    def test_inactive_festival_is_hidden(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Archived", is_active=False)
        _create_event(db_session, festival, "Old")
        response = _propfind(client, _collection(raw, AGENDA_COLLECTION), depth=1)
        assert _event_hrefs(response.text) == []

    def test_hidden_festival_event_is_hidden(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Hidden", show_in_calendar=False)
        _create_event(db_session, festival, "Secret fest")
        response = _propfind(client, _collection(raw, AGENDA_COLLECTION), depth=1)
        assert _event_hrefs(response.text) == []


class TestDavGetResource:
    """Tests for GET/HEAD on a single VEVENT resource."""

    def test_resource_body_describes_one_vevent(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        response = client.get(_resource(raw, AGENDA_COLLECTION, event.id))
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/calendar; charset=utf-8; component=vevent"
        assert "component=vevent" in response.headers["content-type"]
        assert response.text.count("BEGIN:VEVENT") == 1
        assert "BEGIN:VCALENDAR" in response.text
        assert "END:VCALENDAR" in response.text
        assert f"UID:event-{event.id}@clakettes" in response.text
        assert "SUMMARY:Opening" in response.text

    def test_resource_carries_a_weak_etag_matching_propfind(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        etag = client.get(_resource(raw, AGENDA_COLLECTION, event.id)).headers["etag"]
        assert etag.startswith('W/"')
        propfind = _propfind(client, _resource(raw, AGENDA_COLLECTION, event.id), depth=0)
        assert _prop_text(_responses(propfind.text)[0], q("D", "getetag")) == etag

    def test_unknown_event_id_is_not_found(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        assert client.get(_resource(raw, AGENDA_COLLECTION, 4242)).status_code == 404

    def test_non_ics_resource_segment_is_not_found(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        url = _resource(raw, AGENDA_COLLECTION, event.id).replace(".ics", ".json")
        assert client.get(url).status_code == 404

    def test_event_of_another_collection_is_not_found(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        alpha = _create_festival(db_session, "Alpha")
        beta = _create_festival(db_session, "Beta")
        event = _create_event(db_session, alpha, "Alpha night")
        assert client.get(_resource(raw, f"{FESTIVAL_PREFIX}{beta.id}", event.id)).status_code == 404

    def test_head_returns_the_same_headers_with_an_empty_body(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        url = _resource(raw, AGENDA_COLLECTION, event.id)
        get_response = client.get(url)
        head_response = client.head(url)
        assert head_response.status_code == 200
        assert head_response.content == b""
        assert head_response.headers["content-type"] == get_response.headers["content-type"]
        assert head_response.headers["etag"] == get_response.headers["etag"]

    def test_trailing_slash_on_a_resource_is_served(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        response = client.get(_resource(raw, AGENDA_COLLECTION, event.id) + "/")
        assert response.status_code == 200
        assert "SUMMARY:Opening" in response.text

    def test_geo_line_is_emitted_with_coordinates(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        event.venue_latitude = 41.3874
        event.venue_longitude = 2.1686
        db_session.commit()
        body = client.get(_resource(raw, AGENDA_COLLECTION, event.id)).text
        assert "GEO:41.3874;2.1686" in body

    def test_geo_line_is_absent_without_coordinates(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        body = client.get(_resource(raw, AGENDA_COLLECTION, event.id)).text
        assert "GEO:" not in body

    def test_partial_geo_coordinates_are_not_emitted(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        event.venue_latitude = 41.3874
        db_session.commit()
        assert "GEO:" not in client.get(_resource(raw, AGENDA_COLLECTION, event.id)).text

    def test_location_lines_are_rendered(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        event.venue = "Cinema Central"
        event.short_description = "Opening gala"
        db_session.commit()
        body = client.get(_resource(raw, AGENDA_COLLECTION, event.id)).text
        assert "LOCATION:Cinema Central" in body
        assert "DESCRIPTION:Opening gala" in body
        assert 'CATEGORIES:"screening"' in body
        assert "X-APPLE-STRUCTURE-LOCATION:Alpha" in body


class TestDavFeed:
    """Tests for the whole-collection ICS feed."""

    def test_agenda_feed_structure_and_headers(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Opening")
        response = client.get(_feed(raw, AGENDA_COLLECTION))
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/calendar")
        assert "METHOD:PUBLISH" in response.text
        assert "X-WR-CALNAME:Agenda" in response.text
        assert "PRODID:-//Clakettes//Agenda//ES" in response.text
        assert "BEGIN:VCALENDAR" in response.text
        assert "END:VCALENDAR" in response.text
        assert response.text.count("BEGIN:VEVENT") == 1
        assert _uids(response.text) == {"event-1@clakettes"}

    def test_agenda_feed_uses_crlf_only(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Opening")
        text = client.get(_feed(raw, AGENDA_COLLECTION)).text
        assert "\r\n" in text
        assert "\n" not in text.replace("\r\n", "")
        assert "\r" not in text.replace("\r\n", "")

    def test_feed_is_served_inline_not_as_an_attachment(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        _create_festival(db_session, "Alpha")
        disposition = client.get(_feed(raw, AGENDA_COLLECTION)).headers["content-disposition"]
        assert disposition.startswith("inline")
        assert "attachment" not in disposition

    def test_festival_feed_names_the_festival(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        alpha = _create_festival(db_session, "Alpha")
        _create_event(db_session, alpha, "Alpha night")
        response = client.get(_feed(raw, f"{FESTIVAL_PREFIX}{alpha.id}"))
        assert response.status_code == 200
        assert "X-WR-CALNAME:Alpha" in response.text
        assert _titles(response.text) == {"Alpha night"}

    def test_festival_feed_excludes_other_festivals(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        alpha = _create_festival(db_session, "Alpha")
        beta = _create_festival(db_session, "Beta")
        _create_event(db_session, alpha, "Alpha night")
        _create_event(db_session, beta, "Beta night")
        assert _titles(client.get(_feed(raw, f"{FESTIVAL_PREFIX}{alpha.id}")).text) == {"Alpha night"}
        assert _titles(client.get(_feed(raw, AGENDA_COLLECTION)).text) == {"Alpha night", "Beta night"}

    def test_multi_day_event_keeps_one_vevent(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Marathon", end=BASE + timedelta(days=5))
        body = client.get(_feed(raw, AGENDA_COLLECTION)).text
        assert body.count("BEGIN:VEVENT") == 1
        assert "DTSTART:20260310T180000Z" in body
        assert "DTEND:20260315T180000Z" in body
        assert body.index("DTSTART:") < body.index("DTEND:")

    def test_event_without_end_date_gets_a_one_hour_dtend(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        assert event.end_date is None
        body = client.get(_feed(raw, AGENDA_COLLECTION)).text
        assert "DTSTART:20260310T180000Z" in body
        assert "DTEND:20260310T190000Z" in body

    def test_feed_escapes_ics_special_characters(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Party; Rock, Roll\nLate")
        body = client.get(_feed(raw, AGENDA_COLLECTION)).text
        assert "SUMMARY:Party\\; Rock\\, Roll\\nLate" in body
        assert "SUMMARY:Party; Rock, Roll" not in body

    def test_feed_escapes_backslashes(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Back\\slash")
        assert "SUMMARY:Back\\\\slash" in client.get(_feed(raw, AGENDA_COLLECTION)).text

    def test_bare_festival_number_feed_is_not_found(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        response = client.get(_feed(raw, str(festival.id)))
        assert response.status_code == 404

    def test_feed_requires_a_valid_token(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        _create_festival(db_session, "Alpha")
        assert client.get(_feed("invalid-token", AGENDA_COLLECTION)).status_code == 401
        assert client.get(_feed(raw, AGENDA_COLLECTION)).status_code == 200

    def test_feed_carries_the_collection_etag(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Opening")
        etag = client.get(_feed(raw, AGENDA_COLLECTION)).headers["etag"]
        propfind = _propfind(client, _collection(raw, AGENDA_COLLECTION), depth=0)
        assert _prop_text(_responses(propfind.text)[0], q("D", "getetag")) == etag

    def test_calendar_disabled_feed_is_empty(self, client, create_user, db_session):
        db_session.add(AppSetting(key="calendar.enabled", value=False, value_type="boolean"))
        db_session.commit()
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Opening")
        body = client.get(_feed(raw, AGENDA_COLLECTION)).text
        assert _titles(body) == set()
        assert "Opening" not in body

    def test_calendar_disabled_festival_feed_is_empty(self, client, create_user, db_session):
        db_session.add(AppSetting(key="calendar.enabled", value=False, value_type="boolean"))
        db_session.commit()
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Opening")
        body = client.get(_feed(raw, f"{FESTIVAL_PREFIX}{festival.id}")).text
        assert _titles(body) == set()
        assert "Opening" not in body

    def test_agenda_feed_is_ordered_by_start_date(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        late = _create_event(db_session, festival, "Late", start=BASE + timedelta(days=2))
        early = _create_event(db_session, festival, "Early", start=BASE - timedelta(days=2))
        body = client.get(_feed(raw, AGENDA_COLLECTION)).text
        assert body.index(f"UID:event-{early.id}@clakettes") < body.index(f"UID:event-{late.id}@clakettes")


class TestDavReport:
    """Tests for the calendar-query, calendar-multiget and sync-collection reports."""

    def test_calendar_query_returns_the_event_inside_the_range(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        window = _time_range(BASE - timedelta(days=1), BASE + timedelta(days=1))
        response = _report(client, _collection(raw, AGENDA_COLLECTION), _query_body(window))
        assert response.status_code == 207
        assert "<C:calendar-data" in response.text
        assert _calendar_titles(response.text) == {"Opening"}
        assert _event_hrefs(response.text) == [_resource(raw, AGENDA_COLLECTION, event.id)]

    def test_calendar_query_range_excludes_the_event(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Opening")
        window = _time_range(BASE + timedelta(days=10), BASE + timedelta(days=11))
        response = _report(client, _collection(raw, AGENDA_COLLECTION), _query_body(window))
        assert response.status_code == 207
        assert _event_hrefs(response.text) == []
        assert "calendar-data" not in response.text

    def test_calendar_query_without_a_range_returns_everything(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        first = _create_event(db_session, festival, "Early")
        second = _create_event(db_session, festival, "Late", start=BASE + timedelta(days=4))
        response = _report(client, _collection(raw, AGENDA_COLLECTION), _query_body())
        assert response.status_code == 207
        assert _event_hrefs(response.text) == [
            _resource(raw, AGENDA_COLLECTION, first.id),
            _resource(raw, AGENDA_COLLECTION, second.id),
        ]

    def test_calendar_query_without_a_range_skips_private_events(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Members only", scope=EventVisibilityScope.FESTIVAL_MEMBERS.value)
        _create_event(db_session, festival, "Public thing")
        response = _report(client, _collection(raw, AGENDA_COLLECTION), _query_body())
        assert _calendar_titles(response.text) == {"Public thing"}

    def test_calendar_query_is_scoped_to_its_collection(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        alpha = _create_festival(db_session, "Alpha")
        beta = _create_festival(db_session, "Beta")
        _create_event(db_session, alpha, "Alpha night")
        _create_event(db_session, beta, "Beta night")
        response = _report(client, _collection(raw, f"{FESTIVAL_PREFIX}{alpha.id}"), _query_body())
        assert _calendar_titles(response.text) == {"Alpha night"}

    def test_calendar_query_with_an_inverted_range_is_forbidden(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        _create_festival(db_session, "Alpha")
        window = _time_range(BASE + timedelta(days=1), BASE)
        response = _report(client, _collection(raw, AGENDA_COLLECTION), _query_body(window))
        assert response.status_code == 403
        assert "valid-filter-test" in response.text

    def test_calendar_query_with_an_unparsable_range_is_forbidden(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        _create_festival(db_session, "Alpha")
        window = '<C:filter><C:comp-filter name="VCALENDAR"><C:comp-filter name="VEVENT">'
        window += '<C:time-range start="not-a-date" end="20260311T000000Z"/>'
        window += "</C:comp-filter></C:comp-filter></C:filter>"
        response = _report(client, _collection(raw, AGENDA_COLLECTION), _query_body(window))
        assert response.status_code == 403

    def test_calendar_multiget_returns_both_resources(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        first = _create_event(db_session, festival, "Opening")
        second = _create_event(db_session, festival, "Brigadoon", start=BASE + timedelta(days=1))
        hrefs = [
            _resource(raw, AGENDA_COLLECTION, second.id),
            _resource(raw, AGENDA_COLLECTION, first.id),
        ]
        response = _report(client, _collection(raw, AGENDA_COLLECTION), _multiget_body(hrefs))
        assert response.status_code == 207
        assert _responses_for(response.text) == hrefs
        assert _calendar_titles(response.text) == {"Opening", "Brigadoon"}

    def test_calendar_multiget_skips_an_unknown_href(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        good = _resource(raw, AGENDA_COLLECTION, event.id)
        missing = _resource(raw, AGENDA_COLLECTION, 4242)
        response = _report(client, _collection(raw, AGENDA_COLLECTION), _multiget_body([good, missing]))
        assert response.status_code == 207
        assert _responses_for(response.text) == [good, missing]
        skipped = _response_for(response.text, "4242.ics")
        assert skipped.find(q("D", "status")) is not None
        assert "404" in skipped.find(q("D", "status")).text
        assert _calendar_titles(response.text) == {"Opening"}

    def test_calendar_multiget_skips_a_private_resource(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Members only", scope=EventVisibilityScope.FESTIVAL_MEMBERS.value)
        href = _resource(raw, AGENDA_COLLECTION, event.id)
        response = _report(client, _collection(raw, AGENDA_COLLECTION), _multiget_body([href]))
        assert response.status_code == 207
        assert _calendar_titles(response.text) == set()

    def test_sync_collection_without_a_token_lists_everything(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        first = _create_event(db_session, festival, "Opening")
        second = _create_event(db_session, festival, "Brigadoon", start=BASE + timedelta(days=1))
        response = _report(client, _collection(raw, AGENDA_COLLECTION), _sync_body())
        assert response.status_code == 207
        assert _event_hrefs(response.text) == [
            _resource(raw, AGENDA_COLLECTION, first.id),
            _resource(raw, AGENDA_COLLECTION, second.id),
        ]
        token = _sync_token(response.text)
        assert token is not None
        assert token.startswith(SYNC_TOKEN_PREFIX)
        assert _response_for(response.text, AGENDA_COLLECTION + "/") is not None

    def test_sync_collection_replaying_the_token_is_unchanged(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Opening")
        url = _collection(raw, AGENDA_COLLECTION)
        token = _sync_token(_report(client, url, _sync_body()).text)
        response = _report(client, url, _sync_body(token=token))
        assert response.status_code == 204
        assert response.content == b""

    def test_sync_collection_with_a_stale_token_reports_changes(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Opening")
        url = _collection(raw, AGENDA_COLLECTION)
        token = _sync_token(_report(client, url, _sync_body()).text)
        _create_event(db_session, festival, "Brigadoon", start=BASE + timedelta(days=1))
        response = _report(client, url, _sync_body(token=token))
        assert response.status_code == 207
        assert len(_event_hrefs(response.text)) == 2

    def test_sync_collection_with_an_unrelated_token_does_a_full_sync(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Opening")
        response = _report(client, _collection(raw, AGENDA_COLLECTION), _sync_body(token="nonsense"))
        assert response.status_code == 207
        assert len(_event_hrefs(response.text)) == 1

    def test_sync_collection_with_a_foreign_etag_does_a_full_sync(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Opening")
        body = _sync_body(token=f"{SYNC_TOKEN_PREFIX}deadbeef")
        response = _report(client, _collection(raw, AGENDA_COLLECTION), body)
        assert response.status_code == 207
        assert len(_event_hrefs(response.text)) == 1

    def test_sync_collection_level_two_is_forbidden(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        _create_festival(db_session, "Alpha")
        response = _report(client, _collection(raw, AGENDA_COLLECTION), _sync_body(level="2"))
        assert response.status_code == 403
        assert "supported-report" in response.text

    def test_unsupported_report_is_forbidden(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        _create_festival(db_session, "Alpha")
        body = _xml("D:expand-property", '<D:property name="x"/>')
        response = _report(client, _collection(raw, AGENDA_COLLECTION), body)
        assert response.status_code == 403
        assert "supported-report" in response.text
        assert "calendar-query" in response.text

    def test_malformed_report_body_is_a_client_error(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        _create_festival(db_session, "Alpha")
        response = _report(client, _collection(raw, AGENDA_COLLECTION), "<D:sync-collection><oops>")
        assert 400 <= response.status_code < 500

    def test_report_without_a_body_is_a_client_error(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        _create_festival(db_session, "Alpha")
        response = _dav(client, "REPORT", _collection(raw, AGENDA_COLLECTION), depth="1")
        assert 400 <= response.status_code < 500

    def test_report_on_an_unknown_collection_is_not_found(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        response = _report(client, _collection(raw, "nonsense"), _query_body())
        assert response.status_code == 404

    def test_calendar_home_set_report_resolves_the_home(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        response = _report(client, f"/dav/{raw}/", _xml("D:calendar-home-set"))
        assert response.status_code == 207
        assert _responses_for(response.text) == [f"/dav/{raw}/"]
        assert _link(_responses(response.text)[0], q("C", "calendar-home-set")) == _home(raw)

    def test_sync_collection_on_an_empty_collection_still_returns_a_token(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        response = _report(client, _collection(raw, AGENDA_COLLECTION), _sync_body())
        assert response.status_code == 207
        assert _event_hrefs(response.text) == []
        assert _sync_token(response.text) is not None


class TestDavReadOnly:
    """Every write verb is refused and leaves the database untouched."""

    @pytest.mark.parametrize("method", WRITE_METHODS)
    def test_write_verb_on_a_resource_is_refused(self, client, create_user, db_session, method):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        response = client.request(
            method,
            _resource(raw, AGENDA_COLLECTION, event.id),
            content="BEGIN:VCALENDAR",
            headers={"Content-Type": "text/calendar"},
        )
        assert response.status_code == 405, method
        assert set(response.headers["allow"].split(", ")) == READ_METHODS, method
        assert _count_events(db_session) == 1

    def test_refusal_advertises_no_write_verb(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        response = client.put(_resource(raw, AGENDA_COLLECTION, event.id), content="x")
        assert response.status_code == 405
        assert response.headers["allow"] == DAV_ALLOW
        for verb in WRITE_METHODS:
            assert verb not in response.headers["allow"]

    def test_refusal_does_not_touch_the_event(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        client.delete(_resource(raw, AGENDA_COLLECTION, event.id))
        db_session.expire_all()
        stored = db_session.query(Event).filter(Event.id == event.id).one()
        assert stored.title == "Opening"
        assert stored.is_active is True
        assert _count_events(db_session) == 1

    def test_put_cannot_create_a_new_resource(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        _create_festival(db_session, "Alpha")
        response = client.put(_resource(raw, AGENDA_COLLECTION, 9999), content="BEGIN:VCALENDAR")
        assert response.status_code == 405
        assert _count_events(db_session) == 0

    def test_write_on_a_collection_is_refused(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        _create_festival(db_session, "Alpha")
        response = client.request("DELETE", _collection(raw, AGENDA_COLLECTION))
        assert response.status_code == 405
        assert set(response.headers["allow"].split(", ")) == READ_METHODS

    def test_write_on_the_principal_is_refused(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        response = client.request("MOVE", f"/dav/{raw}/")
        assert response.status_code == 405

    def test_write_on_the_dav_root_is_refused(self, client):
        response = client.request("PROPPATCH", "/dav/", content="<D:propertyupdate/>")
        assert response.status_code == 405
        assert set(response.headers["allow"].split(", ")) == READ_METHODS

    def test_lock_is_refused_on_the_collection(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        _create_festival(db_session, "Alpha")
        assert client.request("LOCK", _collection(raw, AGENDA_COLLECTION)).status_code == 405

    def test_mkcol_is_refused(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        assert client.request("MKCOL", _collection(raw, "brand-new")).status_code == 405

    def test_propfind_is_never_redirected(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        urls = [
            "/dav/",
            f"/dav/{raw}/",
            _home(raw),
            _collection(raw, AGENDA_COLLECTION),
            _collection(raw, AGENDA_COLLECTION).rstrip("/"),
            _resource(raw, AGENDA_COLLECTION, event.id),
            _feed(raw, AGENDA_COLLECTION).rstrip(".ics"),
        ]
        for url in urls:
            response = _propfind(client, url, depth=1)
            assert response.status_code not in (301, 302, 307, 308), url
            assert response.history == [], url

    def test_report_is_never_redirected(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        for url in [f"/dav/{raw}/", _home(raw), _collection(raw, AGENDA_COLLECTION)]:
            response = _report(client, url, _query_body())
            assert response.status_code not in (301, 302, 307, 308), url
            assert response.history == [], url


class TestDavTokenApi:
    """Tests for GET|POST|DELETE /api/calendar/dav/token."""

    def test_status_requires_authentication(self, client):
        assert client.get("/api/calendar/dav/token").status_code == 401

    def test_creation_requires_authentication(self, client):
        assert client.post("/api/calendar/dav/token").status_code == 401

    def test_revocation_requires_authentication(self, client):
        assert client.delete("/api/calendar/dav/token").status_code == 401

    def test_plain_user_may_generate_a_token(self, client, auth_headers):
        headers, _ = auth_headers
        assert client.post("/api/calendar/dav/token", headers=headers).status_code == 200

    def test_generated_token_authenticates_on_dav(self, client, auth_headers):
        headers, _ = auth_headers
        token = client.post("/api/calendar/dav/token", headers=headers).json()["token"]
        response = client.get(_feed(token, AGENDA_COLLECTION))
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/calendar")

    def test_generated_token_is_43_url_safe_characters(self, client, auth_headers):
        headers, _ = auth_headers
        token = client.post("/api/calendar/dav/token", headers=headers).json()["token"]
        assert re.fullmatch(r"[A-Za-z0-9_-]{43}", token)

    def test_plaintext_token_is_never_stored(self, client, auth_headers, db_session):
        headers, user = auth_headers
        token = client.post("/api/calendar/dav/token", headers=headers).json()["token"]
        db_session.expire_all()
        stored = db_session.query(User).filter(User.id == user.id).one().dav_token_hash
        assert stored == hash_token(token)
        assert stored != token
        assert db_session.query(User).filter(User.dav_token_hash == token).count() == 0

    def test_status_before_any_token_is_false(self, client, auth_headers):
        headers, _ = auth_headers
        assert client.get("/api/calendar/dav/token", headers=headers).json()["has_token"] is False

    def test_status_reports_the_token_without_leaking_it(self, client, auth_headers):
        headers, _ = auth_headers
        token = client.post("/api/calendar/dav/token", headers=headers).json()["token"]
        response = client.get("/api/calendar/dav/token", headers=headers)
        assert response.status_code == 200
        assert response.json()["has_token"] is True
        assert token not in response.text
        assert "token" not in {key for key in response.json()}

    def test_collections_are_listed_on_creation(self, client, auth_headers, db_session):
        headers, _ = auth_headers
        festival = _create_festival(db_session, "Alpha")
        body = client.post("/api/calendar/dav/token", headers=headers).json()
        assert {c["name"]: c["display_name"] for c in body["collections"]} == {
            AGENDA_COLLECTION: "Agenda",
            f"{FESTIVAL_PREFIX}{festival.id}": "Alpha",
        }

    def test_status_lists_the_same_collections(self, client, auth_headers, db_session):
        headers, _ = auth_headers
        festival = _create_festival(db_session, "Alpha")
        client.post("/api/calendar/dav/token", headers=headers)
        listed = client.get("/api/calendar/dav/token", headers=headers).json()["collections"]
        assert AGENDA_COLLECTION in {c["name"] for c in listed}
        assert f"{FESTIVAL_PREFIX}{festival.id}" in {c["name"] for c in listed}

    def test_regeneration_rotates_the_token(self, client, auth_headers):
        headers, _ = auth_headers
        first = client.post("/api/calendar/dav/token", headers=headers).json()["token"]
        second = client.post("/api/calendar/dav/token", headers=headers).json()["token"]
        assert first != second
        assert client.get(_feed(first, AGENDA_COLLECTION)).status_code == 401
        assert client.get(_feed(second, AGENDA_COLLECTION)).status_code == 200

    def test_revocation_clears_the_token(self, client, auth_headers):
        headers, _ = auth_headers
        token = client.post("/api/calendar/dav/token", headers=headers).json()["token"]
        assert client.get(_feed(token, AGENDA_COLLECTION)).status_code == 200
        response = client.delete("/api/calendar/dav/token", headers=headers)
        assert response.status_code == 200
        assert response.json()["has_token"] is False
        assert client.get(_feed(token, AGENDA_COLLECTION)).status_code == 401

    def test_revocation_leaves_the_token_row_empty(self, client, auth_headers, db_session):
        headers, user = auth_headers
        client.post("/api/calendar/dav/token", headers=headers)
        client.delete("/api/calendar/dav/token", headers=headers)
        db_session.expire_all()
        assert db_session.query(User).filter(User.id == user.id).one().dav_token_hash is None

    def test_revocation_keeps_listing_collections(self, client, auth_headers, db_session):
        headers, _ = auth_headers
        _create_festival(db_session, "Alpha")
        client.post("/api/calendar/dav/token", headers=headers)
        body = client.delete("/api/calendar/dav/token", headers=headers).json()
        assert body["has_token"] is False
        assert AGENDA_COLLECTION in {c["name"] for c in body["collections"]}

    def test_one_token_cannot_read_another_users_private_events(self, client, auth_headers, create_user, db_session):
        owner, owner_raw = _subscriber(db_session, create_user, username="owner")
        other, other_raw = _subscriber(db_session, create_user, username="other")
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Members only", scope=EventVisibilityScope.FESTIVAL_MEMBERS.value)
        db_session.execute(user_festival.insert().values(user_id=owner.id, festival_id=festival.id))
        db_session.commit()
        assert client.get(_resource(owner_raw, AGENDA_COLLECTION, event.id)).status_code == 200
        assert client.get(_resource(other_raw, AGENDA_COLLECTION, event.id)).status_code == 404
        assert "Members only" not in client.get(_feed(other_raw, AGENDA_COLLECTION)).text

    def test_a_second_user_gets_a_different_token(self, client, auth_headers, create_user, db_session):
        headers, first_user = auth_headers
        other, _ = create_user(username="other", email="other@example.com")
        first = client.post("/api/calendar/dav/token", headers=headers).json()["token"]
        from app.auth import create_session

        _, access, _ = create_session(db_session, other.id)
        second = client.post("/api/calendar/dav/token", headers={"Authorization": f"Bearer {access}"}).json()["token"]
        assert first != second
        assert first_user.id != other.id


class TestDavLogRedaction:
    """The DAV token is a bearer credential, so it must never reach the log line."""

    def test_token_in_path_is_redacted(self):
        from app.main import _redact_dav_path

        assert _redact_dav_path("/dav/abc123XYZ/calendars/agenda/") == "/dav/***/calendars/agenda/"
        assert _redact_dav_path("/dav/abc123XYZ/calendars/agenda.ics") == "/dav/***/calendars/agenda.ics"

    def test_principal_id_is_left_readable(self):
        from app.main import _redact_dav_path

        assert _redact_dav_path("/dav/u7/calendars/agenda/") == "/dav/u7/calendars/agenda/"

    def test_other_paths_are_untouched(self):
        from app.main import _redact_dav_path

        assert _redact_dav_path("/api/users/login") == "/api/users/login"
        assert _redact_dav_path("/dav") == "/dav"
        assert _redact_dav_path("/dav/") == "/dav/"

    def test_middleware_rewrites_the_scope_after_the_app_returns(self, create_user, db_session):
        from app.main import RedactDavTokenMiddleware

        _, raw = _subscriber(db_session, create_user)
        seen = {}

        async def inner_app(scope, receive, send):
            seen["during"] = scope["path"]

        scope = {"type": "http", "path": f"/dav/{raw}/calendars/agenda/", "raw_path": b""}
        import asyncio

        asyncio.run(RedactDavTokenMiddleware(inner_app)(scope, None, None))
        assert seen["during"] == f"/dav/{raw}/calendars/agenda/"
        assert scope["path"] == "/dav/***/calendars/agenda/"
        assert raw not in scope["raw_path"].decode()

    def test_authenticated_request_still_works_with_redaction_enabled(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        response = client.get(f"/dav/{raw}/calendars/agenda.ics")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/calendar")


class TestDavRateLimit:
    """/dav is metered by its own bucket, separate from the rest of the API."""

    def test_dav_bucket_defaults(self):
        defaults = signature(RateLimitMiddleware.__init__).parameters
        assert defaults["dav_max_requests"].default == 600
        assert defaults["dav_window_seconds"].default == 60
        assert defaults["dav_max_requests"].default > defaults["max_requests"].default

    def test_dav_prefix_is_the_only_split(self):
        assert DAV_PREFIX == "/dav"

    def test_middleware_holds_two_independent_limiters(self):
        middleware = RateLimitMiddleware(app=None)
        assert middleware._limiter is not None
        assert middleware.dav_window_seconds == 60

    def test_dav_and_api_do_not_share_quota(self, monkeypatch):
        monkeypatch.delenv("TESTING", raising=False)
        middleware = RateLimitMiddleware(app=None, max_requests=2, window_seconds=60, dav_max_requests=3)
        dav_key, api_key = "dav:9.9.9.9", "middleware:9.9.9.9"

        async def run():
            async def call(path):
                request = Request(
                    {"type": "http", "method": "GET", "path": path, "headers": [], "client": ("9.9.9.9", 1234)}
                )
                return await middleware.dispatch(request, lambda r: _ok())

            return [await call(f"/dav/{'x' * index}") for index in range(4)] + [await call("/api/calendar/agenda")] * 2

        try:
            statuses = asyncio.run(run())
            assert [response.status_code for response in statuses] == [200, 200, 200, 429, 200, 200]
        finally:
            middleware._limiter.reset(dav_key)
            middleware._limiter.reset(api_key)

    def test_rate_limiting_is_disabled_under_test(self, client, create_user, db_session):
        assert os.environ.get("TESTING", "").lower() == "true"
        _, raw = _subscriber(db_session, create_user)
        _create_festival(db_session, "Alpha")
        assert {client.get(_feed(raw, AGENDA_COLLECTION)).status_code for _ in range(5)} == {200}


async def _ok():
    return Response("ok")


MAX_OCTETS = 75
UTC_VALUE = re.compile(r"\d{8}T\d{6}Z")
TRUNCATED_PROPERTY = "X-WR-CLAKETTES-TRUNCATED"
LONG_TITLE = "Sesión inaugural " + "áéíóúñ 🎬🍿 " * 20
NASTY_TITLE = "Party; Rock, Roll\\Back\nLate " + "áéíóú 🎬 " * 20
NASTY_ESCAPED = "Party\\; Rock\\, Roll\\\\Back\\nLate " + "áéíóú 🎬 " * 20


def _physical_lines(body):
    """Content lines of an ICS body exactly as they went on the wire."""
    assert body.endswith("\r\n"), "an iCalendar stream ends with CRLF"
    return body.split("\r\n")[:-1]


def _unfold(body):
    """Logical content lines of an ICS body, with folded continuations rejoined."""
    lines = []
    for physical in _physical_lines(body):
        if physical[:1] in (" ", "\t") and lines:
            lines[-1] += physical[1:]
        else:
            lines.append(physical)
    return lines


def _value(body, name):
    """First unfolded value of property ``name`` in an ICS body."""
    return _values(body, name)[:1][0] if _values(body, name) else None


def _values(body, name):
    """Every unfolded value of property ``name`` in an ICS body."""
    prefix = f"{name}:"
    return [line[len(prefix) :] for line in _unfold(body) if line.startswith(prefix)]


def _block_ics(block):
    """Turn a VEVENT block of unfolded lines back into a stream."""
    return "\r\n".join(block) + "\r\n"


def _body_of(lines):
    """Turn a list of already unfolded logical lines back into a stream."""
    return "\r\n".join(lines) + "\r\n"


def _vevents(body):
    """The VEVENT blocks of an ICS body, each as a list of unfolded lines."""
    blocks = []
    current = None
    for line in _unfold(body):
        if line == "BEGIN:VEVENT":
            current = []
        elif line == "END:VEVENT":
            blocks.append(current if current is not None else [])
            current = None
        elif current is not None:
            current.append(line)
    return blocks


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


def _calendar_data(multistatus_body):
    """The first non-empty ``<C:calendar-data>`` payload of a multistatus body."""
    root = ET.fromstring(multistatus_body.encode("utf-8"))
    for element in root.iter(q("C", "calendar-data")):
        if element.text:
            return element.text
    return ""


def _long_title_event(db_session, festival, title=LONG_TITLE, end=None):
    """An event whose title is far longer than one 75 octet content line."""
    return _create_event(db_session, festival, title, end=end)


def _bulk_events(db_session, festival, count):
    """Insert ``count`` public events in one statement."""
    db_session.bulk_save_objects(
        [
            Event(
                festival_id=festival.id,
                title=f"Bulk {index}",
                event_type="screening",
                start_date=BASE + timedelta(minutes=index),
                end_date=BASE + timedelta(minutes=index, seconds=1800),
                visibility_scope=EventVisibilityScope.PUBLIC.value,
                is_active=True,
            )
            for index in range(count)
        ]
    )
    db_session.commit()


class TestDavIcsRfcCompliance:
    """RFC 5545 conformance of the generated ICS, asserted on the bytes served."""

    def test_folded_lines_never_exceed_75_octets(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _long_title_event(db_session, festival)
        event.venue = "Sala " + "á" * 200
        event.short_description = "Descripción " + "🎬" * 120
        db_session.commit()
        body = client.get(_resource(raw, AGENDA_COLLECTION, event.id)).text
        lengths = [len(line.encode("utf-8")) for line in _physical_lines(body)]
        assert max(lengths) <= MAX_OCTETS, sorted(lengths, reverse=True)[:3]
        assert max(lengths) >= MAX_OCTETS - 1
        assert len(_physical_lines(body)) > len(_unfold(body))

    def test_folding_never_splits_a_utf8_sequence(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _long_title_event(db_session, festival)
        content = client.get(_resource(raw, AGENDA_COLLECTION, event.id)).content
        chunks = content.split(b"\r\n")[:-1]
        assert max(len(chunk) for chunk in chunks) <= MAX_OCTETS
        for chunk in chunks:
            chunk.decode("utf-8")
        assert _value(content.decode("utf-8"), "SUMMARY") == LONG_TITLE

    def test_long_multibyte_title_round_trips_through_unfolding(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _long_title_event(db_session, festival)
        body = client.get(_feed(raw, AGENDA_COLLECTION)).text
        assert _value(body, "SUMMARY") == LONG_TITLE
        assert len(LONG_TITLE.encode("utf-8")) > MAX_OCTETS

    def test_a_leading_space_in_a_value_survives_folding(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        title = " " + "Leading space title " + "é" * 100
        _create_event(db_session, festival, title)
        body = client.get(_feed(raw, AGENDA_COLLECTION)).text
        assert _value(body, "SUMMARY") == title
        assert _value(body, "SUMMARY").startswith(" ")
        assert len(_physical_lines(body)) > len(_unfold(body))

    def test_continuation_lines_carry_exactly_one_leading_space(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _long_title_event(db_session, festival)
        body = client.get(_feed(raw, AGENDA_COLLECTION)).text
        physical = _physical_lines(body)
        continuations = [line for line in physical if line[:1].isspace()]
        assert continuations
        assert all(line[:1] == " " for line in continuations)
        assert len(physical) == len(_unfold(body)) + len(continuations)
        assert not any(line[:1].isspace() for line in _unfold(body))

    def test_value_escaping_happens_before_folding(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, NASTY_TITLE)
        body = client.get(_feed(raw, AGENDA_COLLECTION)).text
        summary = _value(body, "SUMMARY")
        assert summary == NASTY_ESCAPED
        assert _unescape(summary) == NASTY_TITLE
        assert len(_values(body, "SUMMARY")) == 1
        assert "\\;" in summary and "\\," in summary and "\\\\" in summary and "\\n" in summary
        assert len(_physical_lines(body)) > len(_unfold(body))

    def test_backslash_is_doubled_before_folding(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        title = "Path C:\\clakettes\\cine " + "\\ó" * 80
        _create_event(db_session, festival, title)
        body = client.get(_feed(raw, AGENDA_COLLECTION)).text
        assert _unescape(_value(body, "SUMMARY")) == title
        assert _value(body, "SUMMARY").count("\\\\") == title.count("\\")

    def test_literal_newline_becomes_an_escaped_sequence(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "First line\r\nSecond line")
        body = client.get(_feed(raw, AGENDA_COLLECTION)).text
        assert _value(body, "SUMMARY") == "First line\\nSecond line"
        assert "\n" not in body.replace("\r\n", "")
        assert "\r" not in body.replace("\r\n", "")

    def test_stream_is_crlf_terminated_without_a_trailing_blank_line(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _long_title_event(db_session, festival)
        content = client.get(_feed(raw, AGENDA_COLLECTION)).content
        assert content.endswith(b"\r\n")
        assert not content.endswith(b"\r\n\r\n")
        lines = _unfold(content.decode("utf-8"))
        assert lines[0] == "BEGIN:VCALENDAR"
        assert lines[-1] == "END:VCALENDAR"
        assert "" not in lines

    def test_stream_has_no_bare_lf_or_lone_cr(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Party; Rock, Roll\nLate")
        content = client.get(_feed(raw, AGENDA_COLLECTION)).content
        assert b"\n" not in content.replace(b"\r\n", b"")
        assert b"\r" not in content.replace(b"\r\n", b"")

    def test_stream_has_no_byte_order_mark(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Acentuádo 🎬")
        for url in [_feed(raw, AGENDA_COLLECTION), _resource(raw, AGENDA_COLLECTION, event.id)]:
            content = client.get(url).content
            assert not content.startswith(b"\xef\xbb\xbf"), url
            assert content.startswith(b"BEGIN:VCALENDAR"), url
            assert content.endswith(b"\r\n"), url

    def test_every_vevent_declares_uid_dtstamp_and_dtstart(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        first = _long_title_event(db_session, festival)
        second = _create_event(db_session, festival, "Brigadoon", start=BASE + timedelta(days=1))
        blocks = _vevents(client.get(_feed(raw, AGENDA_COLLECTION)).text)
        assert len(blocks) == 2
        assert {_value(_block_ics(block), "UID") for block in blocks} == {
            f"event-{first.id}@clakettes",
            f"event-{second.id}@clakettes",
        }
        for block in blocks:
            joined = _block_ics(block)
            names = [line.split(":", 1)[0] for line in block]
            for required in ("UID", "DTSTAMP", "DTSTART"):
                assert required in names, (required, names)
            assert re.fullmatch(r"event-\d+@clakettes", _value(joined, "UID"))
            assert _value(joined, "DTSTART")

    def test_uid_is_stable_across_regenerations(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _long_title_event(db_session, festival)
        first = client.get(_feed(raw, AGENDA_COLLECTION))
        second = client.get(_feed(raw, AGENDA_COLLECTION))
        assert _values(first.text, "UID") == _values(second.text, "UID")
        assert _values(first.text, "UID") == [f"event-{event.id}@clakettes"]
        assert _value(first.text, "UID") in client.get(_resource(raw, AGENDA_COLLECTION, event.id)).text

    def test_dtstamp_is_utc_formatted(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _long_title_event(db_session, festival)
        body = client.get(_feed(raw, AGENDA_COLLECTION)).text
        for block in _vevents(body):
            joined = _block_ics(block)
            assert UTC_VALUE.fullmatch(_value(joined, "DTSTAMP")), _value(joined, "DTSTAMP")
            assert _value(joined, "DTSTAMP").endswith("Z")

    def test_no_tzid_and_no_floating_local_times(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _long_title_event(db_session, festival)
        for url in [_feed(raw, AGENDA_COLLECTION)]:
            body = client.get(url).text
            assert "TZID" not in body
            for line in _unfold(body):
                if ":" not in line:
                    continue
                name = line.split(":", 1)[0].split(";", 1)[0]
                if name in ("DTSTART", "DTEND", "DTSTAMP", "LAST-MODIFIED", "CREATED"):
                    assert UTC_VALUE.fullmatch(line.split(":", 1)[1]), line
                if name in ("DTSTART", "DTEND", "DTSTAMP", "LAST-MODIFIED"):
                    assert "VALUE=DATE" not in line, line

    @pytest.mark.parametrize(
        "end",
        [None, BASE + timedelta(days=5), BASE, BASE - timedelta(hours=3), BASE + timedelta(seconds=1)],
        ids=["default", "multiday", "zero-length", "inverted", "minimal"],
    )
    def test_dtend_is_strictly_after_dtstart(self, client, create_user, db_session, end):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Opening", end=end)
        block = _vevents(client.get(_feed(raw, AGENDA_COLLECTION)).text)[0]
        joined = _block_ics(block)
        assert _instant(_value(joined, "DTEND")) > _instant(_value(joined, "DTSTART"))

    def test_multiday_event_keeps_its_exact_span(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Marathon", start=BASE, end=BASE + timedelta(days=5, hours=3))
        block = _vevents(client.get(_feed(raw, AGENDA_COLLECTION)).text)[0]
        joined = _block_ics(block)
        assert _value(joined, "DTSTART") == "20260310T180000Z"
        assert _value(joined, "DTEND") == "20260315T210000Z"
        assert _instant(_value(joined, "DTEND")) - _instant(_value(joined, "DTSTART")) == timedelta(days=5, hours=3)

    def test_feed_wrapper_is_well_formed(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Opening")
        _create_event(db_session, festival, "Brigadoon", start=BASE + timedelta(days=1))
        lines = _unfold(client.get(_feed(raw, AGENDA_COLLECTION)).text)
        assert lines[0] == "BEGIN:VCALENDAR"
        assert lines[-1] == "END:VCALENDAR"
        assert lines.count("BEGIN:VCALENDAR") == 1
        assert lines.count("END:VCALENDAR") == 1
        assert lines.count("BEGIN:VEVENT") == lines.count("END:VEVENT") == 2
        assert _value(_body_of(lines), "VERSION") == "2.0"
        assert _value(_body_of(lines), "PRODID") == "-//Clakettes//Agenda//ES"
        assert _value(_body_of(lines), "CALSCALE") == "GREGORIAN"
        assert _value(_body_of(lines), "METHOD") == "PUBLISH"
        assert lines.index("VERSION:2.0") < lines.index("BEGIN:VEVENT")
        assert lines.index("END:VCALENDAR") == len(lines) - 1
        sequence = [line for line in lines if line.endswith(":VEVENT") or line.endswith(":VCALENDAR")]
        assert sequence == [
            "BEGIN:VCALENDAR",
            "BEGIN:VEVENT",
            "END:VEVENT",
            "BEGIN:VEVENT",
            "END:VEVENT",
            "END:VCALENDAR",
        ]

    def test_single_resource_wrapper_declares_version_and_prodid(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        body = client.get(_resource(raw, AGENDA_COLLECTION, event.id)).text
        lines = _unfold(body)
        assert lines[0] == "BEGIN:VCALENDAR"
        assert lines[-1] == "END:VCALENDAR"
        assert lines.count("BEGIN:VEVENT") == 1
        assert lines.count("END:VEVENT") == 1
        assert lines[1] == "VERSION:2.0"
        assert "PRODID:-//Clakettes//Agenda//ES" in lines

    def test_feed_warns_when_the_event_limit_truncates_it(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _bulk_events(db_session, festival, DAV_MAX_EVENTS + 1)
        body = client.get(_feed(raw, AGENDA_COLLECTION)).text
        assert _value(body, TRUNCATED_PROPERTY) == str(DAV_MAX_EVENTS)
        assert _unfold(body).count("BEGIN:VEVENT") == DAV_MAX_EVENTS

    def test_feed_without_truncation_declares_no_warning(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _bulk_events(db_session, festival, DAV_MAX_EVENTS - 1)
        body = client.get(_feed(raw, AGENDA_COLLECTION)).text
        assert _value(body, TRUNCATED_PROPERTY) is None
        assert _unfold(body).count("BEGIN:VEVENT") == DAV_MAX_EVENTS - 1

    def test_structured_geo_keeps_its_unquoted_semicolon(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        event.venue_latitude = 41.3874
        event.venue_longitude = 2.1686
        db_session.commit()
        body = client.get(_feed(raw, AGENDA_COLLECTION)).text
        assert _value(body, "GEO") == "41.3874;2.1686"

    def test_x_wr_calname_escapes_text_specials(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha; Sitges, BCN")
        _create_event(db_session, festival, "Opening")
        body = client.get(_feed(raw, f"{FESTIVAL_PREFIX}{festival.id}")).text
        calname = _value(body, "X-WR-CALNAME")
        assert calname == "Alpha\\; Sitges\\, BCN"
        assert _unescape(calname) == festival.name
        assert _value(body, "X-APPLE-STRUCTURE-LOCATION") == "Alpha\\; Sitges\\, BCN"
        assert "\r\nSUMMARY:Opening" in body

    @pytest.mark.parametrize("title", ["", "   ", " ", "\t"], ids=["empty", "spaces", "space", "tab"])
    def test_empty_or_blank_title_still_yields_a_valid_vevent(self, client, create_user, db_session, title):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, title)
        body = client.get(_resource(raw, AGENDA_COLLECTION, event.id)).text
        blocks = _vevents(body)
        assert len(blocks) == 1
        joined = _block_ics(blocks[0])
        assert _value(joined, "SUMMARY") == title
        assert _value(joined, "UID") == f"event-{event.id}@clakettes"
        assert _instant(_value(joined, "DTEND")) > _instant(_value(joined, "DTSTART"))
        assert all(len(line.encode("utf-8")) <= MAX_OCTETS for line in _physical_lines(body))

    def test_report_calendar_data_carries_the_folded_summary(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _long_title_event(db_session, festival)
        response = _report(client, _collection(raw, AGENDA_COLLECTION), _query_body())
        ics = _calendar_data(response.text)
        assert _value(ics, "SUMMARY") == LONG_TITLE
        assert all(len(line.encode("utf-8")) <= MAX_OCTETS for line in _physical_lines(ics))

    def test_propfind_calendar_data_carries_the_folded_summary(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _long_title_event(db_session, festival)
        response = _propfind(client, _collection(raw, AGENDA_COLLECTION), depth=1)
        ics = _calendar_data(response.text)
        assert _value(ics, "SUMMARY") == LONG_TITLE
        assert all(len(line.encode("utf-8")) <= MAX_OCTETS for line in _physical_lines(ics))


def _stamped_event(db_session, festival, updated_at, created_at=None, title="Opening"):
    """An event whose own timestamps are pinned to fixed instants."""
    event = _create_event(db_session, festival, title)
    event.updated_at = updated_at
    if created_at is not None:
        event.created_at = created_at
    db_session.commit()
    db_session.refresh(event)
    return event


class TestDavDtstampReproducibility:
    """DTSTAMP is read from the event row, so unchanged resources never move."""

    def test_dtstamp_is_the_event_updated_at(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        stamp = datetime(2021, 5, 4, 3, 2, 1)
        event = _stamped_event(db_session, festival, stamp)
        body = client.get(_resource(raw, AGENDA_COLLECTION, event.id)).text
        assert _value(body, "DTSTAMP") == stamp.strftime(UTC_BASIC)
        assert _value(body, "DTSTAMP") == "20210504T030201Z"
        assert _value(body, "LAST-MODIFIED") == "20210504T030201Z"

    def test_dtstamp_is_read_as_utc_from_a_naive_column(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        stamp = datetime(2021, 5, 4, 3, 2, 1)
        event = _stamped_event(db_session, festival, stamp)
        assert event.updated_at.tzinfo is None
        body = client.get(_resource(raw, AGENDA_COLLECTION, event.id)).text
        assert _value(body, "DTSTAMP") == "20210504T030201Z"
        assert _value(body, "DTSTART") == "20260310T180000Z"

    def test_dtstamp_is_not_the_wall_clock(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        stamp = datetime(2019, 3, 4, 5, 6, 7)
        event = _stamped_event(db_session, festival, stamp)
        this_year = datetime.now().strftime("%Y")
        for url in [_resource(raw, AGENDA_COLLECTION, event.id), _feed(raw, AGENDA_COLLECTION)]:
            body = client.get(url).text
            assert this_year not in _value(body, "DTSTAMP"), (url, this_year)
            assert _value(body, "DTSTAMP") == "20190304T050607Z"

    def test_dtstamp_falls_back_to_created_at(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _stamped_event(
            db_session,
            festival,
            None,
            created_at=datetime(2018, 7, 6, 5, 4, 3),
        )
        body = client.get(_resource(raw, AGENDA_COLLECTION, event.id)).text
        assert _value(body, "DTSTAMP") == "20180706T050403Z"
        assert _value(body, "LAST-MODIFIED") is None

    def test_dtstamp_survives_null_timestamps(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _stamped_event(db_session, festival, None, created_at=None)
        body = client.get(_resource(raw, AGENDA_COLLECTION, event.id)).text
        stamp = _value(body, "DTSTAMP")
        assert UTC_VALUE.fullmatch(stamp), stamp
        assert stamp.endswith("Z")
        assert _instant(stamp) >= datetime(2020, 1, 1)

    def test_two_gets_of_one_resource_are_byte_identical(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _long_title_event(db_session, festival)
        event.venue = "Sala " + "á" * 200
        db_session.commit()
        url = _resource(raw, AGENDA_COLLECTION, event.id)
        first = client.get(url)
        second = client.get(url)
        assert first.status_code == second.status_code == 200
        assert first.content == second.content
        assert first.headers["etag"] == second.headers["etag"]
        assert first.content.count(b"DTSTAMP:") == 1

    def test_two_gets_of_a_feed_are_byte_identical(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _long_title_event(db_session, festival)
        _create_event(db_session, festival, "Brigadoon", start=BASE + timedelta(days=1))
        first = client.get(_feed(raw, AGENDA_COLLECTION))
        second = client.get(_feed(raw, AGENDA_COLLECTION))
        assert first.content == second.content
        assert _values(first.text, "DTSTAMP") == _values(second.text, "DTSTAMP")
        assert len(_values(first.text, "DTSTAMP")) == 2

    def test_resource_etag_is_stable_across_gets(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _stamped_event(db_session, festival, datetime(2021, 5, 4, 3, 2, 1))
        url = _resource(raw, AGENDA_COLLECTION, event.id)
        etags = {client.get(url).headers["etag"] for _ in range(3)}
        assert len(etags) == 1
        propfind = _propfind(client, _collection(raw, AGENDA_COLLECTION), depth=1)
        assert etags == {_prop_text(_response_for(propfind.text, f"/{event.id}.ics"), q("D", "getetag"))}

    def test_collection_etag_is_stable_when_nothing_changed(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _stamped_event(db_session, festival, datetime(2021, 5, 4, 3, 2, 1))
        url = _feed(raw, AGENDA_COLLECTION)
        first, second = client.get(url), client.get(url)
        assert first.headers["etag"] == second.headers["etag"]
        collection = _propfind(client, _collection(raw, AGENDA_COLLECTION), depth=0)
        href = f"/dav/{raw}/calendars/{AGENDA_COLLECTION}/"
        assert _prop_text(_response_for(collection.text, href), q("D", "getetag")) == first.headers["etag"]
        assert _sync_token(_report(client, _collection(raw, AGENDA_COLLECTION), _sync_body()).text)

    def test_etag_and_body_move_together(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _stamped_event(db_session, festival, datetime(2021, 5, 4, 3, 2, 1))
        url = _resource(raw, AGENDA_COLLECTION, event.id)
        before = client.get(url)
        event.title = "Renamed"
        db_session.commit()
        after = client.get(url)
        assert before.headers["etag"] != after.headers["etag"]
        assert _value(before.text, "DTSTAMP") != _value(after.text, "DTSTAMP")
        assert _value(after.text, "SUMMARY") == "Renamed"


def _conditional(client, method, url, if_none_match, body=None):
    """Send a DAV request carrying a raw If-None-Match header value."""
    headers = {"If-None-Match": if_none_match}
    if body is not None:
        headers["Content-Type"] = "application/xml"
    return client.request(method, url, content=body, headers=headers)


def _strong(etag):
    """The entity-tag with its weak prefix dropped."""
    return etag[2:] if etag.startswith("W/") else etag


def _weak(etag):
    """The entity-tag written in its weak form."""
    return etag if etag.startswith("W/") else f"W/{etag}"


def _sequence_of(client, url):
    """SEQUENCE of the first VEVENT of an ICS response."""
    return int(_value(client.get(url).text, "SEQUENCE"))


def _category_list(body):
    """CATEGORIES of an ICS body read back as the list a parser would build."""
    raw = _value(body, "CATEGORIES")
    if raw is None:
        return []
    return [_unescape(entry) for entry in re.findall(r'"((?:[^"\\]|\\.)*)"', raw)]


class TestDavConditionalGet:
    """If-None-Match is honoured on every ICS representation (RFC 9110 13.1.2)."""

    def test_feed_returns_304_for_a_matching_strong_tag(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Opening")
        url = _feed(raw, AGENDA_COLLECTION)
        etag = client.get(url).headers["etag"]
        response = _conditional(client, "GET", url, etag)
        assert response.status_code == 304
        assert response.headers["etag"] == etag

    def test_feed_accepts_the_weak_form_of_its_strong_tag(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Opening")
        url = _feed(raw, AGENDA_COLLECTION)
        etag = client.get(url).headers["etag"]
        assert not etag.startswith("W/")
        assert _conditional(client, "GET", url, _weak(etag)).status_code == 304

    def test_feed_accepts_the_strong_form_of_a_weak_tag(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Opening")
        url = _feed(raw, AGENDA_COLLECTION)
        etag = _weak(client.get(url).headers["etag"])
        assert _conditional(client, "GET", url, etag).status_code == 304

    def test_resource_returns_304_for_its_weak_tag(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        url = _resource(raw, AGENDA_COLLECTION, event.id)
        etag = client.get(url).headers["etag"]
        assert etag.startswith('W/"')
        assert _conditional(client, "GET", url, etag).status_code == 304

    def test_resource_accepts_the_strong_form_of_its_weak_tag(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        url = _resource(raw, AGENDA_COLLECTION, event.id)
        strong = _strong(client.get(url).headers["etag"])
        assert _conditional(client, "GET", url, strong).status_code == 304
        assert _conditional(client, "GET", url, f"W/{strong}").status_code == 304

    def test_trailing_slash_resource_alias_answers_304(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        url = _resource(raw, AGENDA_COLLECTION, event.id) + "/"
        etag = client.get(url).headers["etag"]
        response = _conditional(client, "GET", url, etag)
        assert response.status_code == 304
        assert response.headers["etag"] == etag

    def test_star_matches_any_existing_representation(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        assert _conditional(client, "GET", _feed(raw, AGENDA_COLLECTION), "*").status_code == 304
        assert _conditional(client, "GET", _resource(raw, AGENDA_COLLECTION, event.id), "*").status_code == 304

    def test_a_comma_separated_list_matches_on_any_member(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Opening")
        url = _feed(raw, AGENDA_COLLECTION)
        etag = client.get(url).headers["etag"]
        assert _conditional(client, "GET", url, f'"deadbeef", {_weak(etag)} , "feed"').status_code == 304

    def test_a_stale_tag_is_answered_with_the_full_body(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Opening")
        url = _feed(raw, AGENDA_COLLECTION)
        response = _conditional(client, "GET", url, '"0123456789abcdef0123"')
        assert response.status_code == 200
        assert "SUMMARY:Opening" in response.text
        assert response.headers["etag"] != '"0123456789abcdef0123"'

    def test_opaque_tags_are_compared_case_sensitively(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        url = _resource(raw, AGENDA_COLLECTION, event.id)
        opaque = _strong(client.get(url).headers["etag"]).strip('"')
        mutated = ("B" if opaque[0] != "B" else "C") + opaque[1:]
        assert mutated != opaque
        assert _conditional(client, "GET", url, f'W/"{mutated}"').status_code == 200
        assert _conditional(client, "GET", url, f'w/"{opaque}"').status_code == 200

    @pytest.mark.parametrize(
        "garbage",
        ["not-an-etag", '"', '""', "W/", 'W/""x"', '"unterminated', "*,,", ",", "W/, W/"],
        ids=["word", "quote", "empty", "dquote", "open", "commas", "only-comma", "empty-weak", "weak-comma"],
    )
    def test_a_malformed_header_falls_back_to_the_full_body(self, client, create_user, db_session, garbage):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Opening")
        response = _conditional(client, "GET", _feed(raw, AGENDA_COLLECTION), garbage)
        assert response.status_code == 200
        assert "SUMMARY:Opening" in response.text

    def test_a_malformed_header_does_not_fail_a_resource(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        response = _conditional(client, "GET", _resource(raw, AGENDA_COLLECTION, event.id), "garbage")
        assert response.status_code == 200
        assert "SUMMARY:Opening" in response.text

    def test_a_not_modified_body_is_empty(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        for url in [_feed(raw, AGENDA_COLLECTION), _resource(raw, AGENDA_COLLECTION, event.id)]:
            etag = client.get(url).headers["etag"]
            response = _conditional(client, "GET", url, etag)
            assert response.status_code == 304
            assert response.content == b""
            assert response.text == ""

    def test_a_not_modified_repeats_the_representation_headers(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Opening")
        url = _feed(raw, AGENDA_COLLECTION)
        first = client.get(url)
        response = _conditional(client, "GET", url, first.headers["etag"])
        assert response.headers["etag"] == first.headers["etag"]
        assert response.headers["content-disposition"] == first.headers["content-disposition"]

    def test_head_with_a_matching_tag_is_also_not_modified(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        url = _resource(raw, AGENDA_COLLECTION, event.id)
        etag = client.head(url).headers["etag"]
        response = _conditional(client, "HEAD", url, etag)
        assert response.status_code == 304
        assert response.content == b""

    def test_two_gets_then_a_conditional_get_is_the_polling_sequence(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Opening")
        url = _feed(raw, AGENDA_COLLECTION)
        first = client.get(url)
        second = _conditional(client, "GET", url, first.headers["etag"])
        assert first.status_code == 200
        assert first.headers["etag"] == second.headers["etag"]
        assert second.status_code == 304
        assert second.content == b""

    def test_an_update_invalidates_the_cached_tag(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _stamped_event(db_session, festival, datetime(2021, 5, 4, 3, 2, 1))
        url = _resource(raw, AGENDA_COLLECTION, event.id)
        stale = client.get(url).headers["etag"]
        event.title = "Renamed"
        event.updated_at = datetime(2021, 5, 4, 3, 2, 2)
        db_session.commit()
        refreshed = _conditional(client, "GET", url, stale)
        assert refreshed.status_code == 200
        assert refreshed.headers["etag"] != stale
        assert _value(refreshed.text, "SUMMARY") == "Renamed"

    def test_an_unchanged_collection_keeps_its_tag_across_a_new_event(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _stamped_event(db_session, festival, datetime(2021, 5, 4, 3, 2, 1))
        url = _feed(raw, AGENDA_COLLECTION)
        etag = client.get(url).headers["etag"]
        assert _conditional(client, "GET", url, etag).status_code == 304

    def test_an_unauthenticated_conditional_get_is_still_challenged(self, client, db_session):
        assert _conditional(client, "GET", "/dav/nobody/calendars/agenda.ics", "*").status_code == 401

    def test_multistatus_verbs_carry_no_http_validator_to_revalidate(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        propfind = _conditional(client, "PROPFIND", _collection(raw, AGENDA_COLLECTION), "*")
        assert propfind.status_code == 207
        assert "etag" not in propfind.headers
        report = _conditional(client, "REPORT", _collection(raw, AGENDA_COLLECTION), "*", body=_sync_body())
        assert report.status_code == 207
        assert "etag" not in report.headers
        resource = _conditional(client, "PROPFIND", _resource(raw, AGENDA_COLLECTION, event.id), "*")
        assert resource.status_code == 207
        assert "etag" not in resource.headers


class TestDavEventProperties:
    """URL, SEQUENCE and CATEGORIES of the rendered VEVENT (RFC 5545)."""

    def test_url_is_absolute_when_a_public_base_url_is_configured(self, client, create_user, db_session, monkeypatch):
        monkeypatch.setattr(settings, "PUBLIC_BASE_URL", "https://clakettes.example")
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        for url in [_feed(raw, AGENDA_COLLECTION), _resource(raw, AGENDA_COLLECTION, event.id)]:
            value = _value(client.get(url).text, "URL")
            assert value == f"https://clakettes.example/events/{event.id}", url
            assert value.startswith(("http://", "https://")), url

    def test_a_trailing_slash_on_the_base_url_is_not_doubled(self, client, create_user, db_session, monkeypatch):
        monkeypatch.setattr(settings, "PUBLIC_BASE_URL", "https://clakettes.example/")
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        assert _value(client.get(_resource(raw, AGENDA_COLLECTION, event.id)).text, "URL") == (
            f"https://clakettes.example/events/{event.id}"
        )

    def test_url_is_omitted_when_no_public_base_url_is_configured(self, client, create_user, db_session, monkeypatch):
        monkeypatch.setattr(settings, "PUBLIC_BASE_URL", None)
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        for url in [_feed(raw, AGENDA_COLLECTION), _resource(raw, AGENDA_COLLECTION, event.id)]:
            body = client.get(url).text
            assert _value(body, "URL") is None, url
            assert "URL:" not in body, url
            assert body.count("BEGIN:VEVENT") == 1

    def test_a_blank_public_base_url_is_treated_as_unset(self, client, create_user, db_session, monkeypatch):
        monkeypatch.setattr(settings, "PUBLIC_BASE_URL", "   ")
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        assert _value(client.get(_resource(raw, AGENDA_COLLECTION, event.id)).text, "URL") is None

    def test_a_new_event_starts_at_sequence_zero(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        body = client.get(_resource(raw, AGENDA_COLLECTION, event.id)).text
        assert _value(body, "SEQUENCE") == "0"

    def test_sequence_is_stable_across_two_gets(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _stamped_event(
            db_session,
            festival,
            datetime(2021, 5, 4, 3, 2, 1),
            created_at=datetime(2021, 1, 1, 0, 0, 0),
        )
        url = _resource(raw, AGENDA_COLLECTION, event.id)
        elapsed = int((datetime(2021, 5, 4, 3, 2, 1) - datetime(2021, 1, 1)).total_seconds())
        assert _sequence_of(client, url) == _sequence_of(client, url)
        assert _sequence_of(client, url) == elapsed
        assert _value(client.get(_feed(raw, AGENDA_COLLECTION)).text, "SEQUENCE") == str(elapsed)

    def test_sequence_moves_after_an_update(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _stamped_event(
            db_session,
            festival,
            datetime(2021, 5, 4, 3, 2, 1),
            created_at=datetime(2021, 1, 1, 0, 0, 0),
        )
        url = _resource(raw, AGENDA_COLLECTION, event.id)
        before = _sequence_of(client, url)
        event.updated_at = datetime(2021, 6, 1, 0, 0, 0)
        db_session.commit()
        after = _sequence_of(client, url)
        assert after > before
        assert after == int((datetime(2021, 6, 1) - datetime(2021, 1, 1)).total_seconds())

    def test_sequence_is_a_non_negative_integer_whatever_the_row_holds(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        for updated_at, created_at in [
            (None, None),
            (datetime(2030, 1, 1, 0, 0, 0), datetime(2021, 1, 1, 0, 0, 0)),
            (datetime(2019, 1, 1, 0, 0, 0), datetime(2021, 1, 1, 0, 0, 0)),
            (datetime(2021, 1, 1, 0, 0, 0), None),
        ]:
            event = _stamped_event(db_session, festival, updated_at, created_at=created_at)
            value = _value(client.get(_resource(raw, AGENDA_COLLECTION, event.id)).text, "SEQUENCE")
            assert re.fullmatch(r"\d+", value), (updated_at, created_at, value)
            assert int(value) >= 0

    def test_a_category_containing_a_comma_stays_one_value(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        event.event_type = "Rock, Roll & Scream"
        db_session.commit()
        body = client.get(_resource(raw, AGENDA_COLLECTION, event.id)).text
        raw_value = _value(body, "CATEGORIES")
        assert raw_value == '"Rock\\, Roll & Scream"'
        assert _category_list(body) == ["Rock, Roll & Scream"]
        assert len(_values(body, "CATEGORIES")) == 1
        assert raw_value.strip('"').replace("\\,", ",") == "Rock, Roll & Scream"
        assert raw_value.replace('"', "").split(",") == ["Rock\\", " Roll & Scream"]

    def test_a_quote_inside_a_category_is_escaped(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        event.event_type = 'The "Best" of Sitges'
        db_session.commit()
        body = client.get(_resource(raw, AGENDA_COLLECTION, event.id)).text
        assert _value(body, "CATEGORIES") == '"The \\"Best\\" of Sitges"'
        assert _category_list(body) == ['The "Best" of Sitges']

    def test_a_plain_category_keeps_its_visible_name(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        _create_event(db_session, festival, "Opening")
        body = client.get(_feed(raw, AGENDA_COLLECTION)).text
        assert _value(body, "CATEGORIES") == '"screening"'
        assert _category_list(body) == ["screening"]

    def test_an_event_without_a_type_carries_no_categories(self, client, create_user, db_session):
        _, raw = _subscriber(db_session, create_user)
        festival = _create_festival(db_session, "Alpha")
        event = _create_event(db_session, festival, "Opening")
        event.event_type = ""
        db_session.commit()
        body = client.get(_resource(raw, AGENDA_COLLECTION, event.id)).text
        assert _value(body, "CATEGORIES") is None
