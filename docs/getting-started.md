# Getting Started

## Installation

```bash
pip install -e .
```

Ensure Docker is installed and running.



## Basic example

```python
from pybox.executor import execute

result = execute(
    code="""
result = 1 + 2
"""
)

print(result)  # 3

```


## With input

```python
result = execute(
    code="""
result = x + y
""",
    input={"x": 10, "y": 5}
)

print(result)  # 15

```


## Error handling

```python
from pybox.executor import ExecuteError

try:
    execute("raise ValueError('boom')")
except ExecuteError as e:
    print(e.errmsg)

```
