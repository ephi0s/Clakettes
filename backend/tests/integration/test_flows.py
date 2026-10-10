"""End-to-end flow tests across routers (festival → event → seats → reservation,
channel → message lifecycle, delegation → revoke).

These pin the public multi-step contracts; per-endpoint edge cases live in the
router test modules.
"""

from datetime import datetime, timezone


def _create_festival(db_session, name="Flow Festival"):
    from app.models.festival import Festival

    fest = Festival(name=name, is_active=True)
    db_session.add(fest)
    db_session.commit()
    db_session.refresh(fest)
    return fest


def _event_payload(festival_id, title="Flow Event"):
    return {
        "festival_id": festival_id,
        "title": title,
        "start_date": datetime.now(timezone.utc).isoformat(),
        "event_type": "screening",
    }


class TestEventBookingFlow:
    """festival → event → bulk seats → reservation → occupancy."""

    def test_full_booking_flow(self, client, db_session, admin_headers):
        h, _ = admin_headers
        fest = _create_festival(db_session)
        event = client.post(f"/api/festivals/{fest.id}/events/", json=_event_payload(fest.id), headers=h).json()
        eid = event["id"]

        seats = client.post(
            f"/api/events/{eid}/seats/bulk",
            json={"section": "A", "rows": ["1"], "numbers_per_row": 2},
            headers=h,
        )
        assert seats.status_code == 201
        assert len(seats.json()) == 2
        seat_id = seats.json()[0]["id"]

        counts = client.get(f"/api/events/{eid}/seats/counts", headers=h).json()
        assert counts["total"] == 2

        reservation = client.post(
            f"/api/events/{eid}/reservations/",
            json={"event_id": eid, "attendees": [{"seat_id": seat_id}]},
            headers=h,
        )
        assert reservation.status_code == 201

        occupancy = client.get(f"/api/events/{eid}/occupancy", headers=h)
        assert occupancy.status_code == 200

        programacion = client.get(f"/api/festivals/{fest.id}/events/programacion?venue=")
        assert programacion.status_code == 200


class TestChannelMessagingFlow:
    """channel → add member → DM → read → delete."""

    def test_full_messaging_flow(self, client, auth_headers, create_user, db_session):
        from app.auth import create_session

        headers, sender = auth_headers
        receiver, _ = create_user(username="flow_recv", email="flowrecv@example.com")
        channel = client.post(
            "/api/channels",
            json={"name": "Flow Room", "channel_type": "private"},
            headers=headers,
        )
        assert channel.status_code == 201
        cid = channel.json()["id"]

        added = client.post(
            f"/api/channels/{cid}/members",
            json={"user_id": receiver.id, "role": "member"},
            headers=headers,
        )
        assert added.status_code == 201

        msg = client.post(
            "/api/chat/messages",
            json={"content": "Flow hi", "sender_id": sender.id, "receiver_id": receiver.id},
            headers=headers,
        )
        assert msg.status_code == 201
        mid = msg.json()["id"]

        _, token, _ = create_session(db_session, receiver.id)
        recv_headers = {"Authorization": f"Bearer {token}"}
        assert client.put(f"/api/chat/messages/{mid}/read", headers=recv_headers).status_code == 200
        assert client.delete(f"/api/chat/messages/{mid}", headers=headers).status_code == 200


class TestDelegationFlow:
    """role → delegate → list → revoke → revoked status."""

    def test_full_delegation_flow(self, client, auth_headers, admin_headers, create_user):
        user_h, user = auth_headers
        admin_h, _ = admin_headers
        delegate, _ = create_user(username="flow_del", email="flowdel@example.com")
        role = client.post(
            "/api/roles/", json={"name": "flow_role", "display_name": "Flow Role"}, headers=admin_h
        ).json()
        delegation = client.post(
            "/api/delegations/",
            json={"delegator_id": user.id, "delegate_id": delegate.id, "role_id": role["id"]},
            headers=user_h,
        )
        assert delegation.status_code == 201
        did = delegation.json()["id"]

        listed = client.get(f"/api/users/{user.id}/active-delegations?direction=given", headers=user_h)
        assert listed.status_code == 200
        assert any(d["id"] == did for d in listed.json())

        revoked = client.post(f"/api/delegations/{did}/revoke", headers=user_h)
        assert revoked.status_code == 200
        assert revoked.json()["status"] == "revoked"
