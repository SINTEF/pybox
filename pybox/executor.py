import json
import logging
import shlex
import subprocess
import time
import uuid
from typing import Any, Dict, Optional

from .config import Config

logger = logging.getLogger("pybox.executor")


# ============================================================
# Errors
# ============================================================

class ExecuteError(Exception):
    def __init__(self, payload: Dict[str, Any]):
        self.__dict__.update(payload)


# ============================================================
# Executor
# ============================================================

class Executor:
    """Secure Docker-based executor with optional fast mode."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self._container_name = None

    # ========================================================
    # Docker command builders
    # ========================================================

    def _base_security_flags(self) -> list[str]:
        cfg = self.config

        flags = [
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges",
            "--pids-limit", str(cfg.pids_limit),
            "--cpus", str(cfg.cpus),
            "--memory", cfg.memory,
            "--memory-swap", cfg.memory,
            "--tmpfs", f"/tmp:ro,noexec,nosuid,size={cfg.tmpfs_size}",
        ]

        if cfg.read_only_root:
            flags.append("--read-only")

        if cfg.network_disabled:
            flags += ["--network", "none"]

        if cfg.userns:
            flags += ["--userns", cfg.userns]

        if cfg.apparmor_profile:
            flags += ["--security-opt", f"apparmor={cfg.apparmor_profile}"]

        if cfg.seccomp_profile:
            flags += ["--security-opt", f"seccomp={cfg.seccomp_profile}"]

        # gVisor runtime
        if cfg.runtime:
            flags += ["--runtime", cfg.runtime]
        if cfg.runtime == "runsc" and self._have_selinux():
            flags += ["--security-opt", "label=disable"]

        return flags

    @staticmethod
    def _have_selinux():
        """Returns true if SELinux is available and enforced."""
        try:
            output = subprocess.check_output(["getenforce"], text=True)
        except:
            return False
        return output.strip() == "Enforcing"

    def _docker_run_cmd(self) -> list[str]:
        """Safe mode: one container per execution."""
        print("*** run")
        return [
            "docker", "run", "--rm", "-i",
            *_self_named_container(self),
            *self._base_security_flags(),
            self.config.image,
        ]

    def _start_fast_container(self):
        """Start long-lived container for fast mode."""
        if self._container_name:
            return

        name = f"pybox-fast-{uuid.uuid4()}"
        self._container_name = name

        cmd = [
            "docker", "run", "-d",
            "--name", name,
            *self._base_security_flags(),
            "--entrypoint", "sleep",  # override entrypoint
            self.config.image,
            "infinity",
        ]

        subprocess.run(cmd, check=True)
        logger.info("Started fast container %s", name)

    def _inspect_entrypoint(self) -> str:
        """Return the entrypoint (or cmd) in the image."""
        def inspect(conf):
            cmd = [
                "docker", "inspect", "-f",
                conf,
                self.config.image,
            ]
            return subprocess.check_output(cmd).decode().strip().strip("[]")
        entrypoint = inspect("{{.Config.Entrypoint}}")
        if not entrypoint:
            entrypoint = inspect("{{.Config.Cmd}}")
        if not entrypoint:
            raise ValueError(
                f"No Entrypoint or Cmd in Docker image: {self.config.image}"
            )
        return shlex.split(entrypoint)


    def _docker_exec_cmd(self) -> list[str]:
        """Exec command for fast mode."""
        cmd = [
            "docker", "exec",
            "-i",
            self._container_name,
        ] + self._inspect_entrypoint()
        return cmd


    # ========================================================
    # Resource stats
    # ========================================================

    def _get_stats(self) -> Dict[str, Any]:
        """Fetch container resource usage (fast mode only)."""
        if not self._container_name:
            return {}

        try:
            proc = subprocess.run(
                ["docker", "stats", self._container_name, "--no-stream", "--format", "{{json .}}"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            return json.loads(proc.stdout.strip())
        except Exception:
            return {}

    # ========================================================
    # Execution
    # ========================================================

    def run(
        self,
        code: str,
        input: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        payload = json.dumps({
            "code": code,
            "input": input or {},
        })

        start = time.time()

        if self.config.fast_mode:
            self._start_fast_container()
            cmd = self._docker_exec_cmd()
        else:
            cmd = self._docker_run_cmd()

        logger.info("Executing code (fast_mode=%s)", self.config.fast_mode)

        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            stdout, stderr = proc.communicate(
                payload,
                timeout=self.config.timeout
            )
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()

            duration = time.time() - start

            return self._log_result({
                "status": "timeout",
                "result": None,
                "errmsg": "Execution timed out",
                "returncode": None,
                "duration": duration,
            })

        duration = time.time() - start

        status = "ok" if proc.returncode == 0 else "error"

        try:
            result = json.loads(stdout).get("result") if stdout else None
        except Exception:
            result = None
            stderr += "\nInvalid JSON output"

        payload = {
            "status": status,
            "result": result,
            "errmsg": stderr.strip() or None,
            "returncode": proc.returncode,
            "duration": duration,
        }

        # Add resource stats in fast mode
        if self.config.fast_mode:
            payload["resources"] = self._get_stats()

        return self._log_result(payload)

    # ========================================================
    # Logging
    # ========================================================

    def _log_result(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Emit structured log."""
        logger.info(
            "pybox.execution",
            extra={"execution": payload},
        )
        return payload

    # ========================================================
    # Cleanup
    # ========================================================

    def close(self):
        if self._container_name:
            subprocess.run(
                ["docker", "rm", "-f", self._container_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            logger.info("Removed fast container %s", self._container_name)
            self._container_name = None


# ============================================================
# Convenience API
# ============================================================

def execute(
    code: str,
    input: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,
) -> Any:
    cfg = Config(**(config or {}))
    executor = Executor(cfg)

    try:
        payload = executor.run(code, input)
    finally:
        if not cfg.fast_mode:
            executor.close()

    if payload["status"] == "ok":
        return payload["result"]

    raise ExecuteError(payload)


def _self_named_container(executor: Executor):
    return ["--name", f"pybox-{uuid.uuid4()}"]
