from fastapi.testclient import TestClient


def _current_user_id(client: TestClient, auth_headers: dict[str, str]) -> int:
    response = client.get('/users/', headers=auth_headers)
    assert response.status_code == 200
    return response.json()[0]['id']


def test_create_user(client: TestClient, user_payload: dict[str, str]) -> None:
    response = client.post('/users/', json=user_payload)

    assert response.status_code == 201
    body = response.json()
    assert body['email'] == 'alice@example.com'
    assert body['is_active'] is True
    assert 'password' not in body
    assert 'created_at' in body


def test_create_user_rejects_invalid_email(client: TestClient) -> None:
    response = client.post(
        '/users/',
        json={'name': 'Alice', 'email': 'not-an-email', 'password': 'secret123'},
    )

    assert response.status_code == 422


def test_create_user_rejects_short_password(client: TestClient) -> None:
    response = client.post(
        '/users/',
        json={'name': 'Alice', 'email': 'alice@example.com', 'password': 'short'},
    )

    assert response.status_code == 422


def test_create_user_rejects_duplicate_email(
    client: TestClient, user_payload: dict[str, str]
) -> None:
    client.post('/users/', json=user_payload)

    duplicate = client.post(
        '/users/',
        json={**user_payload, 'email': user_payload['email'].upper()},
    )

    assert duplicate.status_code == 409


def test_list_users_requires_auth(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.get('/users/', headers=auth_headers)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_user_not_found(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.get('/users/9999', headers=auth_headers)

    assert response.status_code == 404


def test_get_user(client: TestClient, auth_headers: dict[str, str]) -> None:
    user_id = _current_user_id(client, auth_headers)

    response = client.get(f'/users/{user_id}', headers=auth_headers)

    assert response.status_code == 200
    assert response.json()['id'] == user_id


def test_update_own_user(client: TestClient, auth_headers: dict[str, str]) -> None:
    user_id = _current_user_id(client, auth_headers)

    response = client.put(
        f'/users/{user_id}',
        headers=auth_headers,
        json={'name': 'Alice Updated', 'password': 'newsecret123'},
    )

    assert response.status_code == 200
    assert response.json()['name'] == 'Alice Updated'


def test_update_other_user_forbidden(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    other = client.post(
        '/users/',
        json={
            'name': 'Bob',
            'email': 'bob@example.com',
            'password': 'secret123',
        },
    )
    other_id = other.json()['id']

    response = client.put(
        f'/users/{other_id}',
        headers=auth_headers,
        json={'name': 'Hacked'},
    )

    assert response.status_code == 403


def test_update_to_duplicate_email_conflicts(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    user_id = _current_user_id(client, auth_headers)
    client.post(
        '/users/',
        json={
            'name': 'Bob',
            'email': 'bob@example.com',
            'password': 'secret123',
        },
    )

    response = client.put(
        f'/users/{user_id}',
        headers=auth_headers,
        json={'email': 'bob@example.com'},
    )

    assert response.status_code == 409


def test_delete_other_user_forbidden(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    other = client.post(
        '/users/',
        json={
            'name': 'Bob',
            'email': 'bob@example.com',
            'password': 'secret123',
        },
    )
    other_id = other.json()['id']

    response = client.delete(f'/users/{other_id}', headers=auth_headers)

    assert response.status_code == 403


def test_delete_own_user(
    client: TestClient, auth_headers: dict[str, str], user_payload: dict[str, str]
) -> None:
    user_id = _current_user_id(client, auth_headers)

    response = client.delete(f'/users/{user_id}', headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {'detail': 'User deleted'}

    login = client.post(
        '/auth/token',
        data={
            'username': user_payload['email'].lower(),
            'password': user_payload['password'],
        },
    )
    assert login.status_code == 401
