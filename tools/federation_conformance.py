"""CLI de conformidad para nodos federados de terceros."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import httpx

_BACKEND = Path(__file__).resolve().parents[1] / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from app.services.federation_conformance_service import FederationConformanceService


def _print_report(report: dict) -> None:
    for check in report["checks"]:
        state = "PASS" if check["passed"] else "FAIL"
        print(f"[{state}] {check['id']:<16} {check['severity']:<8} {check['detail']}")
    print(
        f"score={report['score']} passed={report['passed']} failed={report['failed']} "
        f"severe={report['severe_failures']} schema_version={report['schema_version']}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Comprueba la conformidad de un nodo federado"
    )
    parser.add_argument(
        "base_url", help="URL base del nodo (p. ej. https://nodo.ejemplo)"
    )
    parser.add_argument(
        "--json", action="store_true", help="Imprime el informe como JSON"
    )
    args = parser.parse_args(argv)

    with httpx.Client(base_url=args.base_url.rstrip("/"), timeout=10.0) as http_client:
        report = FederationConformanceService(http_client).run()

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        _print_report(report)
    return 1 if report["severe_failures"] > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
