"""Read-only CalDAV (RFC 4791) surface over the shared agenda.

Only ``GET``/``HEAD``, ``PROPFIND``, ``REPORT`` and ``OPTIONS`` are served.
Every write verb is rejected by a catch-all registered last in this module, so
it can never shadow a real route, and a 307 redirect is never used: clients
send ``PROPFIND``/``REPORT`` with a body that a redirect would drop. Routes are
declared from the widest path to the narrowest so each one is matched before
the catch-alls that follow it.

Two collections are exposed per user — the ``agenda`` pseudo-collection (every
festival the user may see) plus one ``festival-<id>`` collection per festival.
``{principal}`` is either the raw DAV token or ``u<user_id>``, resolved by
:func:`app.dav.auth.resolve_principal_user` and echoed back verbatim.

``xmlbuild`` owns namespace prefixes, parsing and serialisation; this module
only maps them onto HTTP.

``GET``/``HEAD`` on the ICS representations honour ``If-None-Match`` with the
weak comparison of RFC 9110 13.1.2 and answer 304 with no body. The multistatus
verbs do not: they expose ETags as ``<D:getetag>`` properties, not as an HTTP
validator, so there is nothing to revalidate against.
"""

from collections.abc import Iterable, Mapping
from datetime import datetime
from email.utils import formatdate
from functools import partial
from urllib.parse import quote
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dav import auth as dav_auth
from app.dav import constants, xmlbuild
from app.dav.xmlbuild import q
from app.models.event import Event
from app.models.festival import Festival
from app.models.user import User
from app.services.calendar_service import CalendarService
from app.services.dav_service import DavCalendar, DavService

STATUS_MULTISTATUS = 207
NOT_MODIFIED = 304
UTC_BASIC_FORMAT = "%Y%m%dT%H%M%SZ"
HOME_DISPLAY_NAME = "Calendarios"

WEAK_ETAG_PREFIX = "W/"
ANY_ETAG = "*"

WRITE_METHODS = ["PUT", "POST", "DELETE", "PATCH", "MOVE", "COPY", "LOCK", "UNLOCK", "PROPPATCH"]

SUPPORTED_REPORTS = (
    "<D:supported-report>"
    "<D:report><C:calendar-query/></D:report>"
    "<D:report><C:calendar-multiget/></D:report>"
    "<D:report><D:sync-collection/></D:report>"
    "</D:supported-report>"
)
VALID_FILTER_TEST = "<C:valid-filter-test/>"
FINITE_DEPTH = "<D:propfind-finite-depth/>"

CR_SENTINEL = "\ue000"

router = APIRouter()
xmlbuild.register_namespaces()

dav_service = DavService()
calendar_service = CalendarService()


def _dav_method(method: str):
    """Return a route decorator for a WebDAV verb FastAPI does not define."""
    return partial(router.api_route, methods=[method], response_class=Response)


router.propfind = _dav_method("PROPFIND")
router.report = _dav_method("REPORT")


PropertyValue = str | list[Element]
PropertyMap = dict[str, PropertyValue]


def _fragment_elements(fragment: str) -> list[Element]:
    """Parse a raw XML fragment with every ``constants.NSMAP`` prefix bound."""
    decls = "".join(f' xmlns:{prefix}="{uri}"' for prefix, uri in constants.NSMAP.items())
    return list(ET.fromstring(f"<fragment{decls}>{fragment}</fragment>"))


def _href_property(href: str) -> list[Element]:
    """Property value for a link property such as ``<D:owner>``."""
    return [xmlbuild.el(q("D", "href"), text=href)]


def _propstat(properties: Mapping[str, PropertyValue], status: str) -> Element:
    """Build a ``<D:propstat>`` from expanded property names to their values.

    A ``str`` value becomes the text of the property element; a list of
    elements becomes its content. Escaping is left to the serialiser.
    """
    propstat = xmlbuild.el(q("D", "propstat"))
    prop = xmlbuild.child(propstat, q("D", "prop"))
    for name, value in properties.items():
        if isinstance(value, str):
            xmlbuild.child(prop, name, text=value)
        else:
            xmlbuild.child(prop, name).extend(value)
    xmlbuild.child(propstat, q("D", "status"), text=status)
    return propstat


