
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Make backend modules available to pytest.
BACKEND_DIR = Path(__file__).resolve().parents[1]

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import database
import models


@pytest.fixture
def unauthenticated_client(tmp_path):
    """Create an isolated SQLite database and an unauthenticated client."""

    test_database_path = tmp_path / "test_networking.db"

    test_engine = create_engine(
        f"sqlite:///{test_database_path.as_posix()}",
        connect_args={"check_same_thread": False},
    )

    TestSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )

    database.engine = test_engine

    database.Base.metadata.create_all(bind=test_engine)

    from main import app

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[database.get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        test_engine.dispose()


@pytest.fixture
def client(unauthenticated_client):
    """Create a client authenticated as the default test user."""

    response = unauthenticated_client.post(
        "/api/auth/register",
        json={
            "full_name": "Test User",
            "email": "testuser@example.com",
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 201, response.text

    return unauthenticated_client


@pytest.fixture
def second_client(client):
    """Create a second authenticated user sharing the same test database."""

    with TestClient(client.app) as test_client:
        response = test_client.post(
            "/api/auth/register",
            json={
                "full_name": "Second User",
                "email": "seconduser@example.com",
                "password": "SecondPassword123!",
            },
        )

        assert response.status_code == 201, response.text

        yield test_client
