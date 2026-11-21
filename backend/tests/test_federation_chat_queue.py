import asyncio
import uuid
from datetime import datetime, timedelta

from app import database as app_database
from app.main import app
from app.models.base import Base
from app.models.message import Message
from app.models.node_policy import NodePolicy
from app.routers import federation_chat_bridge
from app.services.message_queue_service import ChatOutbox, MessageQueueService

Base.metadata.create_all(bind=app_database.engine)

if not any(getattr(r, "path", "") == "/api/federation/chat/bridge/inbound" for r in app.routes):
    app.include_router(federation_chat_bridge.router, prefix="/api")


class RecordingTransport:
    def __init__(self) -> None:
        self.published: list[dict] = []

    async def publish(self, envelope: dict) -> None:
        self.published.append(envelope)


async def _fake_fetch(node_origin: str) -> str:
    return federation_chat_bridge.federation._tokens.public_pem()


federation_chat_bridge.federation.fetch_peer_public_key_pem = _fake_fetch


def _set_policy(db, node: str, allowed: bool = True, disable_chat: bool = False) -> None:
    policy = db.query(NodePolicy).filter(NodePolicy.node_domain == node).first()
    if policy is None:
        policy = NodePolicy(node_domain=node)
        db.add(policy)
    policy.allowed = allowed
    policy.disable_chat = disable_chat
    db.commit()


def _envelope(content: str = "hola", node: str = "peer.example", **overrides):
    fields = {
        "message_id": str(uuid.uuid4()),
        "node_origin": node,
        "channel_id": None,
        "receiver_id": 1,
        "content": content,
        "timestamp": "2026-11-20T10:00:00+00:00",
    }
    fields.update(overrides)
    fields["signature"] = federation_chat_bridge.federation.sign(fields)
    return fields


def test_outbox_dedup_order_and_replay(db_session):
    transport = RecordingTransport()
    svc = MessageQueueService(transport=transport, backoff_base_seconds=0)
    ids = ["m1", "m3", "m2"]
    for mid in ids:
        svc.enqueue(
            db_session,
            message_id=mid,
            node_origin="peer.example",
            subject="clakettes.chat.1",
            payload={"db_message_id": 1, "sender_id": 2, "receiver_id": 3, "content": mid},
        )
    dup = svc.enqueue(
        db_session,
        message_id="m1",
        node_origin="other",
        subject="other",
        payload={"content": "changed"},
    )
    assert db_session.query(ChatOutbox).count() == 3
    assert dup.message_id == "m1"
    assert dup.payload["content"] == "m1"

    assert [row.message_id for row in svc.pending(db_session)] == ["m1", "m3", "m2"]
    processed = asyncio.run(svc.flush_pending(db_session))
    assert [row.message_id for row in processed] == ["m1", "m3", "m2"]
    assert [env["message_id"] for env in transport.published] == ["m1", "m3", "m2"]
    assert svc.pending(db_session) == []
    assert all(row.status == "sent" for row in db_session.query(ChatOutbox).all())


def test_outbox_failed_with_backoff(db_session):
    svc = MessageQueueService(transport=RecordingTransport(), max_attempts=3, backoff_base_seconds=60)
    row = svc.enqueue(
        db_session,
        message_id="retry-1",
        node_origin="peer.example",
        subject="s",
        payload={"db_message_id": 1, "sender_id": 2, "content": "x"},
    )
    svc.mark_failed(db_session, row.id, "boom")
    assert row.attempts == 1
    assert row.status == "pending"
    assert svc.pending(db_session) == []

    row.created_at = datetime.now() - timedelta(seconds=300)
    db_session.commit()
    assert [item.message_id for item in svc.pending(db_session)] == ["retry-1"]

    svc.mark_failed(db_session, row.id, "boom2")
    svc.mark_failed(db_session, row.id, "boom3")
    assert row.attempts == 3
    assert row.status == "failed"


def test_inbound_valid_and_history(client, db_session, create_user):
    _set_policy(db_session, "peer.example")
    user, _ = create_user()
    env = _envelope(receiver_id=user.id)
    response = client.post("/api/federation/chat/bridge/inbound", json=env)
    assert response.status_code == 200
    assert response.json()["duplicate"] is False
    assert db_session.query(Message).count() == 1

    history = client.get("/api/federation/chat/messages", params={"node": "peer.example"})
    assert history.status_code == 200
    assert len(history.json()["messages"]) == 1
    assert history.json()["messages"][0]["message_id"] == env["message_id"]


def test_inbound_tampered_signature_forbidden(client, db_session, create_user):
    _set_policy(db_session, "peer.example")
    user, _ = create_user()
    env = _envelope(receiver_id=user.id)
    env["content"] = "manipulado"
    response = client.post("/api/federation/chat/bridge/inbound", json=env)
    assert response.status_code == 403
    assert db_session.query(Message).count() == 0


def test_inbound_disable_chat_forbidden(client, db_session, create_user):
    _set_policy(db_session, "peer.example", disable_chat=True)
    user, _ = create_user()
    response = client.post("/api/federation/chat/bridge/inbound", json=_envelope(receiver_id=user.id))
    assert response.status_code == 403


def test_inbound_duplicate_is_idempotent(client, db_session, create_user):
    _set_policy(db_session, "peer.example")
    user, _ = create_user()
    env = _envelope(receiver_id=user.id)
    first = client.post("/api/federation/chat/bridge/inbound", json=env)
    second = client.post("/api/federation/chat/bridge/inbound", json=env)
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["duplicate"] is False
    assert second.json()["duplicate"] is True
    assert db_session.query(Message).count() == 1


def test_history_sorted_by_timestamp(client, db_session, create_user):
    _set_policy(db_session, "peer.example")
    user, _ = create_user()
    late = _envelope(content="tarde", receiver_id=user.id, timestamp="2026-11-20T12:00:00+00:00")
    early = _envelope(content="temprano", receiver_id=user.id, timestamp="2026-11-20T08:00:00+00:00")
    for env in (late, early):
        assert client.post("/api/federation/chat/bridge/inbound", json=env).status_code == 200
    items = client.get("/api/federation/chat/messages").json()["messages"]
    assert [item["message_id"] for item in items] == [early["message_id"], late["message_id"]]


def test_outbound_signs_and_enqueues(client, db_session):
    response = client.post(
        "/api/federation/chat/bridge/outbound",
        json={"target_node": "peer.example", "receiver_id": 7, "content": "saludos"},
    )
    assert response.status_code == 200
    assert response.json()["message_id"]
    row = db_session.query(ChatOutbox).filter(ChatOutbox.message_id == response.json()["message_id"]).first()
    assert row is not None
    assert row.signature
    assert row.subject == "clakettes.chat.node.peer.example"


def test_bridge_config(client):
    response = client.get("/api/federation/chat/bridge/config")
    assert response.status_code == 200
    body = response.json()
    assert body["signature_algorithm"] == "RS256"
    assert "bridge" in body["subject_mapping"]
