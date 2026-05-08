import json
import subprocess
import uuid
import logging
import traceback
from typing import Any, Dict, Optional

from .config import Config


logger = logging.getLogger("pybox.executor")


class RunError(Exception):
    """Error running code."""
    def __init__(self, *args):
        self.__dict__.update(args[0])


class Executor:
    def __init__(self, config: Config | None = None):
        self.config = config or Config()

    def _docker_cmd(self) -> list[str]:
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


def run(
    code: str,
    input: "Optional[Dict[str, Any]]" = None,
    config: "Optional[Dict[str, Any]]" = None,
) -> "Any":
    """Convenient runction for running untrusted code.
    """
    c = config if config else {}
    cfg = Config(**c)
    executor = Executor(cfg)
    payload = executor.run(code, input)
    if payload["status"] == "ok":
        return payload["result"]
    raise RunError(payload)
