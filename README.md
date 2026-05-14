# BizFlow Local Agent

BizFlow Local Agent is a local-first AI agent architecture prototype for desktop productivity, memory, tool execution, workflow automation, approval gates, and auditability.

This repository currently contains:

- Java 21 + Spring Boot 3 local core skeleton.
- SQLite/Flyway migrations for Agent Runtime, Tool/Approval/Audit, and Workflow Engine.
- Workflow Engine service/controller/entity/repository skeleton.
- React + TypeScript frontend skeleton under `apps/desktop`.
- Dark-mode Workflow Builder UI using React Flow.
- Approval Inbox and Agent Studio skeletons.
- Architecture and implementation docs.

> Current status: this is an implementation scaffold, not a production release. The Tauri shell is planned but not yet scaffolded as `src-tauri`.

## Repository Structure

```text
.
├─ pom.xml
├─ src/
│  ├─ main/java/com/bizflow/
│  │  ├─ agent_runtime/
│  │  ├─ approvals/
│  │  ├─ audit/
│  │  ├─ common/
│  │  ├─ models/
│  │  ├─ permissions/
│  │  ├─ tools/
│  │  └─ workflow/
│  ├─ main/resources/
│  │  ├─ application.yml
│  │  └─ db/migration/
│  └─ test/java/com/bizflow/
├─ apps/
│  └─ desktop/
│     ├─ package.json
│     ├─ vite.config.ts
│     ├─ tailwind.config.ts
│     └─ src/
└─ docs/
```

## Main Modules

| Module | Purpose |
|---|---|
| `agent_runtime` | Agent run/step/trace persistence skeleton |
| `tools` | Tool definitions, permissions, call logs |
| `permissions` | Permission policy persistence |
| `approvals` | Approval request persistence/service |
| `audit` | Audit log persistence |
| `workflow` | Workflow definition, run, step, scheduler, replay, rollback skeleton |
| `apps/desktop` | React UI shell, Workflow Builder, Approval Inbox, Agent Studio skeleton |

## Prerequisites

| Tool | Recommended version | Notes |
|---|---:|---|
| Java | 21 | Required for Spring Boot backend |
| Maven | 3.9+ | Not included yet as Maven wrapper |
| Node.js | 20+ | Required for frontend |
| npm | 10+ | Used by `apps/desktop/package.json` |
| SQLite | bundled through JDBC | Runtime DB is created locally |
| Ollama | optional | Future model-router integration |

## Backend Setup

From the repository root:

```powershell
$env:JAVA_HOME='C:\Program Files\Java\jdk-21'
mvn test
mvn spring-boot:run
```

Default backend URL:

```text
http://127.0.0.1:8787
```

Default SQLite DB path:

```text
./data/bizflow.db
```

Override with:

```powershell
$env:BIZFLOW_DB_PATH='D:\bizflow-data\bizflow.db'
$env:BIZFLOW_PORT='8787'
mvn spring-boot:run
```

## Frontend Setup

From `apps/desktop`:

```powershell
npm install
npm run dev
```

Frontend dev URL:

```text
http://127.0.0.1:5173
```

If the backend runs on a different URL:

```powershell
$env:VITE_BIZFLOW_API_URL='http://127.0.0.1:8787'
npm run dev
```

## Frontend Build

```powershell
cd apps/desktop
npm run build
```

## Current API Surface

Workflow APIs currently scaffolded:

```text
POST   /api/workflows
GET    /api/workflows
GET    /api/workflows/{workflowId}
PUT    /api/workflows/{workflowId}
DELETE /api/workflows/{workflowId}
POST   /api/workflows/{workflowId}/activate
POST   /api/workflows/{workflowId}/pause
POST   /api/workflows/{workflowId}/clone
GET    /api/workflows/{workflowId}/versions

POST   /api/workflows/{workflowId}/run
GET    /api/workflows/runs/{runId}
GET    /api/workflows/runs/{runId}/timeline
POST   /api/workflows/runs/{runId}/pause
POST   /api/workflows/runs/{runId}/resume
POST   /api/workflows/runs/{runId}/cancel
POST   /api/workflows/runs/{runId}/retry
POST   /api/workflows/runs/{runId}/rollback

GET    /api/approvals
GET    /api/approvals/{approvalId}
POST   /api/approvals/{approvalId}/approve
POST   /api/approvals/{approvalId}/reject
POST   /api/approvals/{approvalId}/modify-and-approve
```

## Important Docs

- [Workflow Engine](docs/workflow-engine.md)
- [Setup and Run Guide](docs/setup-run.md)
- [Frontend UI Guide](docs/frontend-ui.md)
- [Project Roadmap](docs/roadmap.md)

## Verification Notes

This workspace did not have Maven in `PATH` during generation, so backend tests were not executed locally here. Frontend dependencies were not installed yet, so frontend build was not executed either. The repository includes the commands needed to verify once Maven and npm dependencies are available.

## Next Engineering Tasks

1. Add Maven wrapper: `mvn -N wrapper:wrapper`.
2. Add Tauri v2 `src-tauri` shell under `apps/desktop`.
3. Wire Workflow `StepExecutor` to real Tool Router and Permission Engine.
4. Implement Memory Engine APIs and UI pages.
5. Implement Model Router adapters for Ollama/llama.cpp.
6. Add integration tests with temporary SQLite DB.
7. Add GitHub Actions CI for backend and frontend.
