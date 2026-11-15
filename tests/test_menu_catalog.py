from .conftest import user_auth, admin_auth


def test_public_restaurant_and_menu(client):
    assert client.get('/health').json() == {'status': 'ok'}
    assert client.get('/api/v1/restaurant').json()['name'] == 'MAISON'
    assert len(client.get('/api/v1/menu/categories').json()) == 1
    result = client.get('/api/v1/menu/items?category_id=1&q=pas')
    assert result.status_code == 200
    assert len(result.json()) == 1
    assert result.json()[0]['price_som'] == 400
    assert client.get('/api/v1/menu/items/999').status_code == 404


def test_menu_admin_permissions_and_soft_delete(client):
    normal = user_auth(client)
    payload = {'category_id': 1, 'name': 'Cake', 'price_som': 250}
    assert client.post('/api/v1/menu/items', headers=normal,
                       json=payload).status_code == 403
    admin = admin_auth(client)
    created = client.post('/api/v1/menu/items', headers=admin, json=payload)
    assert created.status_code == 201
    item_id = created.json()['id']
    assert client.patch(f'/api/v1/menu/items/{item_id}', headers=admin,
                        json={'is_available': False}).status_code == 200
    assert client.delete(f'/api/v1/menu/items/{item_id}', headers=admin).status_code == 204
    assert client.get(f'/api/v1/menu/items/{item_id}').status_code == 404
