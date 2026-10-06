from typing import List


class SandboxPolicy:
    ALWAYS_ALLOWED = (
        "pytest",
        "python -m pytest",
        "python -m compileall",
        "python - <<'PY'",
        "python -c",
        "git status",
        "git diff",
        "git rev-parse",
        "ls",
        "find",
        "grep",
        "rg",
        "which",
    )

    @classmethod
    def is_allowed(cls, command: str) -> bool:
        normalized = command.strip()
        if not normalized:
            return False
        for prefix in cls.ALWAYS_ALLOWED:
            if normalized.startswith(prefix):
                return True
        return False