def dav_response(href: str, found: Mapping[str, PropertyValue], missing: Iterable[str] = ()) -> Element:
    """Build a ``<D:response>`` for one href, split into 200 and 404 propstats."""
    element = xmlbuild.el(q("D", "response"))
    xmlbuild.child(element, q("D", "href"), text=href)
    if found:
        element.append(_propstat(found, "HTTP/1.1 200 OK"))
    missing_names = list(missing)
    if missing_names:
        element.append(_propstat(dict.fromkeys(missing_names, ""), "HTTP/1.1 404 Not Found"))
    return element


def error_response(
    status_code: int,
    condition_xml: str = "",
    description: str | None = None,
    headers: dict[str, str] | None = None,
) -> Response:
    """Build an XML ``<D:error>`` body with the given status code.

    ``condition_xml`` is the raw XML placed inside ``<D:error>``, either a
    precondition (``<D:propfind-finite-depth/>``) or a postcondition
    (``<D:supported-report>``).
    """
    root = xmlbuild.el(q("D", "error"))
    for element in _fragment_elements(condition_xml):
        root.append(element)
    if description:
        xmlbuild.child(root, q("D", "responsedescription"), text=description)
    all_headers = dict(headers or {})
    if status_code == 401:
        all_headers.setdefault("WWW-Authenticate", f'Basic realm="{constants.REALM}"')
    return Response(
        content=xmlbuild.document(root),
        status_code=status_code,
        media_type=constants.CT_XML,
        headers=all_headers,
    )


def _multistatus(responses: list[Element]) -> Response:
    """Serialise ``<D:multistatus>`` responses, restoring CRLF inside text.

    ``xmlbuild`` serialises with ElementTree, which would emit a bare CR that
    every XML parser collapses to LF, so calendar data carries a sentinel that
    is turned back into the ``&#13;`` entity here.
    """
    data = xmlbuild.multistatus(responses).replace(CR_SENTINEL.encode("utf-8"), b"&#13;")
    return Response(content=data, status_code=STATUS_MULTISTATUS, media_type=constants.CT_XML)


def _not_found_response(href: str) -> Element:
    """Build a bare 404 ``<D:response>`` for an href that does not resolve."""
    element = xmlbuild.el(q("D", "response"))
    xmlbuild.child(element, q("D", "href"), text=href)
    xmlbuild.child(element, q("D", "status"), text="HTTP/1.1 404 Not Found")
    return element


def _sync_token_response(href: str, token: str) -> Element:
    """Build the collection ``<D:response>`` carrying a sync token."""
    element = xmlbuild.el(q("D", "response"))
    xmlbuild.child(element, q("D", "href"), text=href)
    xmlbuild.child(element, q("D", "sync-token"), text=token)
    return element


def _options_response() -> Response:
    """Advertise the DAV compliance classes and the read-only method set."""
    return Response(
        status_code=200,
        headers={
            "DAV": constants.DAV_COMPLIANCE,
            "Allow": constants.DAV_ALLOW,
            "MS-Author-Via": "DAV",
            "Content-Length": "0",
        },
    )


def _segment(value: str) -> str:
    """Percent-encode a single path segment."""
    return quote(value, safe="")


def _principal_href(principal: str) -> str:
    return f"/dav/{_segment(principal)}/"


def _home_href(principal: str) -> str:
    return f"/dav/{_segment(principal)}/calendars/"


def _collection_href(principal: str, name: str) -> str:
    return f"/dav/{_segment(principal)}/calendars/{_segment(name)}/"


def _resource_href(principal: str, name: str, event_id: int) -> str:
    return f"/dav/{_segment(principal)}/calendars/{_segment(name)}/{event_id}{constants.RESOURCE_SUFFIX}"


def _principal_properties(user: User, principal: str) -> PropertyMap:
    """Properties of the principal collection."""
    href = _href_property(_principal_href(principal))
    return {
        q("D", "resourcetype"): "",
        q("D", "displayname"): user.full_name or user.username or "",
        q("D", "current-user-principal"): href,
        q("D", "principal-URL"): href,
        q("D", "owner"): href,
        q("C", "calendar-home-set"): _href_property(_home_href(principal)),
    }


def _home_properties() -> PropertyMap:
    """Properties of the calendar home collection."""
    return {
        q("D", "resourcetype"): [xmlbuild.el(q("D", "collection"))],
        q("D", "displayname"): HOME_DISPLAY_NAME,
    }


