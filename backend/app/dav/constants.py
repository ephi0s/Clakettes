"""CalDAV namespace and constants."""

DAV_NS = "DAV:"
CALDAV_NS = "urn:ietf:params:xml:ns:caldav"
CALSERVER_NS = "http://calendarserver.org/ns/"
ICAL_NS = "urn:ietf:params:xml:ns:ical"

NSMAP = {"D": DAV_NS, "C": CALDAV_NS, "CS": CALSERVER_NS, "I": ICAL_NS}

DAV_COMPLIANCE = "1, 2, 3, extended-mkcol, calendar-access"
DAV_ALLOW = "OPTIONS, GET, HEAD, PROPFIND, REPORT"

CT_XML = "application/xml; charset=utf-8"
CT_CALENDAR = "text/calendar; charset=utf-8"
CT_VEVENT = "text/calendar; charset=utf-8; component=vevent"

PRODID = "-//Clakettes//Agenda//ES"
REALM = "Clakettes"

AGENDA_COLLECTION = "agenda"
FESTIVAL_PREFIX = "festival-"
RESOURCE_SUFFIX = ".ics"

SYNC_TOKEN_PREFIX = "http://clakettes/ns/sync/"
DAV_MAX_EVENTS = 5000
