import asyncio
import json
import logging
import pytest
from pybox import AsyncExecutor, Config


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

async def test_simple_code():
    """Test simple code."""
    cfg = Config(timeout=3.0, fast_mode=True)
    executor = AsyncExecutor(cfg)
    await executor.start()

    code = "result = x + 2*y"
    tasks = [
        executor.run(code, {"x": 1, "y": i})
        for i in range(10)
    ]
    print("*** xxx")
    x = await asyncio.gather(*tasks)
    print("*** x =", x)


asyncio.run(test_simple_code())
