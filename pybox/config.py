from pydantic import BaseModel, Field
from typing import Optional


class Config(BaseModel):
    image: str = Field(
        default="ghcr.io/sintef/pybox:latest",
        json_schema_extra={
            "description": "Container image used to execute workloads.",
            "example": "ghcr.io/sintef/pybox:latest",
        },
    )

    cpus: float = Field(
        default=0.5,
        gt=0,
        json_schema_extra={
            "description": "Number of CPU cores allocated to the container.",
            "example": 0.5,
        },
    )

    memory: str = Field(
        default="128m",
        json_schema_extra={
            "description": "Memory limit for the container (Docker format, e.g. '128m', '1g').",
            "example": "256m",
        },
    )

    pids_limit: int = Field(
        default=64,
        gt=0,
        json_schema_extra={
            "description": "Maximum number of processes allowed in the container.",
            "example": 64,
        },
    )

    timeout: float = Field(
        default=5.0,
        gt=0,
        json_schema_extra={
            "description": "Execution timeout in seconds before the container is terminated.",
            "example": 10.0,
        },
    )

    tmpfs_size: str = Field(
        default="64m",
        json_schema_extra={
            "description": "Size of temporary filesystem mounted inside the container.",
            "example": "128m",
        },
    )

    network_disabled: bool = Field(
        default=True,
        json_schema_extra={
            "description": "Disable networking inside the container for security isolation.",
        },
    )

    read_only_root: bool = Field(
        default=True,
        json_schema_extra={
            "description": "Mount container root filesystem as read-only.",
        },
    )

    userns: str = Field(
        default="host",
        json_schema_extra={
            "description": "User namespace mode (e.g., 'host' or a remapped namespace).",
            "example": "host",
        },
    )

    apparmor_profile: str = Field(
        default="docker-default",
        json_schema_extra={
            "description": "AppArmor profile applied to the container.",
            "example": "docker-default",
        },
    )

    seccomp_profile: Optional[str] = Field(
        default=None,
        json_schema_extra={
            "description": "Path to a seccomp JSON profile for syscall filtering.",
            "examples": ["/path/to/seccomp.json"],
        },
    )


class QueueConfig(BaseModel):
    max_concurrent: int = Field(
        default=4,
        gt=0,
        json_schema_extra={
            "description": "Maximum number of concurrent jobs allowed in the queue.",
            "example": 4,
        },
    )
