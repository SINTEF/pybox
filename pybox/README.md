# High‑level architecture


## Host service (trusted):

- Accepts a JSON request: { "code": "...", "input": {...}, "limits": {...} }
- Spawns a one‑shot Docker container with strict limits.
- Pipes JSON input to the container’s stdin.
- Reads stdout (JSON result) and stderr (errors/warnings).
- Kills the container on timeout or resource violation.


## Sandbox container (untrusted code):

- Minimal Python image.
- Entrypoint is a small runner script:
- Reads JSON from stdin.
- Executes user code in a subprocess or exec sandbox.
- Writes JSON result to stdout.
- Writes errors/warnings to stderr.
- No persistent filesystem, no network, no extra capabilities.
- Run the docker container with --read-only and tmpfs mounts so nothing persists
