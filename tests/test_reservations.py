from datetime import datetime, timedelta, timezone

from .conftest import admin_auth, user_auth


def future_start(days=2):
    return (datetime.now(timezone.utc) + timedelta(days=days)).replace(microsecond=0).isoformat()


def test_reserve_prevent_overlap_and_cancel(client):
    user = user_auth(client)
    second_user = user_auth(client, "another@example.com")
    start = future_start()
    available = client.get("/api/v1/reservations/availability", params={"starts_at": start, "guests": 2})
    assert available.status_code == 200, available.text
    assert len(available.json()["available_tables"]) == 2

    reservation = client.post("/api/v1/reservations", headers=user, json={"starts_at": start, "guests": 2, "table_id": 1})
    assert reservation.status_code == 201, reservation.text
    reservation_id = reservation.json()["id"]
    assert reservation.json()["table_id"] == 1
    clash = client.post("/api/v1/reservations", headers=second_user, json={"starts_at": start, "guests": 2, "table_id": 1})
    assert clash.status_code == 409, clash.text
    assert client.get(f"/api/v1/reservations/{reservation_id}", headers=second_user).status_code == 404

    other_table = client.post("/api/v1/reservations", headers=second_user, json={"starts_at": start, "guests": 2})
    assert other_table.status_code == 201, other_table.text
    assert other_table.json()["table_id"] == 2

    cancelled = client.post(f"/api/v1/reservations/{reservation_id}/cancel", headers=user)
    assert cancelled.status_code == 200 and cancelled.json()["status"] == "cancelled"
    now_free = client.post("/api/v1/reservations", headers=second_user, json={"starts_at": start, "guests": 2, "table_id": 1})
    assert now_free.status_code == 201, now_free.text


def test_no_past_booking_and_staff_access(client):
    user = user_auth(client)
    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    response = client.post("/api/v1/reservations", headers=user, json={"starts_at": past, "guests": 2})
    assert response.status_code == 422
    assert client.get("/api/v1/admin/reservations", headers=user).status_code == 403
    assert client.get("/api/v1/admin/reservations", headers=admin_auth(client)).status_code == 200
