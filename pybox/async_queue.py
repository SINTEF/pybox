import asyncio
import logging
from typing import Any, Dict, Callable, Awaitable
from .config import QueueConfig

logger = logging.getLogger("pybox.async_queue")

class AsyncSandboxQueue:
    def __init__(self, max_concurrent: int | None = None):
        cfg = QueueConfig()
        self._semaphore = asyncio.Semaphore(max_concurrent or cfg.max_concurrent)

    async def submit(self, func: Callable[..., Dict[str, Any]], *args, **kwargs) -> Dict[str, Any]:
        async with self._semaphore:
            loop = asyncio.get_running_loop()
            logger.info("Submitting sandbox job")
            return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
