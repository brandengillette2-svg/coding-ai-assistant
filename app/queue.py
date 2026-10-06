import redis
import json
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.config_prod import settings


class TaskQueue:
    def __init__(self):
        self.redis = redis.from_url(settings.redis.url)
        self.queue_name = settings.redis.queue_name

    def enqueue(self, task_description: str, repo_url: str, branch: str = "main") -> str:
        task_id = str(uuid.uuid4())
        task_data = {
            "id": task_id,
            "description": task_description,
            "repo_url": repo_url,
            "branch": branch,
            "created_at": datetime.utcnow().isoformat(),
        }
        self.redis.lpush(self.queue_name, json.dumps(task_data))
        return task_id

    def dequeue(self) -> Optional[Dict[str, Any]]:
        result = self.redis.rpop(self.queue_name)
        if result:
            return json.loads(result)
        return None

    def get_status(self, task_id: str) -> Optional[str]:
        status = self.redis.get(f"task:{task_id}:status")
        return status.decode() if status else None

    def set_status(self, task_id: str, status: str):
        self.redis.set(f"task:{task_id}:status", status)

    def set_result(self, task_id: str, result: Dict[str, Any], ttl: int = None):
        ttl = ttl or settings.redis.result_ttl
        self.redis.setex(
            f"task:{task_id}:result",
            ttl,
            json.dumps(result, default=str),
        )

    def get_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        result = self.redis.get(f"task:{task_id}:result")
        return json.loads(result) if result else None
