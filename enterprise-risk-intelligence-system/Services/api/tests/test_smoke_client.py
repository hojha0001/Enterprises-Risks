import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    init_db()
    yield

def test_health_and_risk_score():
    # Health
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json() == {'status': 'ok'}

    # Risk score
    payload = {
        'client_id': 'smoke-test',
        'risk_factors': {'financial_health': 80, 'market_volatility': 20}
    }
    r2 = client.post('/risk/score', json=payload)
    assert r2.status_code == 200
    body = r2.json()
    assert 'score' in body and isinstance(body['score'], (int, float))
    assert body['client_id'] == 'smoke-test'
