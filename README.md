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


# Pybox
Pybox is a lightweight Python library for running untrusted Python code.
It tries to offer a reasonable tradeoff between security and user-friendliness.

The untrusted code is executed in a protected Docker sandbox with (most) side-effects disabled.
All I/O is passed as JSON via the standard input, standard output and standard error.

Main features:
- ✅ Protected Docker sandbox, offering protection against:
    - code escape attempts
    - fork bombs (pids_limit)
    - memory abuse
    - file system writes
    - network exfiltration (optional)
- ✅ Optional gVisor integration for enhanced security (highly recommended)
- ✅ Optional fast mode with container pool (faster but less secure)
- ✅ Provides both a Python and a FastAPI interface


Pybox is designed so you can switch between a safe and fast mode:

| Mode           | Behavior                         | Security   | Performance |
|----------------|----------------------------------|------------|-------------|
| safe (default) | destroy container after each run | ⭐⭐⭐⭐⭐ | slower      |
| fast           | reuse warm containers            | ⭐⭐⭐     | much faster |



## Install

Install Pybox with

```bash
pip install -e .
docker build -t pybox:latest pybox/docker/
```

Optionally, follow [these instructions](docs/install_gvisor.md) to install [gVisor] for enhanced security against kernel exploits.


## Running untrusted code from Python

```python
from pybox import Executor, Config

cfg = Config(timeout=3.0)
executor = Executor(cfg)

code = "result = x + y"
input = {"x": 2, "y": 3}
result = executor.run(code, input)
print(result)
{'status': 'ok', 'result': 5, 'errmsg': None, 'returncode': 0}

```

Pybox includes also a convenient execute() function

```python
from pybox import ExecuteError, execute

code = """
import math
result = math.hypot(x, y)
"""
input = {"x": 3, "y": 4}
result = execute(code, input, config={"timeout": 3.0})
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

It should return a JSON response with the result:

```json
{"status": "ok", "result": 5, "errmsg": null}
```
