# Master Code Wizard

A serious coding agent scaffold for real repository work.

This project is designed around the core capabilities that matter most in production:
- repository-aware code discovery
- task planning and decomposition
- safe command execution with a sandbox policy
- verification-first validation
- correction memory and journaling
- reviewer pass before patch acceptance
- real model integration when an API key is configured

## Architecture overview

The project follows a disciplined execution loop:
1. map the repository
2. gather relevant code and memory
3. plan the task
4. patch only the relevant files
5. execute verification commands
6. review patch quality
7. store useful corrections
8. retry if validation fails

## Included modules

- `app/config.py` — environment settings
- `app/models.py` — DTOs and result types
- `app/model_client.py` — LLM integration for OpenAI and Anthropic
- `app/repo_mapper.py` — repo scan, symbol lookup, and relevance ranking
- `app/context_library.py` — persistent memory store
- `app/journal.py` — execution journaling
- `app/task_planner.py` — phase-based task decomposition
- `app/sandbox.py` — execution policy and restriction checks
- `app/tool_runner.py` — safe shell execution wrapper
- `app/verifier.py` — validation logic
- `app/editor.py` — file editing helpers
- `app/reviewer.py` — patch review pass
- `app/assistant.py` — orchestration loop
- `app/main.py` — FastAPI API
- `app/cli.py` — CLI entrypoint
- `tests/` — smoke tests for key modules

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set a real key if you want actual model calls:

```bash
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4o-mini
MODEL_API_KEY=your_key_here
```

If no API key is configured, the assistant falls back to local planning mode.

## Run the API

```bash
uvicorn app.main:app --reload
```

## Run the CLI

```bash
python -m app.cli "fix the auth token refresh bug"
```

## Example request

```bash
curl -X POST http://localhost:8000/task \
  -H "Content-Type: application/json" \
  -d '{"description":"Fix the token refresh bug in auth flow","repo_root":"."}'
```

## Production upgrades to add next

- vector-indexed semantic retrieval
- dependency graph and symbol graph
- Postgres persistence for tasks and memory
- worker queue for long-running operations
- stronger sandboxing / isolated execution service
- diff-aware validation and acceptance scoring
- reviewer and planner as separate agents

This is the correct architecture direction for a serious coding agent: a control loop around repo context, safe execution, verification, and memory.
