import json
from typing import Any, Dict, List

from app.model_client import ModelClient


class PlannerService:
    def __init__(self, model_client: ModelClient | None = None):
        self.model = model_client or ModelClient()

    def create_plan(self, task_description: str, relevant_files: List[str]) -> Dict[str, Any]:
        prompt = f"""
You are a senior engineer planning a code change.

Task: {task_description}
Candidate files:
{json.dumps(relevant_files, indent=2)}

Return compact JSON:
{
  "summary": "...",
  "files_to_edit": ["..."],
  "steps": ["..."],
  "verification_steps": ["..."],
  "risks": ["..."]
}
"""
        result = self.model.chat([{"role": "user", "content": prompt}], temperature=0.1, max_tokens=1200)
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {
                "summary": result,
                "files_to_edit": relevant_files,
                "steps": ["inspect files", "patch", "verify"],
                "verification_steps": ["pytest -q"],
                "risks": ["fallback plan used because model output was not valid JSON"],
            }
