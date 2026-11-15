from .conftest import user_auth


def test_registration_login_and_profile(client):
    auth = user_auth(client)
    anonymous = client.get('/api/v1/users/me')
    assert anonymous.status_code == 401
    me = client.get('/api/v1/users/me', headers=auth)
    assert me.status_code == 200
    assert me.json()['role'] == 'customer'
    response = client.patch('/api/v1/users/me', headers=auth,
                            json={'full_name': 'Updated Person', 'phone': '+996000000000'})
    assert response.status_code == 200
    assert response.json()['full_name'] == 'Updated Person'
    assert client.patch('/api/v1/users/me', headers=auth,
                        json={'full_name': None}).status_code == 422


def test_invalid_login_and_duplicate_email(client):
    user_auth(client)
    duplicate = client.post('/api/v1/auth/register', json={
        'email': 'USER@EXAMPLE.COM', 'password': 'strong-password-123',
        'full_name': 'Duplicate'})
    assert duplicate.status_code == 409
    invalid = client.post('/api/v1/auth/login', json={
        'email': 'user@example.com', 'password': 'wrong'})
    assert invalid.status_code == 401
