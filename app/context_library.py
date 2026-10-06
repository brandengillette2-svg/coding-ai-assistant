import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional


class ContextLibrary:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS context (
                id TEXT PRIMARY KEY,
                kind TEXT,
                key TEXT,
                content TEXT,
                metadata TEXT,
                created_at TEXT
            )
            """
        )
        conn.commit()
        conn.close()

    def add(self, kind: str, key: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        import uuid
        from datetime import datetime

        entry_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            INSERT INTO context (id, kind, key, content, metadata, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                entry_id,
                kind,
                key,
                content,
                json.dumps(metadata or {}, ensure_ascii=False),
                datetime.utcnow().isoformat(),
            ),
        )
        conn.commit()
        conn.close()

    def search(self, query: str, kind: Optional[str] = None, limit: int = 8) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        q = f"%{query}%"

        if kind:
            rows = conn.execute(
                """
                SELECT key, content, metadata, created_at
                FROM context
                WHERE kind = ? AND (key LIKE ? OR content LIKE ?)
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (kind, q, q, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT key, content, metadata, created_at
                FROM context
                WHERE key LIKE ? OR content LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (q, q, limit),
            ).fetchall()

        conn.close()
        return [
            {
                "key": row[0],
                "content": row[1],
                "metadata": json.loads(row[2]) if row[2] else {},
                "created_at": row[3],
            }
            for row in rows
        ]

    def list_recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        rows = conn.execute(
            """
            SELECT key, content, metadata, created_at
            FROM context
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        conn.close()
        return [
            {
                "key": row[0],
                "content": row[1],
                "metadata": json.loads(row[2]) if row[2] else {},
                "created_at": row[3],
            }
            for row in rows
        ]
