"""Auditoría de dependencias contra la base de datos OSV (CVEs y GHSA).

Uso:
    python tools/audit_deps.py --requirements backend/requirements.txt \
        --requirements backend/requirements-dev.txt --lock frontend/pubspec.lock
    python tools/audit_deps.py --venv backend/.venv --fail-on fixable

Sin --fail-on el script solo informa. Con ``--fail-on fixable`` sale con 1 si
existe algún aviso con versión parcheada; con ``--fail-on all`` también cuenta
los avisos sin corrección conocida. `--ignore` permite excluir un GHSA/CVE
cuando el riesgo esté aceptado y documentado.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

OSV_URL = "https://api.osv.dev/v1/querybatch"
ROOT = Path(__file__).resolve().parent.parent
REQ_LINE = re.compile(r"^\s*([A-Za-z0-9_.-]+)\s*(?:\[[^\]]+\])?\s*(?:==|>=|~=|!=|>|<)\s*([0-9][^\s;,]*)")


def read_requirements(path: Path) -> list[dict]:
    queries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        match = REQ_LINE.match(line)
        if match:
            queries.append(
                {"package": {"name": match.group(1), "ecosystem": "PyPI"}, "version": match.group(2)}
            )
    return queries


def read_pubspec_lock(path: Path) -> list[dict]:
    packages: dict[str, str] = {}
    current = None
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^  ([a-zA-Z0-9_]+):\s*$", line)
        if match:
            current = match.group(1)
            continue
        match = re.match(r'^    version: "([^"]+)"', line)
        if match and current:
            packages[current] = match.group(1)
            current = None
    return [
        {"package": {"name": name, "ecosystem": "Pub"}, "version": version}
        for name, version in packages.items()
    ]


def normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def venv_installed(venv: Path) -> dict:
    python = venv / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    code = (
        "import json; from importlib.metadata import distributions; "
        "print(json.dumps({d.metadata['Name']: {'version': d.version, 'requires': d.requires or []} "
        "for d in distributions()}))"
    )
    return json.loads(subprocess.check_output([str(python), "-c", code], text=True))


def read_venv(venv: Path) -> list[dict]:
    installed = venv_installed(venv)
    return [
        {"package": {"name": name, "ecosystem": "PyPI"}, "version": meta["version"]}
        for name, meta in installed.items()
    ]


def show_orphans(venv: Path, requirement_files: list[Path]) -> None:
    """Lista paquetes del venv que no declara nadie ni figuran en requirements."""
    direct = set()
    for path in requirement_files:
        for query in read_requirements(path):
            direct.add(normalize(query["package"]["name"]))

    installed = venv_installed(venv)
    required = set()
    for meta in installed.values():
        for requirement in meta["requires"]:
            match = re.match(r"^\s*([A-Za-z0-9_.-]+)", requirement)
            if match:
                required.add(normalize(match.group(1)))

    basis = {"pip", "setuptools", "wheel"}
    orphans = [
        f"{name}=={meta['version']}"
        for name, meta in sorted(installed.items(), key=lambda item: item[0].lower())
        if normalize(name) not in direct and normalize(name) not in required and normalize(name) not in basis
    ]
    print("Huérfanos del venv:", ", ".join(orphans) if orphans else "ninguno")


def query_osv(queries: list[dict]) -> list[dict]:
    if not queries:
        return []
    payload = json.dumps({"queries": queries}).encode("utf-8")
    request = urllib.request.Request(OSV_URL, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.load(response).get("results", [])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--requirements", action="append", type=Path, default=[])
    parser.add_argument("--lock", action="append", type=Path, default=[])
    parser.add_argument("--venv", type=Path)
    parser.add_argument("--ignore", action="append", default=[], help="ID GHSA/CVE a ignorar")
    parser.add_argument("--show-orphans", action="store_true", help="lista paquetes del venv no declarados")
    parser.add_argument("--fail-on", choices=["none", "fixable", "all"], default="none")
    args = parser.parse_args()

    queries: list[dict] = []
    for path in args.requirements:
        queries.extend(read_requirements(path))
    for path in args.lock:
        queries.extend(read_pubspec_lock(path))
    if args.venv:
        queries.extend(read_venv(args.venv))
    if not queries:
        parser.error("indica --requirements, --lock o --venv")

    if args.show_orphans and args.venv:
        show_orphans(args.venv, args.requirements)

    results = query_osv(queries)
    ignored = set(args.ignore)
    fixable = 0
    unfixable = 0
    for query, result in zip(queries, results):
        advisories = [
            v
            for v in result.get("vulns", [])
            if not ignored.intersection({v.get("id"), *(v.get("aliases") or [])})
        ]
        if not advisories:
            continue
        package = query["package"]
        print(f"{package['ecosystem']} {package['name']} {query['version']}")
        for advisory in advisories:
            patched = any(
                event.get("fixed")
                for affected in advisory.get("affected", [])
                for event_range in affected.get("ranges", [])
                for event in event_range.get("events", [])
            )
            if patched:
                fixable += 1
            else:
                unfixable += 1
            cves = ", ".join(a for a in advisory.get("aliases", []) if a.startswith("CVE")) or "-"
            print(f"  {advisory.get('id')} {cves}: {advisory.get('summary', '')[:100]}")

    print(f"Resumen: {fixable} con corrección disponible, {unfixable} sin corrección conocida")
    if args.fail_on == "fixable" and fixable:
        return 1
    if args.fail_on == "all" and (fixable or unfixable):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
