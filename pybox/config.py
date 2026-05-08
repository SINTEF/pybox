from dataclasses import dataclass

@dataclass
class Config:
    #image: str = "ghcr.io/SINTEF/pybox:latest"
    image: str = "pybox:latest"
    cpus: float = 0.5
    memory: str = "128m"
    pids_limit: int = 64
    timeout: float = 2.0  # Timeout in seconds
    tmpfs_size: str = "64m"
    network_disabled: bool = True
    read_only_root: bool = True
    userns: str = "host"          # or a remapped user namespace
    apparmor_profile: str = "docker-default"
    seccomp_profile: str | None = None  # path to seccomp json if you have one

@dataclass
class QueueConfig:
    max_concurrent: int = 4
