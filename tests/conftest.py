from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models as _models  # noqa: F401  # registra os models no Base.metadata
from app.database.base import Base
from app.database.session import get_db
from app.main import app as fastapi_app

engine = create_engine(
    'sqlite://',
    connect_args={'check_same_thread': False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


fastapi_app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def _reset_database() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(fastapi_app) as test_client:
        yield test_client


@pytest.fixture
def user_payload() -> dict[str, str]:
    return {
        'name': 'Alice Example',
        'email': 'Alice@Example.com',
        'password': 'secret123',
    }


@pytest.fixture
def auth_headers(client: TestClient, user_payload: dict[str, str]) -> dict[str, str]:
    response = client.post('/users/', json=user_payload)
    assert response.status_code == 201

    login = client.post(
        '/auth/token',
        data={
            'username': user_payload['email'].lower(),
            'password': user_payload['password'],
        },
    )
    assert login.status_code == 200
    token = login.json()['access_token']
    return {'Authorization': f'Bearer {token}'}
