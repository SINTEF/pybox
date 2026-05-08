import json
from pybox.executor import SandboxExecutor, SandboxConfig

def test_executor_builds_result(monkeypatch):
    cfg = SandboxConfig(image="pybox-sandbox:latest", timeout_sec=1.0)
    executor = SandboxExecutor(cfg)

    def fake_run(cmd, stdin, stdout, stderr, text):
        class P:
            returncode = 0
            def communicate(self, payload, timeout):
                return (json.dumps({"result": 5}), "")
        return P()

    monkeypatch.setattr("subprocess.Popen", fake_run)

    res = executor.run("result = 5", {})
    assert res["status"] == "ok"
    assert json.loads(res["stdout"])["result"] == 5
