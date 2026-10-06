from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

from app.queue import TaskQueue
from app.storage import get_session, init_db
from app.db import Task as TaskModel
from app.config_prod import settings

app = FastAPI(title="Master Code Wizard API")


class TaskCreate(BaseModel):
    description: str
    repo_url: str
    branch: str = "main"


class TaskResponse(BaseModel):
    id: str
    description: str
    repo_url: str
    branch: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


@app.on_event("startup")
async def startup():
    init_db()


@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.app_version}


@app.post("/tasks")
async def create_task(req: TaskCreate) -> dict:
    """Create and enqueue a new task."""
    queue = TaskQueue()
    task_id = queue.enqueue(
        task_description=req.description,
        repo_url=req.repo_url,
        branch=req.branch,
    )
    return {
        "task_id": task_id,
        "status": "queued",
        "created_at": datetime.utcnow().isoformat(),
    }


@app.get("/tasks/{task_id}")
async def get_task(task_id: str) -> TaskResponse:
    """Get task status and results."""
    session = get_session()
    task = session.query(TaskModel).filter(TaskModel.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskResponse(
        id=task.id,
        description=task.description,
        repo_url=task.repo_url,
        branch=task.branch,
        status=task.status,
        result=task.result,
        error=task.error,
        created_at=task.created_at,
        completed_at=task.completed_at,
    )


@app.get("/tasks")
async def list_tasks(limit: int = 20, skip: int = 0) -> List[TaskResponse]:
    """List recent tasks."""
    session = get_session()
    tasks = (
        session.query(TaskModel)
        .order_by(TaskModel.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        TaskResponse(
            id=task.id,
            description=task.description,
            repo_url=task.repo_url,
            branch=task.branch,
            status=task.status,
            result=task.result,
            error=task.error,
            created_at=task.created_at,
            completed_at=task.completed_at,
        )
        for task in tasks
    ]


@app.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str) -> dict:
    """Cancel a pending or running task."""
    session = get_session()
    task = session.query(TaskModel).filter(TaskModel.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status not in ["pending", "running"]:
        raise HTTPException(status_code=400, detail="Task cannot be cancelled in its current state")

    task.status = "cancelled"
    session.commit()
    return {"task_id": task_id, "status": "cancelled"}
