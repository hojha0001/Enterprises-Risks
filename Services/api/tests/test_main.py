import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from app.main import app
from app.database import get_session
from app.models import RiskAssessment
import tempfile
import os
import os

# Use a temp file for SQLite to avoid threading issues
TEMP_DIR = tempfile.mkdtemp()
DB_FILE = os.path.join(TEMP_DIR, "test.db")
DATABASE_URL = f"sqlite:///{DB_FILE}"
engine = create_engine(DATABASE_URL)

def get_session_override():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    SQLModel.metadata.create_all(engine)
    yield
    try:
        engine.dispose()  # Close all connections
        SQLModel.metadata.drop_all(engine)
    finally:
        try:
            os.remove(DB_FILE)
            os.rmdir(TEMP_DIR)
        except (OSError, PermissionError):
            # Ignore cleanup errors on Windows
            pass

@pytest.fixture
def test_client():
    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

def test_health_endpoint(test_client):
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_risk_score_endpoint(test_client):
    test_request = {
        "entity_name": "Test Corp",
        "risk_factors": ["industry", "location"],
        "context": "Test context"
    }
    response = test_client.post("/risk/score", json=test_request)
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert "confidence" in data
    assert "factors" in data
    assert "id" in data
    assert data["entity_name"] == "Test Corp"
    assert data["factors"] == ["industry", "location"]