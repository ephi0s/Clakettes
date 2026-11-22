import asyncio
import hashlib
import hmac
import json
import threading
import time

import jwt
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.database import get_db
from app.routers import federation_events
from app.services.event_bus_service import event_bus
from app.services.node_peering_service import NodePeeringService


@pytest.fixture
def event_client(db_session):
    app = FastAPI()
    app.include_router(federation_events.router)

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    event_bus.reset()
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
    task = federation_events._worker_task
    if task is not None:
        task.cancel()
    federation_events._worker_task = None
    event_bus.reset()


def _token(headers):
    return headers["Authorization"].split(" ", 1)[1]


def test_bus_subscribe_and_unsubscribe():
    event_bus.reset()
    sub_id, queue = event_bus.subscribe("cache:invalidation")
    envelope = event_bus.publish("cache:invalidation", {"type": "cache.invalidated", "data": {"key": "festival:1"}})
    assert queue.get_nowait()["seq"] == envelope["seq"]
    event_bus.unsubscribe("cache:invalidation", sub_id)
    event_bus.publish("cache:invalidation", {"type": "cache.invalidated"})
    assert queue.empty()


def test_stream_delivers_published_event(event_client, auth_headers):
    headers, _user = auth_headers
    token = _token(headers)

    def _publish_later():
        time.sleep(0.5)
        event_bus.publish("cache:invalidation", {"type": "cache.invalidated", "data": {"key": "festival:7"}})

    worker = threading.Thread(target=_publish_later)
    worker.start()
    with event_client.stream(
        "GET",
        "/api/federation/events/stream",
        params={"topic": "cache:invalidation", "token": token, "limit": 1},
    ) as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        worker.join(timeout=2)
        event_name = None
        data = None
        for line in response.iter_lines():
            if line.startswith("event: "):
                event_name = line[len("event: ") :]
            elif line.startswith("data: "):
                data = json.loads(line[len("data: ") :])
                break
        assert event_name == "cache.invalidated"
        assert data["topic"] == "cache:invalidation"
        assert data["data"]["key"] == "festival:7"


def test_stream_replays_events_since(event_client, auth_headers):
    headers, _user = auth_headers
    token = _token(headers)
    first = event_bus.publish("festival:new", {"type": "festival.created", "data": {"id": 1}})
    second = event_bus.publish("festival:new", {"type": "festival.created", "data": {"id": 2}})

    with event_client.stream(
        "GET",
        "/api/federation/events/stream",
        params={"topic": "festival:new", "since": first["seq"], "token": token, "limit": 1},
    ) as response:
        assert response.status_code == 200
        received = []
        for line in response.iter_lines():
            if line.startswith("data: "):
                received.append(json.loads(line[len("data: ") :]))
                if len(received) == 1:
                    break
        assert [event["seq"] for event in received] == [second["seq"]]
        assert received[0]["data"]["id"] == 2


def test_stream_requires_valid_token(event_client):
    with event_client.stream(
        "GET",
        "/api/federation/events/stream",
        params={"topic": "cache:invalidation", "token": "invalid"},
    ) as response:
        assert response.status_code == 401


