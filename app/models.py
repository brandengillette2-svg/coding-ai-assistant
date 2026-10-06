from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Task:
    id: str
    description: str
    repo_root: str
    status: str = "pending"
    created_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class Step:
    name: str
    kind: str
    description: str = ""


@dataclass
class ToolResult:
    command: str
    returncode: int
    stdout: str
    stderr: str
    duration_sec: float


@dataclass
class VerificationResult:
    passed: bool
    summary: str
    details: List[str] = field(default_factory=list)


@dataclass
class MemoryItem:
    key: str
    kind: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
