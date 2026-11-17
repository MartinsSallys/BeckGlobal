from fastapi.testclient import TestClient


def test_login_success(client: TestClient, auth_headers: dict[str, str]) -> None:
    assert auth_headers['Authorization'].startswith('Bearer ')


def test_login_wrong_password(client: TestClient, user_payload: dict[str, str]) -> None:
    client.post('/users/', json=user_payload)

    response = client.post(
        '/auth/token',
        data={
            'username': user_payload['email'].lower(),
            'password': 'wrong-password',
        },
    )

    assert response.status_code == 401


def test_login_unknown_user(client: TestClient) -> None:
    response = client.post(
        '/auth/token',
        data={'username': 'ghost@example.com', 'password': 'secret123'},
    )

    assert response.status_code == 401


def test_protected_route_requires_token(client: TestClient) -> None:
    response = client.get('/users/')

    assert response.status_code == 401


def test_protected_route_rejects_invalid_token(client: TestClient) -> None:
    response = client.get(
        '/users/',
        headers={'Authorization': 'Bearer not-a-valid-token'},
    )

    assert response.status_code == 401