def _collection_properties(calendar: DavCalendar, etag: str | None, principal: str) -> PropertyMap:
    """Properties of a calendar collection."""
    properties: PropertyMap = {
        q("D", "resourcetype"): [xmlbuild.el(q("D", "collection")), xmlbuild.el(q("C", "calendar"))],
        q("D", "displayname"): calendar.display_name or "",
        q("D", "getcontenttype"): constants.CT_CALENDAR,
        q("D", "owner"): _href_property(_principal_href(principal)),
        q("C", "supported-calendar-component-set"): [xmlbuild.el(q("C", "comp"), name="VEVENT")],
        q("C", "supported-calendar-data"): [
            xmlbuild.el(q("C", "calendar-data"), **{"content-type": "text/calendar", "version": "2.0"})
        ],
    }
    if calendar.description:
        properties[q("C", "calendar-description")] = calendar.description
    if etag:
        properties[q("D", "getetag")] = etag
        properties[q("D", "sync-token")] = dav_service.sync_token(etag)
    return properties


def _event_ics(event: Event, calendar: DavCalendar) -> str:
    """ICS body of one event inside a collection."""
    return dav_service.event_ics(event, event.festival, calendar)


def _resource_properties(event: Event, ics: str) -> PropertyMap:
    """Properties of a single VEVENT resource."""
    properties: PropertyMap = {
        q("D", "resourcetype"): "",
        q("D", "getetag"): dav_service.resource_etag(event),
        q("D", "getcontenttype"): constants.CT_VEVENT,
        q("D", "getcontentlength"): str(len(ics.encode("utf-8"))),
        q("C", "calendar-data"): ics.replace("\r", CR_SENTINEL),
    }
    if event.updated_at is not None:
        properties[q("D", "getlastmodified")] = formatdate(event.updated_at.timestamp(), usegmt=True)
    return properties


def _report_properties(event: Event, ics: str) -> PropertyMap:
    """Minimal property set a REPORT returns for each matching resource."""
    return {
        q("D", "resourcetype"): "",
        q("D", "getetag"): dav_service.resource_etag(event),
        q("C", "calendar-data"): ics.replace("\r", CR_SENTINEL),
    }


def _local_name(tag: object) -> str:
    """Local part of an expanded ``{uri}local`` name (prefix-agnostic)."""
    if not isinstance(tag, str):
        return ""
    return tag.rsplit("}", 1)[-1]


def _find_dav(root: Element | None, local: str) -> Element | None:
    """First descendant with the expanded name ``{DAV:}local``."""
    if root is None:
        return None
    target = q("D", local)
    for element in root.iter():
        if element.tag == target:
            return element
    return None


def _prop_mode(root: Element | None) -> tuple[str, list[str]]:
    """Return the requested mode (``prop``/``allprop``/``propname``) and names."""
    prop = _find_dav(root, "prop")
    if prop is not None:
        return "prop", [element.tag for element in prop if isinstance(element.tag, str)]
    if _find_dav(root, "allprop") is not None:
        return "allprop", []
    if _find_dav(root, "propname") is not None:
        return "propname", []
    return "allprop", []


def _apply_properties(available: PropertyMap, mode: str, requested: list[str]) -> tuple[PropertyMap, list[str]]:
    """Split ``available`` into the properties to send and the ones to 404."""
    if mode == "propname":
        return dict.fromkeys(available, ""), []
    if mode == "allprop":
        return dict(available), []
    found = {name: available[name] for name in requested if name in available}
    missing = [name for name in requested if name not in available]
    resourcetype = q("D", "resourcetype")
    if resourcetype in available:
        found.setdefault(resourcetype, available[resourcetype])
    return found, missing


async def _request_body(request: Request) -> Element | Response | None:
    """Parse the request body, returning a 400 response when malformed."""
    try:
        return xmlbuild.parse_body(await request.body())
    except ValueError:
        return error_response(400, description="Malformed XML body")


def _depth(request: Request) -> int | Response:
    """Read the Depth header, answering 400 when it is malformed."""
    try:
        return xmlbuild.request_depth(request)
    except ValueError:
        return error_response(400, FINITE_DEPTH)


def _authenticate(db: Session, request: Request, principal: str) -> User | Response:
    """Resolve the principal segment, falling back to the shared 401 challenge."""
    try:
        return dav_auth.resolve_principal_user(db, principal, request)
    except HTTPException:
        return dav_auth.unauthorized()


