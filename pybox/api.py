from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
import json
import logging

from .executor import SandboxExecutor
from .async_queue import AsyncSandboxQueue
from .config import SandboxConfig

logger = logging.getLogger("pybox.api")

app = FastAPI(title="pybox")

executor = SandboxExecutor(SandboxConfig())
queue = AsyncSandboxQueue()

class RunRequest(BaseModel):
    code: str
    input: Dict[str, Any] = {}

class RunResponse(BaseModel):
    status: str
    result: Any | None = None
    stderr: str | None = None

@app.post("/run", response_model=RunResponse)
async def run_code(req: RunRequest):
    logger.info("Received /run request")
    result = await queue.submit(executor.run, req.code, req.input)

    if result["status"] == "ok":
        try:
            payload = json.loads(result["stdout"] or "{}")
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Sandbox returned invalid JSON")

        return RunResponse(
            status="ok",
            result=payload.get("result"),
            stderr=result["stderr"] or None,
        )

    if result["status"] == "timeout":
        raise HTTPException(status_code=504, detail="Execution timed out")

    return RunResponse(
        status="error",
        result=None,
        stderr=result["stderr"],
    )
