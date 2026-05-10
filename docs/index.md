# Pybox

**Pybox** is a lightweight sandbox for executing untrusted Python code inside a secure Docker environment.

## Key features

- Strong isolation using Docker
- Resource limits (CPU, memory, PIDs)
- Optional network isolation
- Configurable security (seccomp, AppArmor)
- Simple JSON-based execution API

## How it works

1. Code is sent to a Docker container via stdin
2. The container executes it safely
3. Output is returned as JSON via stdout

➡️ See [Getting Started](getting-started.md) for usage.