def _opaque_etag(tag: str) -> str | None:
    """Opaque value of one entity-tag, with any ``W/`` prefix dropped.

    None means the text is not a well-formed entity-tag.
    """
    if tag.startswith(WEAK_ETAG_PREFIX):
        tag = tag[len(WEAK_ETAG_PREFIX) :]
    if len(tag) < 2 or not tag.startswith('"') or not tag.endswith('"'):
        return None
    return tag[1:-1]


def _etag_matches(if_none_match: str | None, etag: str | None) -> bool:
    """True when ``If-None-Match`` selects the representation identified by ``etag``.

    RFC 9110 13.1.2 gives GET the weak comparison function, so ``W/"x"`` and
    ``"x"`` match one another and only the weak prefix is ignored; the opaque
    tags themselves stay compared byte for byte, because RFC 9110 8.8.3 makes
    that comparison case-sensitive. ``*`` matches because the callers only ask
    once a representation has been resolved and found.

    A header that is present but not a well-formed entity-tag list selects
    nothing rather than failing the request: the worst it can do is answer with
    the full 200 body, which is what a client without the header gets anyway.
    """
    if etag is None or not if_none_match:
        return False
    header = if_none_match.strip()
    if header == ANY_ETAG:
        return True
    current = _opaque_etag(etag)
    if current is None:
        return False
    return any(_opaque_etag(candidate) == current for candidate in (part.strip() for part in header.split(",")))


def _not_modified(headers: dict[str, str]) -> Response:
    """304 carrying the validators of the representation it stands for."""
    return Response(status_code=NOT_MODIFIED, headers=headers)


def _resolve_collection(db: Session, user: User, name: str) -> DavCalendar | None:
    """Find a collection by name.

    Only collections the user can actually reach are returned, so a hidden
    festival, an unknown id or a disabled agenda all resolve to None and the
    caller answers 404 instead of serving an empty calendar.
    """
    return dav_service.calendar_by_name(db, user, name)


def _event_id_from_resource(resource: str) -> int | None:
    """Parse ``<id>.ics`` into an event id, or None when it is not one."""
    suffix = constants.RESOURCE_SUFFIX
    if not resource.endswith(suffix):
        return None
    digits = resource[: -len(suffix)]
    if not digits.isdigit():
        return None
    return int(digits)


def _festivals_by_id(db: Session) -> dict[int, Festival]:
    """Map id to Festival for every festival that feeds a calendar."""
    festivals = db.query(Festival).filter(Festival.is_active.is_(True), Festival.show_in_calendar.is_(True)).all()
    return {festival.id: festival for festival in festivals}


def _time_range(root: Element) -> tuple[datetime, datetime] | None:
    """Read the first VEVENT ``<C:time-range>``; raise ValueError when invalid."""
    for element in root.iter():
        if _local_name(element.tag) != "comp-filter":
            continue
        if (element.get("name") or "").upper() != "VEVENT":
            continue
        for child in element.iter():
            if _local_name(child.tag) != "time-range":
                continue
            start_value = child.get("start")
            end_value = child.get("end")
            if not start_value or not end_value:
                continue
            start = datetime.strptime(start_value, UTC_BASIC_FORMAT)
            end = datetime.strptime(end_value, UTC_BASIC_FORMAT)
            if start >= end:
                raise ValueError("time-range start must precede end")
            return start, end
    return None


def _report_type(root: Element) -> str:
    """Local name of the report element — the body root, else its single child.

    Namespaces are ignored on purpose: a report is matched by local name only.
    """
    own = _local_name(root.tag)
    if own:
        return own
    for element in root:
        if isinstance(element.tag, str):
            return _local_name(element.tag)
    return own


async def _propfind_principal(request: Request, db: Session, principal: str) -> Response:
    """PROPFIND on ``/dav/{principal}/``."""
    user = _authenticate(db, request, principal)
    if isinstance(user, Response):
        return user
    depth = _depth(request)
    if isinstance(depth, Response):
        return depth
    body = await _request_body(request)
    if isinstance(body, Response):
        return body
    mode, requested = _prop_mode(body)
    found, missing = _apply_properties(_principal_properties(user, principal), mode, requested)
    return _multistatus([dav_response(_principal_href(principal), found, missing)])


