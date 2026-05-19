import asyncio
from typing import Any
from .executor import Executor, ExecuteError
from .config import Config


class AsyncExecutor:
    def __init__(self, config: Config, max_concurrent: int = 4):
        self.executor = Executor(config)
        self.queue: asyncio.Queue = asyncio.Queue()
        self.workers = []
        self.max_concurrent = max_concurrent

    async def start(self):
        for _ in range(self.max_concurrent):
            self.workers.append(
                asyncio.create_task(self._worker())
            )

    async def _worker(self):
        while True:
            code, input, fut = await self.queue.get()
            try:
                result = await asyncio.to_thread(
                    self.executor.run,
                    code,
                    input,
                )
                if result["status"] == "ok":
                    fut.set_result(result["result"])
                else:
                    fut.set_exception(ExecuteError(result))
            except Exception as e:
                fut.set_exception(e)
            finally:
                self.queue.task_done()

    async def run(self, code: str, input: dict | None = None) -> Any:
        fut = asyncio.get_running_loop().create_future()
        await self.queue.put((code, input, fut))
        return await fut

    async def close(self):
        for w in self.workers:
            w.cancel()
