import os
import re
from pathlib import Path
from typing import Dict, List, Optional
from app.config_prod import settings


class SemanticIndex:
    def __init__(self):
        self.repo_root = settings.repo_root
        self.ignored_dirs = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache"}

    def extract_symbols(self, file_path: str) -> List[Dict[str, str]]:
        """Extract function, class, and method definitions from a code file."""
        full_path = self.repo_root / file_path
        if not full_path.exists():
            return []

        try:
            content = full_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return []

        symbols = []
        ext = full_path.suffix.lower()

        if ext == ".py":
            symbols.extend(self._extract_python_symbols(content, file_path))
        elif ext in {".js", ".ts", ".tsx", ".jsx"}:
            symbols.extend(self._extract_js_symbols(content, file_path))

        return symbols

    def _extract_python_symbols(self, content: str, file_path: str) -> List[Dict[str, str]]:
        symbols = []
        # Simple regex-based extraction
        class_pattern = r"^class\s+(\w+)\s*(?:\([^)]*\))?:"
        func_pattern = r"^def\s+(\w+)\s*\("

        for match in re.finditer(class_pattern, content, re.MULTILINE):
            symbols.append(
                {
                    "name": match.group(1),
                    "kind": "class",
                    "file": file_path,
                    "line": content[:match.start()].count("\n") + 1,
                }
            )

        for match in re.finditer(func_pattern, content, re.MULTILINE):
            symbols.append(
                {
                    "name": match.group(1),
                    "kind": "function",
                    "file": file_path,
                    "line": content[:match.start()].count("\n") + 1,
                }
            )

        return symbols

    def _extract_js_symbols(self, content: str, file_path: str) -> List[Dict[str, str]]:
        symbols = []
        # Simple regex-based extraction
        func_pattern = r"(?:async\s+)?function\s+(\w+)|const\s+(\w+)\s*=|let\s+(\w+)\s*="
        class_pattern = r"class\s+(\w+)"

        for match in re.finditer(class_pattern, content):
            symbols.append(
                {
                    "name": match.group(1),
                    "kind": "class",
                    "file": file_path,
                    "line": content[:match.start()].count("\n") + 1,
                }
            )

        for match in re.finditer(func_pattern, content):
            name = match.group(1) or match.group(2) or match.group(3)
            if name:
                symbols.append(
                    {
                        "name": name,
                        "kind": "function",
                        "file": file_path,
                        "line": content[:match.start()].count("\n") + 1,
                    }
                )

        return symbols

    def index_repo(self) -> List[Dict[str, str]]:
        """Index all code symbols in the repository."""
        all_symbols = []

        for root, dirs, files in os.walk(self.repo_root):
            dirs[:] = [d for d in dirs if d not in self.ignored_dirs]
            for file in files:
                full_path = Path(root) / file
                rel_path = str(full_path.relative_to(self.repo_root))
                symbols = self.extract_symbols(rel_path)
                all_symbols.extend(symbols)

        return all_symbols

    def find_relevant_symbols(self, task_description: str, limit: int = 10) -> List[Dict[str, str]]:
        """Find symbols relevant to a task description."""
        tokens = re.findall(r"[a-zA-Z0-9_./-]+", task_description.lower())
        keywords = [t for t in tokens if len(t) > 2]

        all_symbols = self.index_repo()
        scored_symbols = []

        for symbol in all_symbols:
            score = 0
            name_lower = symbol["name"].lower()
            for kw in keywords:
                if kw in name_lower:
                    score += 3
            if score > 0:
                scored_symbols.append((symbol, score))

        ranked = sorted(scored_symbols, key=lambda x: x[1], reverse=True)
        return [symbol for symbol, _ in ranked[:limit]]