def test_publish_enqueues_retry_when_peer_fails(event_client, admin_headers, monkeypatch, db_session):
    headers, _user = admin_headers
    NodePeeringService().register_or_update(db_session, "peer.example", "a" * 64, capabilities=["federation"])

    def _fail(_domain, _envelope):
        raise RuntimeError("peer offline")

    monkeypatch.setattr(federation_events, "_send_to_peer", _fail)
    response = event_client.post(
        "/api/federation/events/publish",
        headers=headers,
        json={"type": "festival.created", "topic": "festival:new", "data": {"id": 9}},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["published"] is True
    assert body["failed"] == ["peer.example"]
    assert body["retry_queued"] == 1

    status = event_client.get("/api/federation/events/retry-queue", headers=headers)
    assert status.status_code == 200
    pending = status.json()["pending"]
    assert len(pending) == 1
    assert pending[0]["node_domain"] == "peer.example"
    assert pending[0]["attempt"] == 0
    assert pending[0]["max_attempts"] == 3


def test_publish_skips_peer_that_disables_chat(event_client, admin_headers, monkeypatch, db_session):
    headers, _user = admin_headers
    NodePeeringService().register_or_update(
        db_session,
        "chatless.example",
        "b" * 64,
        capabilities=["federation", "disable_chat"],
    )
    calls = []

    async def _record(domain, _envelope):
        calls.append(domain)
        return True

    monkeypatch.setattr(federation_events, "_send_to_peer", _record)
    response = event_client.post(
        "/api/federation/events/publish",
        headers=headers,
        json={"type": "chat.message", "topic": "node:primary:entity:chat", "data": {"id": 1}},
    )
    assert response.status_code == 200
    assert response.json()["skipped"] == ["chatless.example"]
    assert calls == []


def test_publish_and_retry_queue_require_admin(event_client, auth_headers):
    headers, _user = auth_headers
    publish = event_client.post(
        "/api/federation/events/publish",
        headers=headers,
        json={"type": "festival.created"},
    )
    assert publish.status_code == 403
    queue = event_client.get("/api/federation/events/retry-queue", headers=headers)
    assert queue.status_code == 403
    anonymous = event_client.get("/api/federation/events/retry-queue")
    assert anonymous.status_code == 401


def _sign(raw):
    return hmac.new(str(federation_events.settings.SECRET_KEY).encode("utf-8"), raw, hashlib.sha256).hexdigest()


def _peer_token(domain="peer.example"):
    from app.routers import federation as federation_router

    return federation_router.federation_token_service.create_token(
        "events", extra_claims={"iss": domain, "issuer_node": domain}
    )


def _stub_peer(monkeypatch, domain="peer.example"):
    from app.routers import federation as federation_router

    async def _peer(_request):
        return {"iss": domain, "issuer_node": domain, "sub": "events", "typ": "federation"}

    monkeypatch.setattr(federation_router, "get_current_federation_peer", _peer)

    async def _noop(_domain, _envelope):
        return True

    monkeypatch.setattr(federation_events, "_send_to_peer", _noop)


def test_send_to_peer_includes_federation_token_and_signature(monkeypatch):
    captured = {}

    class _Response:
        def raise_for_status(self):
            return None

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def post(self, url, content=None, headers=None, timeout=None):
            captured.update(url=url, content=content, headers=headers)
            return _Response()

    monkeypatch.setattr(federation_events.httpx, "AsyncClient", _Client)
    asyncio.run(federation_events._send_to_peer("peer.example", {"type": "festival.created"}))

    headers = captured["headers"]
    assert headers["Authorization"].startswith("Bearer ")
    claims = jwt.decode(headers["Authorization"].split(" ", 1)[1], options={"verify_signature": False})
    assert claims["typ"] == "federation"
    assert claims["aud"] == "clakettes-federation"
    assert claims["issuer_node"]
    assert headers["X-Clakettes-Signature"] == _sign(captured["content"])
    assert json.loads(captured["content"])["event"] == {"type": "festival.created"}


def test_publish_accepts_federated_peer_with_valid_signature(event_client, db_session, monkeypatch):
    NodePeeringService().register_or_update(db_session, "peer.example", "a" * 64)
    _stub_peer(monkeypatch)
    raw = json.dumps(
        {
            "type": "festival.created",
            "topic": "festival:new",
            "node": "peer.example",
            "issuer": "peer.example",
            "data": {"id": 3},
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    response = event_client.post(
        "/api/federation/events/publish",
        content=raw,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {_peer_token()}",
            "X-Clakettes-Signature": _sign(raw),
        },
    )
    assert response.status_code == 200
    assert response.json()["topic"] == "festival:new"
    assert event_bus.replay("festival:new")[-1]["node"] == "peer.example"


@pytest.mark.parametrize("signature", [None, "bad-signature"])
def test_publish_rejects_peer_without_valid_signature(event_client, db_session, monkeypatch, signature):
    NodePeeringService().register_or_update(db_session, "peer.example", "a" * 64)
    _stub_peer(monkeypatch)
    raw = json.dumps({"type": "festival.created", "data": {}}, sort_keys=True, separators=(",", ":")).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {_peer_token()}",
    }
    if signature is not None:
        headers["X-Clakettes-Signature"] = signature
    response = event_client.post("/api/federation/events/publish", content=raw, headers=headers)
    assert response.status_code == 401
    assert event_bus.replay("cache:invalidation") == []


def test_publish_rejects_untrusted_peer(event_client, db_session, monkeypatch):
    NodePeeringService().register_or_update(db_session, "peer.example", "a" * 64, allowed=False)
    _stub_peer(monkeypatch)
    raw = json.dumps({"type": "festival.created", "data": {}}, sort_keys=True, separators=(",", ":")).encode("utf-8")
    response = event_client.post(
        "/api/federation/events/publish",
        content=raw,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {_peer_token()}",
            "X-Clakettes-Signature": _sign(raw),
        },
    )
    assert response.status_code == 403


def test_publish_rejects_node_spoofing(event_client, db_session, monkeypatch):
    NodePeeringService().register_or_update(db_session, "peer.example", "a" * 64)
    _stub_peer(monkeypatch)
    raw = json.dumps(
        {"type": "festival.created", "node": "victim.example", "data": {}},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    response = event_client.post(
        "/api/federation/events/publish",
        content=raw,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {_peer_token()}",
            "X-Clakettes-Signature": _sign(raw),
        },
    )
    assert response.status_code == 403


def test_publish_accepts_mtls_peer_with_valid_signature(db_session, monkeypatch):
    node = NodePeeringService().register_or_update(db_session, "mtls.example", "c" * 64)

    async def _noop(_domain, _envelope):
        return True

    monkeypatch.setattr(federation_events, "_send_to_peer", _noop)

    def _override_get_db():
        yield db_session

    app = FastAPI()

    @app.middleware("http")
    async def _peer_middleware(request, call_next):
        request.state.peer_node = node
        return await call_next(request)

    app.include_router(federation_events.router)
    app.dependency_overrides[get_db] = _override_get_db
    event_bus.reset()
    raw = json.dumps({"type": "festival.created", "data": {}}, sort_keys=True, separators=(",", ":")).encode("utf-8")
    with TestClient(app) as client:
        response = client.post(
            "/api/federation/events/publish",
            content=raw,
            headers={"Content-Type": "application/json", "X-Clakettes-Signature": _sign(raw)},
        )
    assert response.status_code == 200
    event_bus.reset()
