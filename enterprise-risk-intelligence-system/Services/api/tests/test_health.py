import os
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient

# Get the absolute path to the test file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the path to the api directory (parent of tests)
api_dir = os.path.dirname(current_dir)
# Add the api directory to Python path
if api_dir not in sys.path:
    sys.path.insert(0, api_dir)

from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
