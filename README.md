<img src="https://raw.githubusercontent.com/SINTEF/pybox/master/docs/pybox-logo_name.svg" align="right" />

<!--
[![PyPi](https://img.shields.io/pypi/v/dlite-python.svg)](https://pypi.org/project/dlite-python/)
-->
[![CI tests](https://github.com/sintef/pybox/workflows/CI%20tests/badge.svg)](https://github.com/SINTEF/pybox/actions)
<!--
[![Documentation](https://img.shields.io/badge/documentation-informational?logo=githubpages)](https://sintef.github.io/pybox/index.html)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7811078.svg)](https://doi.org/10.5281/zenodo.7811078)
-->

> A lightweight library to run untrusted Python code


# pybox

A small Python library for running untrusted Python code.

The code is executed in a Docker sandbox with JSON I/O.

Pybox includes also a FastAPI service for running the untrusted code.


## Install

```bash
pip install -e .
docker build -t pybox:latest pybox/docker/
```

## Running untrusted code from Python

```python
from pybox import Executor, Config

cfg = Config(timeout=3.0)
executor = Executor(cfg)

code = "result = x + y"
input = {"x": 2, "y": 3}
result = executor.run(code, input)
print(result)
{'status': 'ok', 'result': 5, 'errmsg': '', 'returncode': 0}

```

Pybox includes also a convenient run() function

```python
from pybox import RunError, run

code = """
import math
result = math.hypot(x, y)
"""
input = {"x": 3, "y": 4}
result = run(code, input, config={"timeout": 3.0})
print(result)
5.0

```


## Using the FastAPI service

Start the service
```bash
uvicorn pybox.api:app --reload
```

Send a request

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"code": "result = x + y", "input": {"x": 2, "y": 3}}'

```
