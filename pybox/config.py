from dataclasses import dataclass

@dataclass
class SandboxConfig:
    image: str = "pybox-sandbox:latest"
    cpus: float = 0.5
    memory: str = "128m"
    pids_limit: int = 64
    timeout_sec: float = 2.0
    tmpfs_size: str = "64m"
    network_disabled: bool = True
    read_only_root: bool = True

@dataclass
class QueueConfig:
    max_concurrent: int = 4
