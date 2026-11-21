"""Conformance checks for third-party Clakettes federation nodes."""

from __future__ import annotations

import base64
import json
from typing import Any

SEVERE_SEVERITIES = {"critical", "high"}


class FederationConformanceService:
    def __init__(self, client: Any, base_url: str = ""):
        self._client = client
        self._base_url = (base_url or "").rstrip("/")
        self._schema_version: str | None = None

    def _url(self, path: str) -> str:
        return f"{self._base_url}{path}"

    def _call(self, method: str, path: str, payload: dict | None = None) -> tuple[int | None, dict, str | None]:
        try:
            if method == "POST":
                response = self._client.post(self._url(path), json=payload)
            else:
                response = self._client.get(self._url(path))
        except Exception as exc:
            return None, {}, f"{type(exc).__name__}: {exc}"
        status = getattr(response, "status_code", None)
        try:
            data = response.json()
            if not isinstance(data, dict):
                data = {"value": data}
        except Exception:
            data = {}
        return status, data, None

    @staticmethod
    def _result(check_id: str, name: str, severity: str, passed: bool, detail: str) -> dict:
        return {"id": check_id, "name": name, "passed": passed, "detail": detail, "severity": severity}

    def _check_manifest(self) -> dict:
        status, data, error = self._call("GET", "/api/federation/manifest")
        if error is not None:
            return self._result("manifest", "Manifiesto firmado", "critical", False, f"request_error: {error}")
        if status is None or status >= 400:
            return self._result("manifest", "Manifiesto firmado", "critical", False, "manifest_unavailable")
        if "schema_version" not in data:
            return self._result("manifest", "Manifiesto firmado", "critical", False, "manifest_schema_version_missing")
        self._schema_version = str(data["schema_version"])
        if not data.get("signature"):
            return self._result("manifest", "Manifiesto firmado", "critical", False, "manifest_signature_missing")
        if not isinstance(data.get("certificate_chain"), list):
            return self._result(
                "manifest", "Manifiesto firmado", "critical", False, "manifest_certificate_chain_missing"
            )
        return self._result("manifest", "Manifiesto firmado", "critical", True, "manifest_ok")

    def _check_jwks(self) -> dict:
        status, data, error = self._call("GET", "/api/federation/.well-known/jwks.json")
        if error is not None:
            return self._result("jwks", "JWKS publicado", "high", False, f"request_error: {error}")
        if status is None or status >= 400:
            return self._result("jwks", "JWKS publicado", "high", False, "jwks_unavailable")
        keys = data.get("keys")
        if not isinstance(keys, list) or not keys:
            return self._result("jwks", "JWKS publicado", "high", False, "jwks_empty")
        key = keys[0] if isinstance(keys[0], dict) else {}
        if key.get("kty") != "RSA" or key.get("alg") not in (None, "RS256") or not key.get("n") or not key.get("e"):
            return self._result("jwks", "JWKS publicado", "high", False, "jwks_invalid")
        return self._result("jwks", "JWKS publicado", "high", True, "jwks_ok")

    def _check_token(self) -> dict:
        status, data, error = self._call("POST", "/api/federation/token", {"subject": "conformance-probe"})
        if error is not None:
            return self._result("token", "Emisión de token RS256", "high", False, f"request_error: {error}")
        if status in (404, 405):
            return self._result("token", "Emisión de token RS256", "high", False, "token_endpoint_missing")
        if status is not None and status >= 500:
            return self._result("token", "Emisión de token RS256", "high", False, "token_server_error")
        if status in (401, 403):
            return self._result("token", "Emisión de token RS256", "high", True, "token_endpoint_protected")
        if status in (200, 201):
            token = data.get("access_token")
            if not isinstance(token, str) or not token:
                return self._result("token", "Emisión de token RS256", "high", False, "token_missing")
            try:
                header = json.loads(base64.urlsafe_b64decode(token.split(".")[0] + "=="))
            except Exception:
                return self._result("token", "Emisión de token RS256", "high", False, "token_malformed")
            if header.get("alg") != "RS256":
                return self._result("token", "Emisión de token RS256", "high", False, "token_not_rs256")
            return self._result("token", "Emisión de token RS256", "high", True, "token_rs256")
        return self._result("token", "Emisión de token RS256", "high", True, "token_endpoint_present")

    def _check_directory(self) -> dict:
        status, data, error = self._call("GET", "/api/federation/directory")
        if error is not None:
            return self._result("directory", "Directorio de nodos", "medium", False, f"request_error: {error}")
        if status is None or status >= 400:
            return self._result("directory", "Directorio de nodos", "medium", False, "directory_unavailable")
        if not isinstance(data.get("nodes"), list):
            return self._result("directory", "Directorio de nodos", "medium", False, "directory_invalid")
        return self._result("directory", "Directorio de nodos", "medium", True, "directory_ok")

    def _check_peers_verify(self) -> dict:
        status, _data, error = self._call("POST", "/api/federation/peers/verify", {})
        if error is not None:
            return self._result("peers_verify", "Verificación de pares", "medium", False, f"request_error: {error}")
        if status in (404, 405):
            return self._result("peers_verify", "Verificación de pares", "medium", False, "peers_verify_missing")
        if status is not None and status >= 500:
            return self._result("peers_verify", "Verificación de pares", "medium", False, "peers_verify_server_error")
        return self._result("peers_verify", "Verificación de pares", "medium", True, "peers_verify_present")

    def _check_user_resolution(self) -> dict:
        status, data, error = self._call("GET", "/api/federation/users/conformance-probe")
        if error is not None:
            return self._result("user_resolution", "Resolución de usuarios", "low", False, f"request_error: {error}")
        if status == 200:
            return self._result("user_resolution", "Resolución de usuarios", "low", True, "user_resolved")
        if status in (401, 403):
            return self._result("user_resolution", "Resolución de usuarios", "low", True, "user_endpoint_protected")
        if status == 404 and "user" in str(data.get("detail", "")).lower():
            return self._result("user_resolution", "Resolución de usuarios", "low", True, "user_endpoint_present")
        return self._result("user_resolution", "Resolución de usuarios", "low", False, "user_endpoint_missing")

    def _check_webfinger(self) -> dict:
        path = "/api/federation/.well-known/webfinger?resource=conformance@example.invalid"
        status, data, error = self._call("GET", path)
        if error is not None:
            return self._result("webfinger", "WebFinger", "low", False, f"request_error: {error}")
        if status == 200:
            return self._result("webfinger", "WebFinger", "low", True, "webfinger_resolved")
        if status in (401, 403):
            return self._result("webfinger", "WebFinger", "low", True, "webfinger_protected")
        if status == 404 and "user" in str(data.get("detail", "")).lower():
            return self._result("webfinger", "WebFinger", "low", True, "webfinger_endpoint_present")
        return self._result("webfinger", "WebFinger", "low", False, "webfinger_missing")

    def _check_reports(self) -> dict:
        status, _data, error = self._call("POST", "/api/federation/reports", {})
        if error is not None:
            return self._result("reports", "Reportes de moderación", "medium", False, f"request_error: {error}")
        if status in (404, 405):
            return self._result("reports", "Reportes de moderación", "medium", False, "reports_missing")
        if status is not None and status >= 500:
            return self._result("reports", "Reportes de moderación", "medium", False, "reports_server_error")
        return self._result("reports", "Reportes de moderación", "medium", True, "reports_present")

    def _check_portability(self) -> dict:
        status, _data, error = self._call("POST", "/api/federation/portability/bundles", {})
        if error is not None:
            return self._result("portability", "Portabilidad de bundles", "medium", False, f"request_error: {error}")
        if status in (404, 405):
            return self._result("portability", "Portabilidad de bundles", "medium", False, "portability_missing")
        if status is not None and status >= 500:
            return self._result("portability", "Portabilidad de bundles", "medium", False, "portability_server_error")
        return self._result("portability", "Portabilidad de bundles", "medium", True, "portability_present")

    def _check_chat_bridge(self) -> dict:
        status, data, error = self._call("GET", "/api/federation/chat/bridge/config")
        if error is not None:
            return self._result("chat_bridge", "Config del bridge de chat", "low", False, f"request_error: {error}")
        if status is None or status >= 400:
            return self._result("chat_bridge", "Config del bridge de chat", "low", False, "chat_bridge_missing")
        if not isinstance(data, dict) or not data:
            return self._result("chat_bridge", "Config del bridge de chat", "low", False, "chat_bridge_invalid")
        return self._result("chat_bridge", "Config del bridge de chat", "low", True, "chat_bridge_ok")

    def _check_events_stream(self) -> dict:
        status, _data, error = self._call("GET", "/api/federation/events/stream")
        if error is not None:
            return self._result("events_stream", "Stream SSE de eventos", "low", False, f"request_error: {error}")
        if status in (404, 405):
            return self._result("events_stream", "Stream SSE de eventos", "low", False, "events_stream_missing")
        if status is not None and status >= 500:
            return self._result("events_stream", "Stream SSE de eventos", "low", False, "events_stream_server_error")
        return self._result("events_stream", "Stream SSE de eventos", "low", True, "events_stream_present")

    def run(self) -> dict:
        self._schema_version = None
        checks = [
            self._check_manifest(),
            self._check_jwks(),
            self._check_token(),
            self._check_directory(),
            self._check_peers_verify(),
            self._check_user_resolution(),
            self._check_webfinger(),
            self._check_reports(),
            self._check_portability(),
            self._check_chat_bridge(),
            self._check_events_stream(),
        ]
        passed = sum(1 for check in checks if check["passed"])
        failed = len(checks) - passed
        severe = sum(1 for check in checks if not check["passed"] and check["severity"] in SEVERE_SEVERITIES)
        return {
            "passed": passed,
            "failed": failed,
            "score": round(100 * passed / len(checks)) if checks else 0,
            "schema_version": self._schema_version,
            "severe_failures": severe,
            "checks": checks,
        }
