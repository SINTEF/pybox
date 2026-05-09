import json
import subprocess
import uuid
import logging
import traceback
from typing import Any, Dict, Optional

from .config import Config


logger = logging.getLogger("pybox.executor")


class ExecuteError(Exception):
    """Exception raised when execution of code inside the container fails.

    The exception is initialized with a dictionary payload returned from the
    execution engine. The payload is unpacked into the exception's __dict__,
    making fields like `status`, `errmsg`, and `returncode` directly accessible.

    Args:
        *args: Expected to contain a single dictionary with execution metadata.
    """

    def __init__(self, *args):
        self.__dict__.update(args[0])


class Executor:
    """Docker-based executor for running untrusted Python code safely.

    This class wraps execution of code inside an isolated Docker container
    configured with strict security and resource limits.

    Args:
        config: Optional configuration object defining container limits and
            security settings. If not provided, a default `Config` is used.
    """

    def __init__(self, config: Config | None = None):
        """Initializes the executor with a given configuration.

        Args:
            config: Optional `Config` instance. Defaults to a new `Config`
                with default values.
        """
        self.config = config or Config()

    def _docker_cmd(self) -> list[str]:
        """Construct the Docker command used to run the container.

        The command includes resource constraints (CPU, memory), security
        restrictions (no new privileges, dropped capabilities), and filesystem
        isolation (read-only root, tmpfs).

        Returns:
            list[str]: The full Docker command as a list of CLI arguments.
        """
        cfg = self.config
        name = f"pybox-{uuid.uuid4()}"

        cmd = [
            "docker", "run", "--rm", "-i",
            "--name", name,
            "--pids-limit", str(cfg.pids_limit),
            "--cpus", str(cfg.cpus),
            "--memory", cfg.memory,
            "--memory-swap", cfg.memory,
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges",
            "--tmpfs", f"/tmp:ro,noexec,nosuid,size={cfg.tmpfs_size}",
        ]

        if cfg.read_only_root:
            cmd.append("--read-only")
        if cfg.network_disabled:
            cmd += ["--network", "none"]
        if cfg.userns:
            cmd += ["--userns", cfg.userns]
        if cfg.apparmor_profile:
            cmd += ["--security-opt", f"apparmor={cfg.apparmor_profile}"]
        if cfg.seccomp_profile:
            cmd += ["--security-opt", f"seccomp={cfg.seccomp_profile}"]

        cmd.append(cfg.image)
        return cmd

    def run(
        self,
        code: str,
        input: "Optional[Dict[str, Any]]" = None,
    ) -> "Dict[str, Any]":
        """Execute Python code inside an isolated Docker container.

        The code and input are serialized into JSON and passed via stdin to
        the container. The container is expected to return a JSON response
        on stdout.

        Args:
            code: Python code to execute inside the container.
            input: Optional dictionary of input data made available to the
                executed code.

        Returns:
            Dict[str, Any]: A dictionary containing execution results with keys:
                - "status": Execution status ("ok", "error", or "timeout").
                - "result": The returned result from the executed code (if any).
                - "errmsg": Standard error output from the container.
                - "returncode": Process return code from the container.

        Notes:
            - If execution exceeds the configured timeout, the container is killed.
            - The container must output valid JSON to stdout for result parsing.
        """
        input_obj = input if input else {}
        payload = json.dumps({"code": code, "input": input_obj})
        cmd = self._docker_cmd()

        logger.info("Starting pybox container")
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            stdout, stderr = proc.communicate(
                payload, timeout=self.config.timeout
            )
        except subprocess.TimeoutExpired:
            logger.warning("Pybox execution timed out")
            proc.kill()
            return {
                "status": "timeout",
                "result": None,
                "errmsg": "Execution timed out",
                "returncode": None,
            }

        status = "ok" if proc.returncode == 0 else "error"
        logger.info("Pybox finished with status %s", status)

        result = json.loads(stdout).get("result") if stdout else None
        return {
            "status": status,
            "result": result,
            "errmsg": stderr,
            "returncode": proc.returncode,
        }


def execute(
    code: str,
    input: "Optional[Dict[str, Any]]" = None,
    config: "Optional[Dict[str, Any]]" = None,
) -> "Any":
    """Convenience function for executing untrusted code.

    This is a high-level wrapper around `Executor` that simplifies usage by:
    - Accepting a raw config dictionary
    - Returning the result directly on success
    - Raising an exception on failure

    Args:
        code: Python code to execute.
        input: Optional dictionary of input data passed to the code.
        config: Optional dictionary of configuration parameters that will be
            used to instantiate a `Config` object.

    Returns:
        Any: The result of the executed code if successful.

    Raises:
        ExecuteError: If execution fails or returns a non-"ok" status.
    """
    c = config if config else {}
    cfg = Config(**c)
    executor = Executor(cfg)
    payload = executor.run(code, input)
    if payload["status"] == "ok":
        return payload["result"]
    raise ExecuteError(payload)
