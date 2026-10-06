from typing import Any, Dict, List


class TaskPlanner:
    def __init__(self):
        pass

    def plan(self, task_description: str) -> List[Dict[str, Any]]:
        text = task_description.lower()
        steps: List[Dict[str, Any]] = [
            {"name": "scope_task", "kind": "analysis", "description": "Understand the task and repo surface."},
            {"name": "locate_code", "kind": "lookup", "description": "Find likely files, modules, and symbols."},
        ]

        if any(token in text for token in ["fix", "bug", "error", "fail", "broken", "issue"]):
            steps.append({"name": "reproduce_issue", "kind": "execution", "description": "Run focused reproduction or validation commands."})

        steps.append({"name": "patch_code", "kind": "edit", "description": "Apply the smallest correct fix to relevant files."})
        steps.append({"name": "review_patch", "kind": "review", "description": "Critique the patch for risk and missing validation."})
        steps.append({"name": "verify", "kind": "verification", "description": "Run focused tests and compile checks."})
        steps.append({"name": "summarize", "kind": "report", "description": "Record the result and lessons learned."})
        return steps
