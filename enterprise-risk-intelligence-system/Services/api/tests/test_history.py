import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    init_db()
    yield


def test_history_roundtrip():
    payload = {
        'client_id': 'hist-test',
        'risk_factors': {'financial_health': 75},
    }
    # create a score via existing endpoint (it will also write history)
    r = client.post('/risk/score', json=payload)
    assert r.status_code == 200
    body = r.json()
    assert 'score' in body

    # query history for that client
    r2 = client.get('/history/timeseries', params={'entity_id': 'hist-test'})
    assert r2.status_code == 200
    data = r2.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    first = data[0]
    assert first['entity_id'] == 'hist-test'
    assert 'score' in first
