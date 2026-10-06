import json
import os
import subprocess
from typing import Any, Dict, List


class DiffValidator:
    def __init__(self, repo_root: str | None = None):
        self.repo_root = repo_root or os.getenv("REPO_ROOT", ".")

    def get_diff(self) -> str:
        proc = subprocess.run(
            ["git", "-C", self.repo_root, "diff", "--", "."],
            capture_output=True,
            text=True,
        )
        return proc.stdout or ""

    def validate(self, command: str = "pytest -q") -> Dict[str, Any]:
        proc = subprocess.run(
            command,
            shell=True,
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )

        return {
            "passed": proc.returncode == 0,
            "command": command,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "diff": self.get_diff(),
            "score": 100 if proc.returncode == 0 else 40,
        }
