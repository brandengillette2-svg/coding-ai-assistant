import json
from typing import List

from app.model_client import ModelClient


class Reviewer:
    def __init__(self, model_client: ModelClient):
        self.model_client = model_client

    def review(self, task_description: str, files: List[str], diff: str) -> str:
        if not self.model_client.enabled:
            return json.dumps(
                {
                    "status": "nominal",
                    "warnings": [
                        "Review is running in local mode because no model API key was configured.",
                        "Check edge cases, validation coverage, and the smallest meaningful change.",
                    ],
                    "files": files,
                    "task": task_description,
                },
                indent=2,
            )

        prompt = f"""
You are an expert code reviewer.

Task: {task_description}
Files changed: {json.dumps(files)}
Diff:
{diff}

Review the patch for correctness, edge cases, missing validation, and regression risk. If there are blocking issues, list them clearly; otherwise say the patch looks nominal.
"""
        return self.model_client.chat([{"role": "user", "content": prompt}], temperature=0.1, max_tokens=900)
