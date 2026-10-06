import json
from pathlib import Path
from typing import Any, Dict

from app.editor import FileEditor


class CoderService:
    def __init__(self, repo_root: str = "."):
        self.repo_root = repo_root
        self.editor = FileEditor(repo_root)

    def apply_patch(self, file_path: str, new_content: str) -> Dict[str, Any]:
        self.editor.write_text(file_path, new_content)
        return {
            "status": "patched",
            "file": file_path,
        }

    def apply_change(self, file_path: str, replace_text: str, replacement_text: str) -> Dict[str, Any]:
        self.editor.replace(file_path, replace_text, replacement_text)
        return {
            "status": "patched",
            "file": file_path,
        }
