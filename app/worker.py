import redis
import json
import uuid
import time
from datetime import datetime
from typing import Any, Dict, Optional, List
from app.config_prod import settings
from app.storage import get_session
from app.db import Task as TaskModel, Step, JournalEntry
from app.queue import TaskQueue
from app.assistant import CodingAssistant
from app.journal import ProgressJournal


class TaskWorker:
    def __init__(self):
        self.queue = TaskQueue()
        self.session = get_session()
        self.journal = ProgressJournal(settings.journal_path)

    def run(self, max_iterations: Optional[int] = None):
        """Main worker loop."""
        iteration = 0
        while True:
            if max_iterations and iteration >= max_iterations:
                break

            try:
                task_data = self.queue.dequeue()
                if task_data:
                    self.process_task(task_data)
                else:
                    time.sleep(1)  # No tasks, wait before retrying
            except Exception as exc:
                self.journal.log("worker_error", str(exc))
                time.sleep(5)

            iteration += 1

    def process_task(self, task_data: Dict[str, Any]):
        """Process a single task."""
        task_id = task_data["id"]
        description = task_data["description"]
        repo_url = task_data["repo_url"]
        branch = task_data.get("branch", "main")

        print(f"Processing task {task_id}: {description[:50]}...")
        self.queue.set_status(task_id, "running")

        # Create task record in DB
        task_model = TaskModel(
            id=task_id,
            description=description,
            repo_url=repo_url,
            branch=branch,
            status="running",
        )
        self.session.add(task_model)
        self.session.commit()

        try:
            # Run the assistant
            assistant = CodingAssistant(repo_root="./repos")
            result = assistant.run_task(description)

            # Update task status
            task_model.status = "completed"
            task_model.result = result
            task_model.completed_at = datetime.utcnow()
            self.session.commit()

            # Set result in Redis
            self.queue.set_result(task_id, result)
            self.queue.set_status(task_id, "completed")
            self.journal.log("task_completed", description, task_id=task_id)

        except Exception as exc:
            task_model.status = "failed"
            task_model.error = str(exc)
            task_model.completed_at = datetime.utcnow()
            self.session.commit()

            self.queue.set_status(task_id, "failed")
            self.journal.log("task_failed", str(exc), task_id=task_id)


if __name__ == "__main__":
    worker = TaskWorker()
    worker.run()
