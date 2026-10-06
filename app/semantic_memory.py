import json, os
from typing import Any, Dict, List, Optional


class SemanticMemory:
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or os.getenv("SEMANTIC_MEMORY_PATH", "./work/semantic_memory.json")
        self.items: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    self.items = json.load(f)
            except Exception:
                self.items = []

    def _save(self):
        os.makedirs(os.path.dirname(self.storage_path) or ".", exist_ok=True)
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(self.items, f, ensure_ascii=False, indent=2)

    def add_fix(self, issue: str, summary: str, metadata: Optional[Dict[str, Any]] = None):
        self.items.append(
            {
                "kind": "fix",
                "issue": issue,
                "summary": summary,
                "metadata": metadata or {},
            }
        )
        self._save()

    def add_failure(self, issue: str, summary: str, metadata: Optional[Dict[str, Any]] = None):
        self.items.append(
            {
                "kind": "failure",
                "issue": issue,
                "summary": summary,
                "metadata": metadata or {},
            }
        )
        self._save()

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        query_lower = query.lower()
        matches = []
        for item in self.items:
            haystack = f"{item.get('issue', '')} {item.get('summary', '')} {json.dumps(item.get('metadata', {}), ensure_ascii=False)}".lower()
            if query_lower in haystack:
                matches.append(item)
        return matches[:limit]