async def _propfind_home(request: Request, db: Session, principal: str) -> Response:
    """PROPFIND on ``/dav/{principal}/calendars/``."""
    user = _authenticate(db, request, principal)
    if isinstance(user, Response):
        return user
    depth = _depth(request)
    if isinstance(depth, Response):
        return depth
    body = await _request_body(request)
    if isinstance(body, Response):
        return body
    mode, requested = _prop_mode(body)

    home_available = _home_properties()
    home_found, home_missing = _apply_properties(home_available, mode, requested)
    responses = [dav_response(_home_href(principal), home_found, home_missing)]

    if depth >= 1:
        for calendar in dav_service.list_calendars(db, user):
            etag = dav_service.collection_etag(db, user, calendar.festival_id)
            available = _collection_properties(calendar, etag, principal)
            found, missing = _apply_properties(available, mode, requested)
            responses.append(dav_response(_collection_href(principal, calendar.name), found, missing))
    return _multistatus(responses)


async def _propfind_collection(request: Request, db: Session, principal: str, name: str) -> Response:
    """PROPFIND on ``/dav/{principal}/calendars/{collection}/``."""
    user = _authenticate(db, request, principal)
    if isinstance(user, Response):
        return user
    calendar = _resolve_collection(db, user, name)
    if calendar is None:
        return error_response(404, description="Collection not found")
    depth = _depth(request)
    if isinstance(depth, Response):
        return depth
    body = await _request_body(request)
    if isinstance(body, Response):
        return body
    mode, requested = _prop_mode(body)

    etag = dav_service.collection_etag(db, user, calendar.festival_id)
    available = _collection_properties(calendar, etag, principal)
    found, missing = _apply_properties(available, mode, requested)
    responses = [dav_response(_collection_href(principal, calendar.name), found, missing)]

    if depth >= 1:
        for event in dav_service.events(db, user, calendar.festival_id):
            ics = _event_ics(event, calendar)
            resource_available = _resource_properties(event, ics)
            resource_found, resource_missing = _apply_properties(resource_available, mode, requested)
            href = _resource_href(principal, calendar.name, event.id)
            responses.append(dav_response(href, resource_found, resource_missing))
    return _multistatus(responses)


async def _load_event(
    request: Request, db: Session, principal: str, name: str, resource: str
) -> tuple[User, DavCalendar, Event] | Response:
    """Resolve principal, collection and event for a resource path."""
    user = _authenticate(db, request, principal)
    if isinstance(user, Response):
        return user
    calendar = _resolve_collection(db, user, name)
    if calendar is None:
        return error_response(404, description="Collection not found")
    event_id = _event_id_from_resource(resource)
    if event_id is None:
        return error_response(404, description="Resource not found")
    event = dav_service.event(db, user, event_id, calendar.festival_id)
    if event is None:
        return error_response(404, description="Resource not found")
    return user, calendar, event


async def _propfind_resource(request: Request, db: Session, principal: str, name: str, resource: str) -> Response:
    """PROPFIND on a single ``.ics`` resource."""
    loaded = await _load_event(request, db, principal, name, resource)
    if isinstance(loaded, Response):
        return loaded
    _, calendar, event = loaded
    body = await _request_body(request)
    if isinstance(body, Response):
        return body
    mode, requested = _prop_mode(body)
    ics = _event_ics(event, calendar)
    found, missing = _apply_properties(_resource_properties(event, ics), mode, requested)
    href = _resource_href(principal, calendar.name, event.id)
    return _multistatus([dav_response(href, found, missing)])


async def _report_collection(request: Request, db: Session, principal: str, name: str) -> Response:
    """REPORT on ``/dav/{principal}/calendars/{collection}/``."""
    user = _authenticate(db, request, principal)
    if isinstance(user, Response):
        return user
    calendar = _resolve_collection(db, user, name)
    if calendar is None:
        return error_response(404, description="Collection not found")
    body = await _request_body(request)
    if isinstance(body, Response):
        return body
    if body is None:
        return error_response(400, description="REPORT requires a body")

    report = _report_type(body)
    if report == "calendar-query":
        return await _report_calendar_query(body, db, user, principal, calendar)
    if report == "calendar-multiget":
        return await _report_calendar_multiget(body, db, user, principal, calendar)
    if report == "sync-collection":
        return _report_sync_collection(body, db, user, principal, calendar)
    if report == "principal-search-property-set":
        href = _principal_href(principal)
        return _multistatus([dav_response(href, {q("D", "principal-search-property-set"): ""})])
    return error_response(403, SUPPORTED_REPORTS, description=f"Unsupported report {report}")


