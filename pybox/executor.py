import json
import subprocess
import uuid
import logging
from typing import Any, Dict
from .config import SandboxConfig

logger = logging.getLogger("pybox.executor")

class SandboxExecutor:
    def __init__(self, config: SandboxConfig | None = None):
        self.config = config or SandboxConfig()

    def _docker_cmd(self) -> list[str]:
        cfg = self.config
        name = f"pybox-{uuid.uuid4()}"

        cmd = [
            "docker", "run", "--rm",
            "--name", name,
            "--pids-limit", str(cfg.pids_limit),
            "--cpus", str(cfg.cpus),
            "--memory", cfg.memory,
            "--memory-swap", cfg.memory,
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges",
            "--tmpfs", f"/tmp:rw,noexec,nosuid,size={cfg.tmpfs_size}",
            "--tmpfs", f"/sandbox:rw,noexec,nosuid,size={cfg.tmpfs_size}",
        ]

        if cfg.read_only_root:
            cmd.append("--read-only")
        if cfg.network_disabled:
            cmd += ["--network", "none"]

        cmd.append(cfg.image)
        return cmd

    def run(self, code: str, input_obj: Dict[str, Any]) -> Dict[str, Any]:
        payload = json.dumps({"code": code, "input": input_obj})
        cmd = self._docker_cmd()

        logger.info("Starting sandbox container")
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            stdout, stderr = proc.communicate(payload, timeout=self.config.timeout_sec)
        except subprocess.TimeoutExpired:
            logger.warning("Sandbox execution timed out")
            proc.kill()
            return {
                "status": "timeout",
                "stdout": "",
                "stderr": "Execution timed out",
                "exit_code": None,
            }

        status = "ok" if proc.returncode == 0 else "error"
        logger.info("Sandbox finished with status %s", status)
        return {
            "status": status,
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": proc.returncode,
        }
