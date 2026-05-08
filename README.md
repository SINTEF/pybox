# pybox

A small Python library for running untrusted Python code.

The code is executed in a Docker sandbox with JSON I/O.

Pybox includes also a FastAPI service for running the untrusted code.


## Install

```bash
pip install -e .
docker build -t pybox:latest pybox/docker/
```

## Using Python interface

```python
import json
from pybox.executor import SandboxExecutor, SandboxConfig

cfg = SandboxConfig(timeout_sec=3.0)
executor = SandboxExecutor(cfg)

code = "result = x + y"
input = {"x": 2, "y": 3}
result = executor.run(code, input)
print(result)
{'status': 'ok', 'result': 5, 'errmsg': '', 'returncode': 0}

```




## Using the FastAPI interface

Start the FastAPI service
```bash
uvicorn pybox.api:app --reload
```

Send a request

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"code": "result = x + y", "input": {"x": 2, "y": 3}}'

```
