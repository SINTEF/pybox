"""
Asynchronous execution queue for sandboxed code execution.

This module provides `AsyncSandboxQueue`, a lightweight concurrency-control
mechanism that limits how many sandbox execution tasks may run at once.
It uses an asyncio semaphore to enforce the concurrency limit and delegates
actual execution to a thread pool via `run_in_executor`.

The queue ensures that untrusted code is executed in a controlled and
non-blocking manner within the FastAPI application.
"""

import asyncio
import logging
from typing import Any, Dict, Callable

from .config import QueueConfig

logger = logging.getLogger("pybox.async_queue")


class AsyncSandboxQueue:
    """Asynchronous queue for managing sandbox execution tasks.

    This class wraps an asyncio semaphore to limit the number of concurrent
    sandbox executions. Each submitted task is executed in a thread pool
    using `loop.run_in_executor`, ensuring that CPU-bound or blocking
    operations do not block the event loop.

    Attributes:
        _semaphore (asyncio.Semaphore): Controls the maximum number of
            concurrent tasks allowed.

    Args:
        max_concurrent (int | None): Optional override for the maximum number
            of concurrent tasks. If not provided, the value is loaded from
            `QueueConfig`.
    """

    def __init__(self, max_concurrent: int | None = None):
        cfg = QueueConfig()
        self._semaphore = asyncio.Semaphore(max_concurrent or cfg.max_concurrent)

    async def submit(
        self,
        func: Callable[..., Dict[str, Any]],
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """Submit a sandbox execution task to the queue.

        The task is executed inside a thread pool using
        `loop.run_in_executor`, ensuring that blocking or CPU-heavy
        operations do not block the asyncio event loop. Concurrency is
        limited by the internal semaphore.

        Args:
            func (Callable[..., Dict[str, Any]]): The function to execute.
                This should be a synchronous function that returns a
                dictionary containing execution results.
            *args: Positional arguments forwarded to `func`.
            **kwargs: Keyword arguments forwarded to `func`.

        Returns:
            Dict[str, Any]: The result returned by `func`.

        """
        async with self._semaphore:
            loop = asyncio.get_running_loop()
            logger.info("Submitting sandbox job")
            return await loop.run_in_executor(
                None,
                lambda: func(*args, **kwargs)
            )
