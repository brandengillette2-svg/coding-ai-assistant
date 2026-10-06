import json
from typing import Any, Dict, List

from app.config import settings
from app.context_library import ContextLibrary
from app.editor import FileEditor
from app.journal import ProgressJournal
from app.model_client import ModelClient
from app.repo_mapper import RepoMapper
from app.reviewer import Reviewer
from app.task_planner import TaskPlanner
from app.tool_runner import ToolRunner
from app.verifier import Verifier


class CodingAssistant:
    def __init__(self, repo_root: str | None = None):
        self.repo_root = repo_root or str(settings.repo_root)
        self.repo_mapper = RepoMapper(self.repo_root)
        self.context = ContextLibrary(settings.db_path)
        self.journal = ProgressJournal(settings.journal_path)
        self.tool_runner = ToolRunner(settings.work_dir)
        self.editor = FileEditor(self.repo_root)
        self.verifier = Verifier()
        self.planner = TaskPlanner()
        self.model_client = ModelClient(
            provider=settings.model_provider,
            model=settings.model_name,
            api_key=settings.model_api_key,
        )
        self.reviewer = Reviewer(self.model_client)

    def _fetch_relevant_context(self, task_description: str) -> List[str]:
        candidates = self.repo_mapper.find_relevant_files(task_description)
        snippets = []
        for path in candidates:
            try:
                content = self.repo_mapper.read_file(path)
                snippets.append(f"FILE: {path}\n\n{content[:6000]}")
            except Exception:
                continue
        return snippets

    def _llm_plan(self, task_description: str, relevant_context: List[str]) -> str:
        context_block = "\n\n---FILE---\n\n".join(relevant_context) if relevant_context else "No file context found."
        prompt = f"""
You are a senior engineer working inside a repo.

Task: {task_description}

Relevant context:
{context_block}

Return compact JSON only with these fields:
{
  "summary": "...",
  "files_to_edit": ["..."],
  "patch_hints": ["..."],
  "verification_steps": ["...", "..."]
}
"""
        return self.model_client.chat([{"role": "user", "content": prompt}], temperature=0.1, max_tokens=1200)

    def run_task(self, task_description: str) -> Dict[str, Any]:
        self.journal.log("task_started", task_description, repo_root=self.repo_root)

        repo_summary = self.repo_mapper.build_summary()
        self.context.add("repo_summary", "repo_summary", json.dumps(repo_summary))
        self.journal.log("repo_scanned", "Repository scanned", summary=repo_summary)

        plan = self.planner.plan(task_description)
        self.context.add("plan", task_description, json.dumps(plan))
        self.journal.log("plan_created", "Plan generated", plan=plan)

        relevant_context = self._fetch_relevant_context(task_description)
        if relevant_context:
            self.context.add("context", task_description, json.dumps(relevant_context))
            self.journal.log("context_loaded", "Relevant context loaded", files=[c.splitlines()[0].replace("FILE: ", "") for c in relevant_context])

        llm_plan = self._llm_plan(task_description, relevant_context)
        self.context.add("llm_plan", task_description, llm_plan)
        self.journal.log("llm_plan", "Planning response captured", response=llm_plan)

        verification_outputs: List[str] = []
        verification_passed = False

        for step in plan:
            self.journal.log("step", step["name"], kind=step["kind"], description=step["description"])

            if step["kind"] == "execution":
                try:
                    result = self.tool_runner.run_pytest(timeout=180)
                    verification_outputs.extend([result.stdout, result.stderr])
                except PermissionError as exc:
                    self.journal.log("tool_blocked", str(exc), step=step["name"])

            if step["kind"] == "verification":
                try:
                    pytest_result = self.tool_runner.run_pytest(timeout=180)
                    compile_result = self.tool_runner.run_compileall(timeout=180)
                    verification_outputs.extend([
                        pytest_result.stdout,
                        pytest_result.stderr,
                        compile_result.stdout,
                        compile_result.stderr,
                    ])
                    check = self.verifier.evaluate(verification_outputs)
                    verification_passed = check.passed
                    self.journal.log("verification", check.summary, passed=check.passed, details=check.details)
                except PermissionError as exc:
                    self.journal.log("tool_blocked", str(exc), step=step["name"])

        diff = ""
        try:
            diff = self.tool_runner.run_git_diff(timeout=60).stdout
        except PermissionError:
            diff = "git diff unavailable under policy"

        review = self.reviewer.review(task_description, [path for path in self.repo_mapper.find_relevant_files(task_description)], diff)
        self.context.add("review", task_description, review)
        self.journal.log("review", "Patch review recorded", review=review)

        if not verification_passed:
            self.context.add(
                "correction",
                task_description,
                "Validation failed. Narrow scope, inspect failure details, and re-run targeted verification.",
                metadata={"task": task_description},
            )

        self.journal.log("task_completed", task_description, verification_passed=verification_passed)
        return {
            "status": "ok",
            "repo_summary": repo_summary,
            "plan": plan,
            "llm_plan": llm_plan,
            "verification_passed": verification_passed,
            "review": review,
        }
