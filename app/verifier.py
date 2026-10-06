from typing import List

from app.models import VerificationResult


class Verifier:
    def __init__(self):
        pass

    def evaluate(self, outputs: List[str]) -> VerificationResult:
        if not outputs:
            return VerificationResult(
                passed=False,
                summary="No verification outputs were received.",
                details=["No command output was collected."],
            )

        merged = "\n".join(outputs)
        failure_markers = ["FAILED", "FAIL", "ERROR", "TRACEBACK", "AssertionError", "ModuleNotFoundError"]
        failed_lines = [
            line.strip()
            for line in merged.splitlines()
            if line.strip() and any(marker in line.upper() for marker in failure_markers)
        ]

        if failed_lines:
            return VerificationResult(
                passed=False,
                summary="Verification failed.",
                details=failed_lines[:20],
            )

        return VerificationResult(
            passed=True,
            summary="Verification succeeded.",
            details=[f"Validated {len(outputs)} output set(s) without failure markers."],
        )
