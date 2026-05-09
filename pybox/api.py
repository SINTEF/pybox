"""
API module for the pybox sandbox execution service.

This module exposes a FastAPI application that provides an HTTP interface
for executing untrusted Python code inside a sandboxed environment. The
execution is handled asynchronously through a queue system to ensure
controlled concurrency and timeout handling.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
import json
import logging

from .executor import Executor
from .async_queue import AsyncSandboxQueue
from .config import Config

logger = logging.getLogger("pybox.api")

app = FastAPI(title="pybox")

executor = Executor(Config())
queue = AsyncSandboxQueue()


class RunRequest(BaseModel):
    """Request model for the /run endpoint.

    Attributes:
        code (str): The Python code to execute inside the sandbox.
        input (Dict[str, Any]): A dictionary of variables to inject into the
            execution environment. Defaults to an empty dictionary.
    """
    code: str
    input: Dict[str, Any] = {}


class RunResponse(BaseModel):
    """Response model for the /run endpoint.

    Attributes:
        status (str): Execution status. One of:
            - "ok": Execution completed successfully.
            - "error": Execution failed with an exception.
            - "timeout": Execution exceeded the allowed time limit.
        result (Any | None): The returned value from the executed code, if any.
        errmsg (str | None): Error message if execution failed, otherwise None.
    """
    status: str
    result: Any | None = None
    errmsg: str | None = None

@app.post("/run", response_model=RunResponse)
async def run_code(req: RunRequest):
    """Execute untrusted Python code inside the sandbox.

    This endpoint receives Python code and optional input variables, submits
    the execution task to an asynchronous sandbox queue, and returns the
    structured result. Timeouts and execution errors are handled gracefully.

    Args:
        req (RunRequest): The request payload containing the code and input
            variables.

    Returns:
        RunResponse: A structured response containing execution status, result,
        and any error message.

    Raises:
        HTTPException: If the execution times out, an HTTP 504 error is raised.
    """
    logger.info("Received /run request")
    payload = await queue.submit(executor.run, req.code, req.input)

    if payload["status"] == "ok":
        return RunResponse(
            status="ok",
            result=payload.get("result"),
            errmsg=payload["errmsg"] or None,
        )

    if payload["status"] == "timeout":
        raise HTTPException(status_code=504, detail="Execution timed out")

    return RunResponse(
        status="error",
        result=None,
        errmsg=payload["errmsg"],
    )
