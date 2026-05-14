# Setup and Run Guide

This guide explains how to set up, run, test, and troubleshoot the current BizFlow Local Agent scaffold.

## 1. Prerequisites

| Dependency | Version | Required for |
|---|---:|---|
| Java JDK | 21 | Backend |
| Maven | 3.9+ | Backend build/test/run |
| Node.js | 20+ | Frontend |
| npm | 10+ | Frontend dependency install |
| Git | latest stable | Source control |

## 2. Clone

```powershell
git clone https://github.com/nhattruowng/hivemind-md.git
cd hivemind-md
```

## 3. Backend Setup

The backend is a Spring Boot 3 application with SQLite JDBC and Flyway migrations.

```powershell
$env:JAVA_HOME='C:\Program Files\Java\jdk-21'
mvn test
mvn spring-boot:run
```

Expected backend URL:

```text
http://127.0.0.1:8787
```

Health endpoint is not implemented yet. Use the workflow list endpoint for a basic smoke test:

```powershell
Invoke-RestMethod http://127.0.0.1:8787/api/workflows
```

## 4. Backend Configuration

`src/main/resources/application.yml`:

```yaml
spring:
  datasource:
    url: jdbc:sqlite:${BIZFLOW_DB_PATH:./data/bizflow.db}

server:
  port: ${BIZFLOW_PORT:8787}
```

Override locally:

```powershell
$env:BIZFLOW_DB_PATH='D:\bizflow-data\bizflow.db'
$env:BIZFLOW_PORT='8787'
mvn spring-boot:run
```

## 5. Database Migrations

Migrations live in:

```text
src/main/resources/db/migration/
```

Current migrations:

| Migration | Purpose |
|---|---|
| `V1__agent_runtime_schema.sql` | Agent runtime, tools, permissions, approvals, model calls, audit |
| `V2__workflow_engine_schema.sql` | Workflow engine, runs, steps, schedules, events, replay, retry, rollback |

Flyway runs migrations automatically on backend startup.

## 6. Frontend Setup

```powershell
cd apps/desktop
npm install
npm run dev
```

Expected frontend URL:

```text
http://127.0.0.1:5173
```

The frontend currently opens the Workflow Builder by default.

## 7. Frontend Configuration

Set backend API URL:

```powershell
$env:VITE_BIZFLOW_API_URL='http://127.0.0.1:8787'
npm run dev
```

Default API URL in code:

```text
http://127.0.0.1:8787
```

## 8. Running Backend and Frontend Together

Terminal 1:

```powershell
$env:JAVA_HOME='C:\Program Files\Java\jdk-21'
mvn spring-boot:run
```

Terminal 2:

```powershell
cd apps/desktop
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

## 9. Testing

Backend:

```powershell
mvn test
```

Frontend:

```powershell
cd apps/desktop
npm run build
npm run test
```

## 10. Known Limitations

| Area | Current status |
|---|---|
| Tauri v2 shell | Not scaffolded yet |
| Tool Router execution | Stubbed in Workflow `StepExecutor` |
| Memory Engine API | Designed previously, not implemented in this scaffold |
| Model Router | Config present, adapters not implemented |
| Connector Manager | Designed previously, not implemented in this scaffold |
| Maven wrapper | Not included yet |
| CI | Not included yet |

## 11. Troubleshooting

| Problem | Fix |
|---|---|
| `mvn` not found | Install Maven or add Maven wrapper |
| Java version mismatch | Set `JAVA_HOME` to JDK 21 |
| SQLite DB locked | Stop running app, remove stale process, retry |
| Frontend cannot call backend | Check `VITE_BIZFLOW_API_URL` and backend port |
| `npm install` fails | Ensure Node 20+ and clean npm cache |

