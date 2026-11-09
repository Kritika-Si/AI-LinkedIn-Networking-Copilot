
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
def client(tmp_path):
    """Create an isolated SQLite database for each API test."""

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

    # Ensure the application's startup table creation uses the test engine.
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
