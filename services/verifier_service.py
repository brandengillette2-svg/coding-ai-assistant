from typing import Any, Dict, List

from app.tool_runner import ToolRunner
from app.verifier import Verifier


class VerifierService:
    def __init__(self, work_dir: str = "./work"):
        self.tool_runner = ToolRunner(work_dir)
        self.verifier = Verifier()

    def verify(self, task_description: str, commands: List[str]) -> Dict[str, Any]:
        outputs = []
        for command in commands:
            result = self.tool_runner.run(command, timeout=180)
            outputs.extend([result.stdout, result.stderr])

        check = self.verifier.evaluate(outputs)
        return {
            "status": "passed" if check.passed else "failed",
            "summary": check.summary,
            "details": check.details,
        }
