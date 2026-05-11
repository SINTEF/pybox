import json
import logging
import pytest
import textwrap
from pybox.executor import Executor, Config
from pybox.executor import ExecuteError, execute


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

def test_simple_code():
    """Test simple code."""
    cfg = Config(timeout=3.0)
    executor = Executor(cfg)

    code = "result = x + y"
    status = executor.run(code, {"x": 2, "y": 3})
    print(status.get("errmsg"))

    assert status["status"] == "ok"
    assert status["result"] == 5
    assert status["errmsg"] is None
    assert status["returncode"] == 0


def test_code_with_statements():
    """Test code with import statement."""
    executor = Executor()

    code = textwrap.dedent(
        """
        import math

        if x < 4:
            result = math.hypot(x, y)
        """
    )
    status = executor.run(code, {"x": 3, "y": 4})
    assert status["result"] == 5.0

    status = executor.run(code, {"x": 4, "y": 3})
    assert status["result"] is None


def test_execute():
    """Test the run() runction."""
    assert execute("result = x*y", {"x": 2, "y": 4}) == 8

    try:
        execute("result = x*y")  # this raises an RunError
    except ExecuteError as exc:
        assert exc.status == "error"
        assert exc.returncode
        assert not exc.result
        assert exc.errmsg.strip().endswith(
            "NameError: name 'x' is not defined"
        )
        #print(exc.errmsg)
    else:
        assert False  # never reached


def test_fast_mode():
    """Test fast mode."""
    cfg = Config(timeout=5.0, fast_mode=True)

    executor = Executor(cfg)

    code = "result = x - y"
    status = executor.run(code, {"x": 2, "y": 3})
    print(status.get("errmsg"))

    assert status["status"] == "ok"
    assert status["result"] == -1
    assert status["errmsg"] is None
    assert status["returncode"] == 0