async def _report_calendar_query(
    body: Element, db: Session, user: User, principal: str, calendar: DavCalendar
) -> Response:
    """REPORT ``calendar-query`` — filtered events of one collection."""
    try:
        window = _time_range(body)
    except ValueError:
        return error_response(403, VALID_FILTER_TEST, description="Invalid time-range")

    festival_ids = [calendar.festival_id] if calendar.festival_id is not None else None
    query = calendar_service.visible_events_query(db, user, festival_ids)
    if window is not None:
        start, end = window
        query = query.filter(func.coalesce(Event.end_date, Event.start_date) >= start, Event.start_date <= end)
    events = query.order_by(Event.start_date, Event.sort_order, Event.id).limit(constants.DAV_MAX_EVENTS).all()

    mode, requested = _prop_mode(body)
    responses = []
    for event in events:
        ics = _event_ics(event, calendar)
        found, missing = _apply_properties(_report_properties(event, ics), mode, requested)
        href = _resource_href(principal, calendar.name, event.id)
        responses.append(dav_response(href, found, missing))
    return _multistatus(responses)


async def _report_calendar_multiget(
    body: Element, db: Session, user: User, principal: str, calendar: DavCalendar
) -> Response:
    """REPORT ``calendar-multiget`` — the exact hrefs the client asked for."""
    mode, requested = _prop_mode(body)
    responses = []
    for element in body.iter():
        if element.tag != q("D", "href"):
            continue
        href = (element.text or "").strip()
        segment = href.rstrip("/").rsplit("/", 1)[-1]
        event_id = _event_id_from_resource(segment)
        event = None
        if event_id is not None:
            event = dav_service.event(db, user, event_id, calendar.festival_id)
        if event is None:
            responses.append(_not_found_response(href))
            continue
        ics = _event_ics(event, calendar)
        found, missing = _apply_properties(_report_properties(event, ics), mode, requested)
        responses.append(dav_response(href, found, missing))
    return _multistatus(responses)


def _report_sync_collection(body: Element, db: Session, user: User, principal: str, calendar: DavCalendar) -> Response:
    """REPORT ``sync-collection`` — full listing, or 204 when nothing changed."""
    level = xmlbuild.find_text(body, q("D", "sync-level"))
    if level is not None and level.strip().lower() not in ("1", "infinite"):
        return error_response(403, "<D:supported-report/>", description="Only sync-level 1 is supported")

    etag = dav_service.collection_etag(db, user, calendar.festival_id)
    token = xmlbuild.find_text(body, q("D", "sync-token"))
    incoming = dav_service.etag_from_sync_token(token)
    if incoming is not None and etag is not None and incoming == etag:
        return Response(status_code=204)

    mode, requested = _prop_mode(body)
    responses = []
    if etag:
        responses.append(_sync_token_response(_collection_href(principal, calendar.name), dav_service.sync_token(etag)))
    for event in dav_service.events(db, user, calendar.festival_id):
        ics = _event_ics(event, calendar)
        found, missing = _apply_properties(_report_properties(event, ics), mode, requested)
        href = _resource_href(principal, calendar.name, event.id)
        responses.append(dav_response(href, found, missing))
    return _multistatus(responses)


async def _report_principal_or_home(request: Request, db: Session, principal: str, href: str) -> Response:
    """REPORT on the principal or the calendar home."""
    user = _authenticate(db, request, principal)
    if isinstance(user, Response):
        return user
    body = await _request_body(request)
    if isinstance(body, Response):
        return body
    if body is None:
        return error_response(400, description="REPORT requires a body")

    report = _report_type(body)
    if report == "calendar-home-set":
        link = _href_property(_home_href(principal))
        return _multistatus([dav_response(href, {q("C", "calendar-home-set"): link})])
    if report == "principal-search-property-set":
        return _multistatus([dav_response(href, {q("D", "principal-search-property-set"): ""})])
    return error_response(403, SUPPORTED_REPORTS, description=f"Unsupported report {report}")


