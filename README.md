# HiveMind MD

HiveMind MD is an open-source, local-first Markdown knowledge manager with an AI copilot. It combines a personal knowledge base, citation-aware RAG, and iterative agentic workflows.

This repository now also includes the **BizFlow Local Agent** scaffold: a production-oriented local-first AI agent architecture with Agent Runtime, Memory Engine, Tool/Permission/Approval systems, Workflow Engine, Audit Log, and a desktop UI prototype.

## BizFlow Local Agent Scaffold

BizFlow is being developed in this repository as a parallel local-first AI agent foundation. The scaffold is intentionally modular so the existing HiveMind MD application can continue to evolve while BizFlow modules are implemented and tested independently.

| Area | Location | Purpose |
|---|---|---|
| Java local core | `pom.xml`, `src/main/java/com/bizflow` | Spring Boot 3 / Java 21 backend skeleton for agent runtime, workflow, approvals, permissions, tools, audit, and model routing |
| Database migrations | `src/main/resources/db/migration` | Flyway SQLite migrations for agent runtime and workflow engine tables |
| Desktop UI prototype | `apps/desktop` | React + TypeScript + Tailwind UI scaffold with Workflow Builder-first structure |
| Workflow docs | `docs/workflow-engine.md` | Workflow Engine design, DSL, API, status model, rollback/replay concepts |
| Frontend docs | `docs/frontend-ui.md` | Desktop UI architecture, routes, state, components, and implementation notes |
| Setup docs | `docs/setup-run.md` | Detailed setup and run instructions for both existing HiveMind and BizFlow scaffold |
| Roadmap | `docs/roadmap.md` | Phased implementation plan |

### Run BizFlow Java Core

Requirements:

- Java 21
- Maven 3.9+

```powershell
$env:JAVA_HOME='C:\Program Files\Java\jdk-21'
mvn test
mvn spring-boot:run
```

The Java core uses SQLite JDBC and Flyway migrations. By default it is prepared for local development and can be connected later to the Tauri desktop shell.

### Run BizFlow Desktop UI Prototype

Requirements:

- Node.js 20+
- npm

```powershell
cd apps/desktop
npm install
npm run dev
```

The desktop UI prototype is currently a Vite/React app. Tauri v2 shell integration is planned as the next packaging step.

### BizFlow Documentation

Start here:

- [Detailed setup and run guide](docs/setup-run.md)
- [Frontend UI design and implementation notes](docs/frontend-ui.md)
- [Workflow Engine design](docs/workflow-engine.md)
- [Implementation roadmap](docs/roadmap.md)

## Architecture

HiveMind MD is split into:

- `backend/`: FastAPI backend, knowledge ingestion, vector search, agent orchestration, and local Ollama integration.
- `frontend/`: React/Vite frontend for Markdown authoring, graph views, semantic search, and assistant interactions.
- `docs/`: Architecture and product documentation.
- `src/`: BizFlow Java local core scaffold.
- `apps/desktop/`: BizFlow desktop UI prototype.

High-level flow:

```text
User
  ↓
Frontend / Desktop UI
  ↓
Local API
  ↓
Knowledge / Memory / Agent / Workflow modules
  ↓
SQLite + vector store + local files
  ↓
Local model first, cloud model optional when enabled
```

## Core Principles

| Principle | Implementation direction |
|---|---|
| Local-first | User data stays on the local machine by default |
| Markdown-native | Notes remain readable and portable |
| Citation-aware AI | Answers should trace back to source notes, files, chunks, or tool outputs |
| Secure by default | Dangerous actions require permission and approval |
| Auditable | Agent, memory, tool, workflow, and approval activity should be traceable |
| Extensible | Tools, workflows, connectors, and model providers are designed as modular capabilities |

## Existing HiveMind MD Setup

### Requirements

- Python 3.11+
- Node.js 20+
- Ollama for local LLM execution

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

### Ollama

Install Ollama and pull a local model:

```powershell
ollama pull llama3.1
ollama pull nomic-embed-text
```

## Docker

If Docker is available, the existing HiveMind stack can be started with:

```powershell
docker compose up --build
```

## Knowledge Refresh

HiveMind supports local knowledge ingestion and semantic retrieval. Source documents and generated indexes are kept out of Git by default:

- `backend/knowledge/`
- `backend/vector_store/`
- local SQLite files

## Agent and Workflow Direction

BizFlow extends the repository with a stricter agent architecture:

```text
AgentOrchestrator
  ↓
Intent Router
  ↓
Context Builder
  ↓
Planner
  ↓
Permission / Approval Gate
  ↓
Executor
  ↓
Verifier
  ↓
Response Composer
  ↓
Audit Log
```

Workflow execution follows:

```text
Workflow Definition
  ↓
Workflow Runner
  ↓
Step Executor
  ↓
Tool / Agent / Memory / Model Step
  ↓
Retry / Approval / Rollback
  ↓
Timeline + Replay Debug
```

## Repository Layout

```text
.
├── backend/                  # Existing HiveMind FastAPI backend
├── frontend/                 # Existing HiveMind React frontend
├── src/                      # BizFlow Java Spring Boot local core scaffold
├── apps/
│   └── desktop/              # BizFlow React desktop UI prototype
├── docs/                     # Architecture, setup, workflow, UI docs
├── docker-compose.yml
├── pom.xml                   # BizFlow Java core build
└── README.md
```

## Development Notes

- Keep existing HiveMind MD modules intact.
- Add BizFlow modules behind clear package/folder boundaries.
- Never commit local memory databases, vector indexes, secrets, generated logs, or user data.
- Prefer local models for sensitive data. Cloud model routing must remain opt-in.

## License

See [LICENSE](LICENSE).
