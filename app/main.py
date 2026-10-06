from fastapi import FastAPI
from pydantic import BaseModel

from app.assistant import CodingAssistant

app = FastAPI(title="Master Code Wizard")


class TaskRequest(BaseModel):
    description: str
    repo_root: str | None = None


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/task")
async def run_task(req: TaskRequest):
    assistant = CodingAssistant(req.repo_root)
    return assistant.run_task(req.description)
