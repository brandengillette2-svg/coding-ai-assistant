from pathlib import Path


class FileEditor:
    def __init__(self, repo_root: str | Path):
        self.repo_root = Path(repo_root).resolve()

    def write_text(self, relative_path: str, content: str):
        full_path = (self.repo_root / relative_path).resolve()
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")

    def replace(self, relative_path: str, old_text: str, new_text: str):
        full_path = (self.repo_root / relative_path).resolve()
        original = full_path.read_text(encoding="utf-8")
        if old_text not in original:
            raise ValueError(f"Old text not found in {relative_path}")
        updated = original.replace(old_text, new_text)
        full_path.write_text(updated, encoding="utf-8")

    def append(self, relative_path: str, content: str):
        full_path = (self.repo_root / relative_path).resolve()
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with full_path.open("a", encoding="utf-8") as f:
            f.write(content)

    def read_text(self, relative_path: str) -> str:
        return (self.repo_root / relative_path).read_text(encoding="utf-8", errors="replace")
