from fastapi.testclient import TestClient
from pybox.api import app


client = TestClient(app)


def test_run_endpoint_success():
    payload = {
        "code": "result = x * 2",
        "input": {"x": 21},
    }
    resp = client.post("/run", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["result"] == 42
