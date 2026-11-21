from .conftest import admin_auth, user_auth


def test_order_server_computes_total_and_status(client):
    user = user_auth(client)
    admin = admin_auth(client)
    order = client.post("/api/v1/orders", headers=user, json={
        "order_type": "pickup",
        "items": [{"menu_item_id": 1, "quantity": 2}, {"menu_item_id": 2, "quantity": 1}],
    })
    assert order.status_code == 201, order.text
    data = order.json()
    assert data["total_som"] == 1000
    assert data["items"][0]["unit_price_som"] == 400
    id = data["id"]
    assert client.get(f"/api/v1/orders/{id}", headers=user).status_code == 200
    assert client.patch(f"/api/v1/admin/orders/{id}/status", json={"status": "completed"}, headers=admin).status_code == 409
    for status in ("preparing", "ready", "completed"):
        result = client.patch(f"/api/v1/admin/orders/{id}/status", json={"status": status}, headers=admin)
        assert result.status_code == 200, result.text
    assert client.post(f"/api/v1/orders/{id}/cancel", headers=user).status_code == 409


def test_order_validation_and_customer_isolation(client):
    user = user_auth(client)
    another = user_auth(client, "other@example.com")
    no_reservation = client.post("/api/v1/orders", headers=user, json={"order_type": "dine_in", "items": [{"menu_item_id": 1, "quantity": 1}]})
    assert no_reservation.status_code == 422
    duplicate = client.post("/api/v1/orders", headers=user, json={
        "order_type": "pickup", "items": [{"menu_item_id": 1, "quantity": 1}, {"menu_item_id": 1, "quantity": 1}]
    })
    assert duplicate.status_code == 422
    assert client.post("/api/v1/orders", headers=user, json={"order_type": "pickup", "items": [{"menu_item_id": 999, "quantity": 1}]}).status_code == 422
    order = client.post("/api/v1/orders", headers=user, json={"order_type": "pickup", "items": [{"menu_item_id": 1, "quantity": 1}]})
    assert order.status_code == 201
    assert client.get(f"/api/v1/orders/{order.json()['id']}", headers=another).status_code == 404
    assert client.get("/api/v1/admin/orders", headers=another).status_code == 403
