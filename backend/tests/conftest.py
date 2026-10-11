import os

import httpx
import pytest

# Make sure tests only runs against firestore emulator
if 'FIRESTORE_EMULATOR_HOST' not in os.environ:
    pytest.exit('FIRESTORE_EMULATOR_HOST is not set, refusing to run against a real Firestore', returncode=1)
os.environ['GOOGLE_CLOUD_PROJECT'] = 'gapsi-exam-test'
os.environ['JWT_SECRET_KEY'] = '89a40eb97d5921580de2f2d28f97055f4d7ff96b9a38b8f4c824975041461fa2'

from fastapi.testclient import TestClient
from google.cloud.firestore import Client

from app.internal.security import hash_password
from app.main import app

TEST_USER = {'username': 'tester', 'password': 'tester-pass'}


@pytest.fixture(scope='session')
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope='session')
def firestore() -> Client:
    return Client()


@pytest.fixture(autouse=True)
def clean_db():
    host = os.environ['FIRESTORE_EMULATOR_HOST']
    project = os.environ['GOOGLE_CLOUD_PROJECT']
    httpx.delete(f'http://{host}/emulator/v1/projects/{project}/databases/(default)/documents').raise_for_status()


@pytest.fixture
def user(firestore: Client) -> dict[str, str]:
    """
    Create a user in the database and return its credentials
    """
    firestore.collection('users').document(TEST_USER['username']).set({
        'password_hash': hash_password(TEST_USER['password']),
    })
    return TEST_USER


@pytest.fixture
def token(client: TestClient, user: dict[str, str]) -> str:
    """
    Log in with the test user and return its access token
    """
    return client.post('/auth/login', json=user).json()['access_token']


@pytest.fixture
def auth_headers(token: str) -> dict[str, str]:
    return {'Authorization': f'Bearer {token}'}
