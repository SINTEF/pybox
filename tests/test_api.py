from fastapi.testclient import TestClient
from pybox.api import app

client = TestClient(app)

def test_run_endpoint(monkeypatch):
    from pybox import api

    async def fake_submit(func, *args, **kwargs):
        return {
            "status": "ok",
            "stdout": '{"result": 42}',
            "stderr": "",
            "exit_code": 0,
        }

    monkeypatch.setattr(api.queue, "submit", fake_submit)

    resp = client.post("/run", json={"code": "result = 42", "input": {}})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["result"] == 42
