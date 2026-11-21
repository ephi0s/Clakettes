import pytest
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.testclient import TestClient

from app import database as app_database
from app.auth import get_current_user
from app.database import get_db
from app.models.base import Base
from app.models.message import Message
from app.models.node_policy import NodePolicy
from app.routers.chat_moderation import router as moderation_router
from app.services.chat_moderation_service import ChatModerationService, ChatMute, MessageReport
from app.services.chat_rate_limit_service import ChatRateLimitService, chat_rate_limit, enforce_chat_rate_limit


@pytest.fixture(scope="module", autouse=True)
def _create_moderation_tables():
    Base.metadata.create_all(bind=app_database.engine)


@pytest.fixture
def moderation() -> ChatModerationService:
    return ChatModerationService(blocked_words=["spam"])


def _make_message(db, sender_id: int) -> Message:
    message = Message(content="mensaje original", sender_id=sender_id)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def test_report_message(db_session, create_user, moderation):
    sender, _ = create_user(username="sender", email="sender@example.com")
    reporter, _ = create_user(username="reporter", email="reporter@example.com")
    message = _make_message(db_session, sender.id)

    report = moderation.report_message(db_session, reporter.id, message.id, "contenido ofensivo")

    assert report.id is not None
    assert report.status == "pending"
    assert db_session.query(MessageReport).filter(MessageReport.message_id == message.id).count() == 1
    assert moderation.list_reports(db_session)[0].id == report.id


def test_moderate_message_admin_hides(db_session, create_user, moderation):
    admin, _ = create_user(username="admin", email="admin@example.com", role="admin")
    sender, _ = create_user(username="sender", email="sender@example.com")
    message = _make_message(db_session, sender.id)

    result = moderation.moderate_message(db_session, message.id, "hide", admin)

    assert result["status"] == "hidden"
    db_session.refresh(message)
    assert "hidden" in message.content


def test_moderate_message_rejects_non_admin(db_session, create_user, moderation):
    sender, _ = create_user(username="sender", email="sender@example.com")
    message = _make_message(db_session, sender.id)

    with pytest.raises(HTTPException) as exc_info:
        moderation.moderate_message(db_session, message.id, "hide", sender)

    assert exc_info.value.status_code == 403


def test_active_mute_blocks_sending(db_session, create_user, moderation):
    admin, _ = create_user(username="admin", email="admin@example.com", role="admin")
    target, _ = create_user(username="target", email="target@example.com")

    mute = moderation.mute_user(
        db_session,
        target.id,
        admin,
        node_domain="node-a.example",
        duration_seconds=600,
        reason="abusivo",
    )

    assert mute.id is not None
    assert db_session.query(ChatMute).filter(ChatMute.user_id == target.id).count() == 1
    with pytest.raises(HTTPException) as exc_info:
        moderation.check_send_allowed(db_session, target.id, node_domain="node-a.example", content="hola")
    assert exc_info.value.status_code == 403


def test_disable_chat_blocks_sending(db_session, create_user, moderation):
    target, _ = create_user(username="target", email="target@example.com")
    db_session.add(NodePolicy(node_domain="node-b.example", allowed=True, disable_chat=True))
    db_session.commit()

    assert moderation.is_chat_disabled(db_session, "node-b.example") is True
    with pytest.raises(HTTPException) as exc_info:
        moderation.check_send_allowed(db_session, target.id, node_domain="node-b.example")
    assert exc_info.value.status_code == 403


def test_word_filter_blocks_content(db_session, create_user, moderation):
    target, _ = create_user(username="target", email="target@example.com")

    with pytest.raises(HTTPException) as exc_info:
        moderation.check_send_allowed(db_session, target.id, content="Este mensaje es SPAM")

    assert exc_info.value.status_code == 400


@pytest.fixture
def rate_limit_app(db_session, create_user):
    user, _ = create_user(username="limited", email="limited@example.com")
    previous = (chat_rate_limit.max_messages, chat_rate_limit.window_seconds)
    chat_rate_limit.max_messages = 3
    chat_rate_limit.window_seconds = 60
    chat_rate_limit.reset()

    app = FastAPI()
    app.dependency_overrides[get_current_user] = lambda: user

    @app.middleware("http")
    async def set_peer_domain(request: Request, call_next):
        request.state.peer_domain = "node-a.example"
        return await call_next(request)

    @app.post("/api/chat/messages")
    async def send(request: Request, current_user=Depends(enforce_chat_rate_limit)):
        return {"ok": True}

    with TestClient(app) as client:
        yield client, user
    app.dependency_overrides.clear()
    chat_rate_limit.max_messages, chat_rate_limit.window_seconds = previous
    chat_rate_limit.reset()


def test_rate_limit_per_node_returns_429(rate_limit_app):
    client, _ = rate_limit_app

    for _ in range(3):
        assert client.post("/api/chat/messages", json={}).status_code == 200

    response = client.post("/api/chat/messages", json={})

    assert response.status_code == 429
    assert "retry-after" in response.headers


def test_rate_limit_service_keys_are_per_node_and_user():
    service = ChatRateLimitService(max_messages=1, window_seconds=60)
    assert service.check("node-a.example", 1) == (True, 0)
    assert service.check("node-a.example", 1)[0] is False
    assert service.check("node-b.example", 1) == (True, 0)
    assert service.check("node-a.example", 2) == (True, 0)
    service.reset("node-a.example", 1)
    assert service.check("node-a.example", 1) == (True, 0)
    service.reset()
    assert service.snapshot() == []


@pytest.fixture
def moderation_app(db_session):
    def build(user):
        app = FastAPI()
        app.include_router(moderation_router)
        app.dependency_overrides[get_db] = lambda: db_session
        app.dependency_overrides[get_current_user] = lambda: user
        return TestClient(app)

    return build


def test_report_endpoint(moderation_app, db_session, create_user):
    sender, _ = create_user(username="sender", email="sender@example.com")
    reporter, _ = create_user(username="reporter", email="reporter@example.com")
    message = _make_message(db_session, sender.id)
    client = moderation_app(reporter)

    response = client.post(f"/api/chat/moderation/messages/{message.id}/report?reason=spam")

    assert response.status_code == 201
    assert response.json()["status"] == "pending"


def test_reports_endpoint_requires_admin(moderation_app, create_user):
    normal, _ = create_user(username="normal", email="normal@example.com")
    admin, _ = create_user(username="admin", email="admin@example.com", role="admin")

    assert moderation_app(normal).get("/api/chat/moderation/reports").status_code == 403
    assert moderation_app(admin).get("/api/chat/moderation/reports").status_code == 200
