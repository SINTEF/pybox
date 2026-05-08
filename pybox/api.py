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
    code: str
    input: Dict[str, Any] = {}

class RunResponse(BaseModel):
    status: str
    result: Any | None = None
    errmsg: str | None = None

@app.post("/run", response_model=RunResponse)
async def run_code(req: RunRequest):
    logger.info("Received /run request")
    payload = await queue.submit(executor.run, req.code, req.input)

    if payload["status"] == "ok":
        return RunResponse(
            status="ok",
            result=payload.get("result"),
            errmsg=payload["errmsg"] or None,
        )

    if result["status"] == "timeout":
        raise HTTPException(status_code=504, detail="Execution timed out")

    return RunResponse(
        status="error",
        result=None,
        errmsg=payload["errmsg"],
    )
