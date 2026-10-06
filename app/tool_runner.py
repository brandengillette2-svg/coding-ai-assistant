import subprocess
import time
from pathlib import Path
from typing import Optional

from app.models import ToolResult
from app.sandbox import SandboxPolicy


class ToolRunner:
    def __init__(self, work_dir: str | Path):
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)

    def run(self, command: str, timeout: int = 120, cwd: Optional[str | Path] = None) -> ToolResult:
        if not SandboxPolicy.is_allowed(command):
            raise PermissionError(f"Command is blocked by sandbox policy: {command}")

        start = time.time()
        proc = subprocess.run(
            command,
            shell=True,
            cwd=str(cwd or self.work_dir),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        duration = time.time() - start
        return ToolResult(
            command=command,
            returncode=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            duration_sec=duration,
        )

    def run_pytest(self, target: str = "", timeout: int = 300) -> ToolResult:
        command = "pytest"
        if target:
            command = f"pytest {target}"
        return self.run(command, timeout=timeout)

    def run_compileall(self, target: str = ".", timeout: int = 300) -> ToolResult:
        return self.run(f"python -m compileall {target}", timeout=timeout)

    def run_git_status(self, timeout: int = 60) -> ToolResult:
        return self.run("git status --short", timeout=timeout)

    def run_git_diff(self, timeout: int = 60) -> ToolResult:
        return self.run("git diff -- .", timeout=timeout)
