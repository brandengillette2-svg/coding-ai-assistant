# Master Code Wizard - Production Architecture

A serious, scalable coding agent built for real-world deployment.

## Architecture overview

The system is organized as a distributed service with these components:

- **API Gateway** (FastAPI): Task ingestion, status queries, result retrieval
- **Orchestrator**: Task state machine, step coordination
- **Repo Scanner**: AST-based code indexing and semantic embedding
- **Planner Service**: LLM-driven task decomposition
- **Coder Service**: Patch generation and file editing
- **Verifier Service**: Test execution and validation
- **Reviewer Service**: Patch critique and acceptance scoring
- **Memory Store**: Postgres + vector DB for semantic retrieval
- **Task Queue**: Redis for job distribution
- **Worker Pool**: Processes tasks asynchronously
- **Journal**: Execution traces and audit log

## Quick start with Docker

```bash
# Build and start all services
docker-compose up --build

# Run a task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Fix the auth token refresh bug",
    "repo_url": "https://github.com/your-org/your-repo",
    "branch": "main"
  }'

# Check task status
curl http://localhost:8000/tasks/{task_id}

# View logs
docker-compose logs -f worker
```

## Services

### API (port 8000)

REST API for task management and status queries.

Endpoints:
- `POST /tasks` - create a new task
- `GET /tasks/{id}` - get task status and results
- `GET /tasks` - list recent tasks
- `POST /tasks/{id}/cancel` - cancel a task
- `GET /health` - health check

### Worker (processes Redis tasks)

Asynchronous task processor. Runs multiple workers for parallelism.

Responsibilities:
- fetch tasks from queue
- execute planner, coder, verifier, reviewer
- update task status and results
- store execution traces

### Postgres (port 5432)

Persistent storage for:
- task metadata
- execution history
- correction memory
- journal entries
- code index metadata

### Redis (port 6379)

Task queue and cache layer for:
- task scheduling
- worker coordination
- result caching

## Project structure

```
.
├── docker-compose.yml              # Service orchestration
├── Dockerfile                      # Worker and API image
├── .dockerignore
├── requirements.txt
├── .env.example
├── app/
│   ├── __init__.py
│   ├── config.py                   # Settings and env vars
│   ├── models.py                   # DTOs and enums
│   ├── model_client.py             # LLM integration
│   ├── repo_mapper.py              # Repo scanning and indexing
│   ├── context_library.py          # Memory retrieval
│   ├── journal.py                  # Execution logging
│   ├── task_planner.py             # Task decomposition
│   ├── sandbox.py                  # Execution policy
│   ├── tool_runner.py              # Safe command execution
│   ├── verifier.py                 # Validation logic
│   ├── editor.py                   # File editing
│   ├── reviewer.py                 # Patch review
│   ├── assistant.py                # Orchestration loop
│   ├── db.py                       # Postgres models and session
│   ├── storage.py                  # Data layer
│   ├── queue.py                    # Redis task queue
│   ├── main.py                     # FastAPI app
│   ├── cli.py                      # CLI entrypoint
│   ├── worker.py                   # Task worker
│   └── semantic_index.py           # Vector store integration
├── services/
│   ├── __init__.py
│   ├── planner_service.py          # Planner microservice
│   ├── coder_service.py            # Coder microservice
│   ├── verifier_service.py         # Verifier microservice
│   ├── reviewer_service.py         # Reviewer microservice
│   └── repo_service.py             # Repo indexing service
├── migrations/
│   ├── __init__.py
│   └── versions/
│       ├── 001_initial_schema.py
│       └── 002_add_embeddings.py
├── tests/
│   ├── test_repo_mapper.py
│   ├── test_verifier.py
│   ├── test_planner.py
│   ├── test_context_library.py
│   └── conftest.py                 # Test fixtures
├── docker/
│   ├── Dockerfile.worker
│   ├── Dockerfile.api
│   └── entrypoint.sh
└── README.md
```

## Environment configuration

See `.env.example` for all options.

Key variables:
- `POSTGRES_URL`: Postgres connection string
- `REDIS_URL`: Redis connection string
- `MODEL_API_KEY`: LLM provider key
- `MODEL_PROVIDER`: openai or anthropic
- `REPO_ROOT`: Default repo to scan

## Deployment

For production, configure:
- Postgres with SSL
- Redis with authentication
- Load balancer for API
- Monitoring and alerting
- Log aggregation

## Next steps

- Add semantic search over repo code
- Implement patch diff validation
- Build web dashboard
- Add GitHub/GitLab integration
- Set up monitoring with Prometheus

