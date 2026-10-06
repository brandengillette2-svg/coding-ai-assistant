import json
from typing import Any, Dict

from app.model_client import ModelClient


class ReviewerService:
    def __init__(self, model_client: ModelClient | None = None):
        self.model = model_client or ModelClient()

    def review_patch(self, task_description: str, diff: str) -> Dict[str, Any]:
        prompt = f"""
You are an expert reviewer.

Task: {task_description}
Patch diff:
{diff}

Return compact JSON:
{
  "score": 0,
  "status": "approved|needs_revision|rejected",
  "issues": ["..."],
  "recommendations": ["..."]
}
"""
        response = self.model.chat([{"role": "user", "content": prompt}], temperature=0.1, max_tokens=1200)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "score": 60,
                "status": "needs_revision",
                "issues": ["Model output could not be parsed as JSON."],
                "recommendations": ["Inspect the patch manually and rerun validation."],
            }
