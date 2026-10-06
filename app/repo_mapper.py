import os
import re
from pathlib import Path
from typing import Dict, List


class RepoMapper:
    def __init__(self, repo_root: str | Path):
        self.repo_root = Path(repo_root).resolve()

    def scan(self) -> Dict[str, List[str]]:
        result: Dict[str, List[str]] = {}
        ignored_dirs = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache", "dist", "build"}

        for root, dirs, files in os.walk(self.repo_root):
            dirs[:] = [d for d in dirs if d not in ignored_dirs]
            for file in files:
                rel = str((Path(root) / file).relative_to(self.repo_root))
                ext = (Path(file).suffix or "noext").lower()
                result.setdefault(ext, []).append(rel)

        return result

    def read_file(self, relative_path: str) -> str:
        full_path = (self.repo_root / relative_path).resolve()
        if not full_path.exists():
            raise FileNotFoundError(relative_path)
        return full_path.read_text(encoding="utf-8", errors="replace")

    def find_symbol_mentions(self, symbol: str, extensions=None) -> List[str]:
        exts = extensions or {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java"}
        matches: List[str] = []

        for root, dirs, files in os.walk(self.repo_root):
            dirs[:] = [d for d in dirs if d not in {".git", ".venv", "venv", "node_modules", "__pycache__"}]
            for file in files:
                full = Path(root) / file
                if full.suffix.lower() not in exts:
                    continue
                try:
                    text = full.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue
                if re.search(rf"\b{re.escape(symbol)}\b", text):
                    matches.append(str(full.relative_to(self.repo_root)))

        return matches

    def find_relevant_files(self, task_description: str, limit: int = 8) -> List[str]:
        tokens = re.findall(r"[a-zA-Z0-9_./-]+", task_description.lower())
        keywords = [t for t in tokens if len(t) > 2]
        if not keywords:
            return []

        score_map: Dict[str, int] = {}
        for root, dirs, files in os.walk(self.repo_root):
            dirs[:] = [d for d in dirs if d not in {".git", ".venv", "venv", "node_modules", ".pytest_cache", "__pycache__"}]
            for file in files:
                full = Path(root) / file
                rel = str(full.relative_to(self.repo_root))
                haystack = (rel + " " + full.name).lower()
                score = 0
                for kw in keywords:
                    if kw in haystack:
                        score += 2
                if score > 0:
                    score_map[rel] = score

        ranked = sorted(score_map.items(), key=lambda item: item[1], reverse=True)
        return [path for path, _ in ranked[:limit]]

    def build_summary(self) -> Dict[str, object]:
        scanned = self.scan()
        return {
            "repo_root": str(self.repo_root),
            "total_files": sum(len(v) for v in scanned.values()),
            "file_types": dict(sorted(scanned.items())),
        }
