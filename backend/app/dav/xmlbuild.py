"""Utilities for building and parsing WebDAV multistatus XML."""

from collections.abc import Iterable, Mapping
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

from fastapi import Request

from app.dav import constants


def q(prefix: str, local: str) -> str:
    """Expand a namespace prefix to '{uri}local'."""
    if prefix == "D":
        return f"{{{constants.DAV_NS}}}{local}"
    if prefix == "C":
        return f"{{{constants.CALDAV_NS}}}{local}"
    if prefix == "CS":
        return f"{{{constants.CALSERVER_NS}}}{local}"
    if prefix == "I":
        return f"{{{constants.ICAL_NS}}}{local}"
    return local


def register_namespaces() -> None:
    """Call ElementTree.register_namespace for every entry in constants.NSMAP."""
    for prefix, uri in constants.NSMAP.items():
        ET.register_namespace(prefix, uri)


def el(qname: str, text: str | None = None, **attrs: str) -> Element:
    element = ET.Element(qname)
    if text is not None:
        element.text = text
    for key, value in attrs.items():
        element.set(key, value)
    return element


def child(parent: Element, qname: str, text: str | None = None, **attrs: str) -> Element:
    element = el(qname, text, **attrs)
    parent.append(element)
    return element


def sub_xml(parent: Element, qname: str, inner_xml: str) -> None:
    """Append a raw XML fragment string as the children of `qname`."""
    root = ET.Element("root")
    for prefix, uri in constants.NSMAP.items():
        root.set(f"xmlns:{prefix}", uri)
    try:
        fragment = ET.fromstring(f"<root>{inner_xml}</root>")
    except ET.ParseError as exc:
        raise ValueError(f"Invalid XML fragment: {exc}") from exc
    target = el(qname)
    for item in list(fragment):
        target.append(item)
    parent.append(target)


def document(root: Element) -> bytes:
    """Serialize with an XML declaration, UTF-8, no pretty printing."""
    register_namespaces()
    data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    return data


def multistatus(responses: Iterable[Element]) -> bytes:
    """Build the <D:multistatus> root, append each response child, return bytes."""
    ms = el(q("D", "multistatus"))
    for response_el in responses:
        ms.append(response_el)
    return document(ms)


def response(href: str, found: Mapping[str, str], missing: Iterable[str] = ()) -> Element:
    """Build a <D:response> for one href."""
    resp = el(q("D", "response"))
    child(resp, q("D", "href"), text=href)
    if found:
        propstat_ok = el(q("D", "propstat"))
        prop_ok = child(propstat_ok, q("D", "prop"))
        for prop_name, inner_xml in found.items():
            sub_xml(prop_ok, prop_name, inner_xml)
        child(propstat_ok, q("D", "status"), text="HTTP/1.1 200 OK")
        resp.append(propstat_ok)
    missing_list = list(missing)
    if missing_list:
        propstat_nf = el(q("D", "propstat"))
        prop_nf = child(propstat_nf, q("D", "prop"))
        for prop_name in missing_list:
            el_el = el(prop_name)
            prop_nf.append(el_el)
        child(propstat_nf, q("D", "status"), text="HTTP/1.1 404 Not Found")
        resp.append(propstat_nf)
    return resp


def parse_body(body: bytes | None) -> Element | None:
    """Parse a request body into a root Element."""
    if not body:
        return None
    data = body.lstrip()
    if data.startswith(b"\xef\xbb\xbf"):
        data = data[3:]
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise ValueError("malformed xml") from exc
    return root


def find_text(root: Element, qname: str) -> str | None:
    """Text of the first direct-or-nested descendant with that expanded name."""
    for elem in root.iter():
        if elem.tag == qname:
            text = elem.text
            if text is None:
                return None
            stripped = text.strip()
            return stripped if stripped else None
    return None


def findall_text(root: Element, qname: str) -> list[str]:
    results: list[str] = []
    for elem in root.iter():
        if elem.tag == qname:
            text = elem.text
            if text is not None:
                stripped = text.strip()
                if stripped:
                    results.append(stripped)
    return results


def request_depth(request: Request) -> int:
    """Read the 'Depth' header."""
    depth = request.headers.get("depth")
    if depth is None:
        return 1
    depth_stripped = depth.strip().lower()
    if depth_stripped == "0":
        return 0
    if depth_stripped == "1":
        return 1
    if depth_stripped == "infinity":
        return 2**31 - 1
    raise ValueError("invalid depth")
