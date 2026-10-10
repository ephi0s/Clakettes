"""Export services — form responses (CSV), registrations (CSV/PDF), attendees (CSV), events (ICS/PDF).

CSV/ICS son stdlib puro (rápidos, sin dependencias). PDF usa reportlab con
import perezoso dentro de _build_pdf para no pagar ~200 ms de import ni
memoria en arranques/peticiones que solo exportan CSV/ICS.
"""

import csv
from datetime import datetime, timedelta, timezone
from io import BytesIO, StringIO
from xml.sax.saxutils import escape

from sqlalchemy.orm import Session, selectinload

from app.models.form_definition import (
    FormDefinition,
    FormPage,
    FormField,
    FormResponse,
    FormFieldResponse,
)
from app.enums import FormFieldType


def _to_csv(headers: list[str], rows: list[list]) -> StringIO:
    """Build a UTF-8 BOM CSV buffer from headers and rows."""
    csv_buffer = StringIO()
    csv_buffer.write("\ufeff")
    writer = csv.writer(csv_buffer)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    csv_buffer.seek(0)
    return csv_buffer


def _utc_format(dt: datetime) -> str:
    """Format a datetime as an ICS UTC timestamp (YYYYMMDDTHHMMSSZ)."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _ics_text(value) -> str:
    """Escape ICS text value (backslash, semicolon, comma, newline)."""
    return (
        str(value).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\r", "").replace("\n", "\\n")
    )


ICS_MAX_LINE_OCTETS = 75


def ics_fold(line: str) -> list[str]:
    """Split one content line into folded lines of at most 75 octets each.

    Folding counts octets, not characters, and never cuts inside a UTF-8
    multi-byte sequence: a cut that would land on a continuation byte moves back
    to the preceding character boundary. Every continuation carries a single
    leading space, so the leading space is budgeted out of the 75 octets it
    still leaves for content.
    """
    data = line.encode("utf-8")
    if len(data) <= ICS_MAX_LINE_OCTETS:
        return [line]
    chunks: list[str] = []
    budget = ICS_MAX_LINE_OCTETS
    while data:
        cut = budget
        while 1 < cut < len(data) and (data[cut] & 0xC0) == 0x80:
            cut -= 1
        chunks.append(data[:cut].decode("utf-8"))
        data = data[cut:]
        budget = ICS_MAX_LINE_OCTETS - 1
    return chunks


def ics_calendar_body(lines: list[str]) -> str:
    """Join content lines into an iCalendar stream: folded, CRLF terminated."""
    physical: list[str] = []
    for line in lines:
        chunks = ics_fold(line)
        physical.append(chunks[0])
        physical.extend(" " + chunk for chunk in chunks[1:])
    return "\r\n".join(physical) + "\r\n"


def _pdf_text(value) -> str:
    """Convert a value to Latin-1 text so reportlab standard fonts never fail."""
    if value is None:
        return ""
    return str(value).encode("latin-1", errors="replace").decode("latin-1")


def export_form_responses_csv(db: Session, form_id: int) -> StringIO:
    form = (
        db.query(FormDefinition)
        .options(selectinload(FormDefinition.pages).selectinload(FormPage.fields).selectinload(FormField.options))
        .filter(FormDefinition.id == form_id)
        .first()
    )
    if not form:
        raise ValueError("Form not found")

    fields: list[FormField] = []
    for page in form.pages:
        fields.extend(sorted(page.fields, key=lambda f: f.sort_order))

    field_map: dict[int, FormField] = {}
    option_map: dict[int, dict[str, str]] = {}
    for field in fields:
        field_map[field.id] = field
        option_map[field.id] = {opt.value: opt.label for opt in field.options}

    responses = (
        db.query(FormResponse)
        .options(selectinload(FormResponse.field_responses))
        .filter(FormResponse.form_id == form_id)
        .order_by(FormResponse.created_at)
        .all()
    )

    csv_buffer = StringIO()
    csv_buffer.write("\ufeff")
    writer = csv.writer(csv_buffer)

    headers = [f.label for f in fields]
    writer.writerow(headers)

    for response in responses:
        row = [""] * len(fields)
        fr_map: dict[int, FormFieldResponse] = {}
        for fr in response.field_responses:
            fr_map[fr.field_id] = fr
        for idx, field in enumerate(fields):
            fr = fr_map.get(field.id)
            if fr is None or fr.value is None:
                continue
            val = fr.value
            ftype = field.field_type.value if hasattr(field.field_type, "value") else field.field_type
            if ftype == FormFieldType.SELECT.value:
                row[idx] = option_map.get(field.id, {}).get(str(val), str(val))
            elif ftype == FormFieldType.MULTISELECT.value:
                if isinstance(val, list):
                    labels = []
                    for v in val:
                        label = option_map.get(field.id, {}).get(str(v), str(v))
                        labels.append(label)
                    row[idx] = "; ".join(labels)
                else:
                    row[idx] = str(val)
            else:
                row[idx] = str(val) if val is not None else ""
        writer.writerow(row)

    csv_buffer.seek(0)
    return csv_buffer


def export_registrations_csv(festival) -> StringIO:
    """CSV of FestivalRegistration rows for a festival."""
    headers = ["id", "username", "full_name", "email", "status", "created_at", "notes"]
    rows = []
    for reg in festival.registrations:
        user = reg.user
        status = reg.status.value if hasattr(reg.status, "value") else reg.status
        rows.append(
            [
                reg.id,
                user.username if user else "",
                user.full_name if user else "",
                user.email if user else "",
                status,
                reg.created_at.isoformat() if reg.created_at else "",
                reg.notes or "",
            ]
        )
    return _to_csv(headers, rows)


def export_attendees_csv(event) -> StringIO:
    """CSV of EventAttendee rows for an event."""
    headers = ["id", "user", "guest_name", "email", "ticket_type", "status", "checked_in_at"]
    rows = []
    for att in event.attendees:
        user = att.user
        email = user.email if user else (att.guest_email or "")
        rows.append(
            [
                att.id,
                user.username if user else "",
                att.guest_name or "",
                email,
                att.ticket_type.name if att.ticket_type else "",
                att.status,
                att.checked_in_at.isoformat() if att.checked_in_at else "",
            ]
        )
    return _to_csv(headers, rows)


def export_events_ics(festival) -> str:
    """ICS calendar string with one VEVENT per Event of the festival."""
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Clakettes//Festival//ES",
        f"X-WR-CALNAME:{_ics_text(festival.name)}",
    ]
    now = _utc_format(datetime.now(timezone.utc))
    for event in festival.events:
        start = event.start_date
        end = event.end_date or (start + timedelta(hours=1))
        if end <= start:
            end = start + timedelta(hours=1)
        dtstart = _utc_format(start)
        dtend = _utc_format(end)
        lines.append("BEGIN:VEVENT")
        lines.append(f"UID:event-{event.id}@clakettes")
        lines.append(f"DTSTAMP:{now}")
        lines.append(f"DTSTART:{dtstart}")
        lines.append(f"DTEND:{dtend}")
        lines.append(f"SUMMARY:{_ics_text(event.title)}")
        location = event.venue or event.location
        if location:
            lines.append(f"LOCATION:{_ics_text(location)}")
        description = event.short_description or event.description
        if description:
            lines.append(f"DESCRIPTION:{_ics_text(description)}")
        lines.append(f"CATEGORIES:{_ics_text(event.event_type)}")
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return ics_calendar_body(lines)


def export_registrations_pdf(festival) -> bytes:
    """PDF report with a table of FestivalRegistration rows for a festival."""
    headers = ["id", "username", "full_name", "email", "status", "created_at", "notes"]
    rows = []
    for reg in festival.registrations:
        user = reg.user
        status = reg.status.value if hasattr(reg.status, "value") else reg.status
        rows.append(
            [
                reg.id,
                user.username if user else "",
                user.full_name if user else "",
                user.email if user else "",
                status,
                reg.created_at.isoformat() if reg.created_at else "",
                reg.notes or "",
            ]
        )
    return _build_pdf(festival.name, "Registrations", headers, rows)


def export_events_pdf(festival) -> bytes:
    """PDF report listing the Events of a festival."""
    headers = ["title", "start_date", "end_date", "location", "event_type"]
    rows = []
    for event in festival.events:
        rows.append(
            [
                event.title,
                event.start_date.isoformat() if event.start_date else "",
                event.end_date.isoformat() if event.end_date else "",
                event.venue or event.location or "",
                event.event_type,
            ]
        )
    return _build_pdf(festival.name, "Events", headers, rows)


def _build_pdf(title: str, subtitle: str, headers: list[str], rows: list[list]) -> bytes:
    """Render a titled table report to PDF bytes."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("title", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=18)
    heading_style = ParagraphStyle("heading", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=14)
    cell_style = ParagraphStyle("cell", parent=styles["BodyText"], fontName="Helvetica", fontSize=8)

    story = [Paragraph(escape(_pdf_text(title)), title_style), Spacer(1, 12)]
    if subtitle:
        story.append(Paragraph(escape(_pdf_text(subtitle)), heading_style))
        story.append(Spacer(1, 12))

    table_data = [[Paragraph(_pdf_text(h), cell_style) for h in headers]]
    for row in rows:
        table_data.append([Paragraph(_pdf_text(c), cell_style) for c in row])
    table = Table(table_data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#B8956E")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
            ]
        )
    )
    story.append(table)
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