async def _get_feed(request: Request, db: Session, principal: str, name: str) -> Response:
    """GET ``/dav/{principal}/calendars/{collection}.ics`` — the whole feed."""
    user = _authenticate(db, request, principal)
    if isinstance(user, Response):
        return user
    calendar = _resolve_collection(db, user, name)
    if calendar is None:
        return error_response(404, description="Collection not found")
    events = dav_service.events(db, user, calendar.festival_id)
    ics = dav_service.feed_ics(events, _festivals_by_id(db), calendar)
    headers = {"Content-Disposition": f'inline; filename="{calendar.name}{constants.RESOURCE_SUFFIX}"'}
    etag = dav_service.collection_etag(db, user, calendar.festival_id)
    if etag:
        headers["ETag"] = etag
    if _etag_matches(request.headers.get("if-none-match"), etag):
        return _not_modified(headers)
    return Response(content=ics.encode("utf-8"), media_type=constants.CT_CALENDAR, headers=headers)


async def _get_resource(request: Request, db: Session, principal: str, name: str, resource: str) -> Response:
    """GET a single ``.ics`` resource."""
    loaded = await _load_event(request, db, principal, name, resource)
    if isinstance(loaded, Response):
        return loaded
    _, calendar, event = loaded
    ics = _event_ics(event, calendar)
    headers = {"ETag": dav_service.resource_etag(event)}
    if _etag_matches(request.headers.get("if-none-match"), headers["ETag"]):
        return _not_modified(headers)
    return Response(content=ics.encode("utf-8"), media_type=constants.CT_VEVENT, headers=headers)


@router.options("/", include_in_schema=False)
async def options_root() -> Response:
    """OPTIONS on the DAV root."""
    return _options_response()


@router.options("/{dav_path:path}", include_in_schema=False)
async def options_any(dav_path: str) -> Response:
    """OPTIONS on any DAV path.

    Registered before the principal routes so every DAV URL advertises the
    compliance classes, authenticated or not.
    """
    return _options_response()


@router.propfind("/")
async def propfind_root(request: Request, db: Session = Depends(get_db)) -> Response:
    """Resolve the credentialed user, or challenge it with a 401."""
    token = dav_auth.token_from_request(request)
    user = dav_auth.user_by_token(db, token) if token else None
    if user is None or not user.is_active:
        return error_response(401, description="Authentication required")
    link = _href_property(_principal_href(token))
    return _multistatus([dav_response("/dav/", {q("D", "current-user-principal"): link})])


@router.get("/{principal}/calendars/{collection}.ics", operation_id="get_feed")
async def get_feed(request: Request, principal: str, collection: str, db: Session = Depends(get_db)) -> Response:
    """Download a whole collection as one ICS file (the webcal:// target).

    Registered before the collection routes so a name ending in ``.ics`` is
    never mistaken for a collection.
    """
    return await _get_feed(request, db, principal, collection)


@router.head("/{principal}/calendars/{collection}.ics", operation_id="get_feed_head")
async def get_feed_head(request: Request, principal: str, collection: str, db: Session = Depends(get_db)) -> Response:
    """HEAD variant of get_feed (headers only, no body)."""
    return await _get_feed(request, db, principal, collection)


@router.get("/{principal}/calendars/{collection}/{resource}", operation_id="get_resource")
async def get_resource(
    request: Request, principal: str, collection: str, resource: str, db: Session = Depends(get_db)
) -> Response:
    """Download a single event as an ICS file."""
    return await _get_resource(request, db, principal, collection, resource)


@router.head("/{principal}/calendars/{collection}/{resource}", operation_id="get_resource_head")
async def get_resource_head(
    request: Request, principal: str, collection: str, resource: str, db: Session = Depends(get_db)
) -> Response:
    """HEAD variant of get_resource (headers only, no body)."""
    return await _get_resource(request, db, principal, collection, resource)


@router.api_route(
    "/{principal}/calendars/{collection}/{resource}/",
    methods=["GET", "HEAD"],
    include_in_schema=False,
)
async def get_resource_slash(
    request: Request, principal: str, collection: str, resource: str, db: Session = Depends(get_db)
) -> Response:
    """Same as get_resource, for clients that append a trailing slash."""
    return await _get_resource(request, db, principal, collection, resource)


@router.api_route(
    "/{principal}/calendars/{collection}/{resource}",
    methods=["PROPFIND"],
    operation_id="propfind_resource_propfind",
)
@router.api_route(
    "/{principal}/calendars/{collection}/{resource}",
    methods=["REPORT"],
    operation_id="propfind_resource_report",
)
async def propfind_resource(
    request: Request, principal: str, collection: str, resource: str, db: Session = Depends(get_db)
) -> Response:
    """Describe a single ``.ics`` resource."""
    return await _propfind_resource(request, db, principal, collection, resource)


