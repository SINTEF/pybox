import json
import logging
import pytest
import textwrap
from pybox.executor import SandboxExecutor, SandboxConfig
from pybox.executor import RunError, run


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def test_simple_code():
    """Test simple code."""
    cfg = SandboxConfig(timeout_sec=3.0)
    executor = SandboxExecutor(cfg)

    code = "result = x + y"
    payload = executor.run(code, {"x": 2, "y": 3})
    print(payload.get("errmsg"))

    assert payload["status"] == "ok"
    assert payload["result"] == 5
    assert payload["errmsg"] == ""
    assert payload["returncode"] == 0


def test_code_with_statements():
    """Test code with import statement."""
    executor = SandboxExecutor()

    code = textwrap.dedent(
        """
        import math

        if x < 4:
            result = math.hypot(x, y)
        """
    )
    payload = executor.run(code, {"x": 3, "y": 4})
    assert payload["result"] == 5

    payload = executor.run(code, {"x": 4, "y": 3})
    assert payload["result"] is None


def test_run():
    """Test the run() runction."""
    assert run("result = x*y", {"x": 2, "y": 4}) == 8

    try:
        run("result = x*y")  # this raises an RunError
    except RunError as exc:
        assert exc.status == "error"
        assert exc.returncode
        assert not exc.result
        assert exc.errmsg.strip().endswith(
            "NameError: name 'x' is not defined"
        )
        #print(exc.errmsg)
    else:
        assert False  # never reached
