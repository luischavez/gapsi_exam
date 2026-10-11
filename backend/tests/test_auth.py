from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi.testclient import TestClient
from google.cloud.firestore import Client

from app.config import get_settings


def make_token(subject: str, expires_in: timedelta, secret: str | None = None) -> str:
    settings = get_settings()
    return jwt.encode(
        {'sub': subject, 'exp': datetime.now(UTC) + expires_in},
        secret or settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def auth_header(token: str) -> dict[str, str]:
    return {'Authorization': f'Bearer {token}'}


def test_login_returns_valid_token(client: TestClient, user: dict[str, str]):
    response = client.post('/auth/login', json=user)

    assert response.status_code == 200
    body = response.json()
    assert body['token_type'] == 'bearer'

    settings = get_settings()
    payload = jwt.decode(body['access_token'], settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    assert payload['sub'] == user['username']


def test_login_wrong_password(client: TestClient, user: dict[str, str]):
    response = client.post('/auth/login', json={'username': user['username'], 'password': 'wrong'})
    assert response.status_code == 401


def test_login_unknown_user_gets_same_error_as_wrong_password(client: TestClient, user: dict[str, str]):
    wrong_password = client.post('/auth/login', json={'username': user['username'], 'password': 'wrong'})
    unknown_user = client.post('/auth/login', json={'username': 'nobody', 'password': 'wrong'})
    assert unknown_user.status_code == 401
    assert unknown_user.json() == wrong_password.json()


@pytest.mark.parametrize('payload', [{}, {'username': 'tester'}, {'password': 'tester-pass'}])
def test_login_missing_fields(client: TestClient, payload: dict[str, str]):
    response = client.post('/auth/login', json=payload)
    assert response.status_code == 422


def test_user_with_valid_token(client: TestClient, user: dict[str, str], token: str):
    response = client.get('/auth/user', headers=auth_header(token))
    assert response.status_code == 200
    assert response.json() == {'username': user['username']}


def test_user_without_token(client: TestClient):
    response = client.get('/auth/user')
    assert response.status_code == 401


def test_user_with_malformed_token(client: TestClient):
    response = client.get('/auth/user', headers=auth_header('abc'))
    assert response.status_code == 401


def test_user_with_expired_token(client: TestClient, user: dict[str, str]):
    expired = make_token(user['username'], expires_in=timedelta(minutes=-1))
    response = client.get('/auth/user', headers=auth_header(expired))
    assert response.status_code == 401


def test_user_with_token_signed_by_another_key(client: TestClient, user: dict[str, str]):
    forged = make_token(user['username'], expires_in=timedelta(minutes=5), secret='another-secret-key-at-least-32-bytes-long')
    response = client.get('/auth/user', headers=auth_header(forged))
    assert response.status_code == 401


def test_user_deleted_after_token_was_issued(
    client: TestClient, user: dict[str, str], token: str, firestore: Client
):
    firestore.collection('users').document(user['username']).delete()
    response = client.get('/auth/user', headers=auth_header(token))
    assert response.status_code == 401