@router.api_route(
    "/{principal}/calendars/{collection}/{resource}/",
    methods=["PROPFIND", "REPORT"],
    include_in_schema=False,
)
async def propfind_resource_slash(
    request: Request, principal: str, collection: str, resource: str, db: Session = Depends(get_db)
) -> Response:
    """Same as propfind_resource, for clients that append a trailing slash."""
    return await _propfind_resource(request, db, principal, collection, resource)


@router.propfind("/{principal}/calendars/{collection}/")
async def propfind_collection(
    request: Request, principal: str, collection: str, db: Session = Depends(get_db)
) -> Response:
    """List a collection, and its events at Depth 1."""
    return await _propfind_collection(request, db, principal, collection)


@router.propfind("/{principal}/calendars/{collection}", include_in_schema=False)
async def propfind_collection_no_slash(
    request: Request, principal: str, collection: str, db: Session = Depends(get_db)
) -> Response:
    """Same as propfind_collection, without the trailing slash."""
    return await _propfind_collection(request, db, principal, collection)


@router.report("/{principal}/calendars/{collection}/")
async def report_collection(
    request: Request, principal: str, collection: str, db: Session = Depends(get_db)
) -> Response:
    """Run a calendar-query, calendar-multiget or sync-collection report."""
    return await _report_collection(request, db, principal, collection)


@router.report("/{principal}/calendars/{collection}", include_in_schema=False)
async def report_collection_no_slash(
    request: Request, principal: str, collection: str, db: Session = Depends(get_db)
) -> Response:
    """Same as report_collection, without the trailing slash."""
    return await _report_collection(request, db, principal, collection)


@router.propfind("/{principal}/calendars/")
async def propfind_home(request: Request, principal: str, db: Session = Depends(get_db)) -> Response:
    """List the calendar home, and its collections at Depth 1."""
    return await _propfind_home(request, db, principal)


@router.propfind("/{principal}/calendars", include_in_schema=False)
async def propfind_home_no_slash(request: Request, principal: str, db: Session = Depends(get_db)) -> Response:
    """Same as propfind_home, without the trailing slash."""
    return await _propfind_home(request, db, principal)


@router.propfind("/{principal}/")
async def propfind_principal(request: Request, principal: str, db: Session = Depends(get_db)) -> Response:
    """Describe the principal collection."""
    return await _propfind_principal(request, db, principal)


@router.propfind("/{principal}", include_in_schema=False)
async def propfind_principal_no_slash(request: Request, principal: str, db: Session = Depends(get_db)) -> Response:
    """Same as propfind_principal, without the trailing slash."""
    return await _propfind_principal(request, db, principal)


@router.report("/{principal}/calendars/")
async def report_home(request: Request, principal: str, db: Session = Depends(get_db)) -> Response:
    """Run a report that targets the calendar home itself."""
    return await _report_principal_or_home(request, db, principal, _home_href(principal))


@router.report("/{principal}/calendars", include_in_schema=False)
async def report_home_no_slash(request: Request, principal: str, db: Session = Depends(get_db)) -> Response:
    """Same as report_home, without the trailing slash."""
    return await _report_principal_or_home(request, db, principal, _home_href(principal))


@router.report("/{principal}/")
async def report_principal(request: Request, principal: str, db: Session = Depends(get_db)) -> Response:
    """Run a report that targets the principal collection."""
    return await _report_principal_or_home(request, db, principal, _principal_href(principal))


@router.report("/{principal}", include_in_schema=False)
async def report_principal_no_slash(request: Request, principal: str, db: Session = Depends(get_db)) -> Response:
    """Same as report_principal, without the trailing slash."""
    return await _report_principal_or_home(request, db, principal, _principal_href(principal))


@router.api_route("/{write_path:path}", methods=WRITE_METHODS, include_in_schema=False)
async def write_not_allowed(write_path: str) -> Response:
    """Reject every write verb: the server is read-only.

    Registered last in this module so it can only catch what nothing else
    matched.
    """
    return error_response(405, description="Read-only CalDAV server", headers={"Allow": constants.DAV_ALLOW})
