# pybox

Secure Docker-based Python sandbox with JSON I/O, asyncio queue, and FastAPI API.

## Install

```bash
pip install -e .
docker build -t pybox-sandbox:latest pybox/docker/
```

## Run API

```bash
uvicorn pybox.api:app --reload
```


## Example request

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"code": "result = input_data[\"x\"] + input_data[\"y\"]", "input": {"x": 2, "y": 3}}'

```
