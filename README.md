# HiveMind MD + BizFlow Local Agent

HiveMind MD là một hệ thống quản lý tri thức Markdown chạy local-first, có AI copilot, RAG có citation và các workflow agentic lặp lại được. Repo này hiện cũng chứa scaffold cho **BizFlow Local Agent**: một nền tảng AI agent local-first hướng production với Agent Runtime, Memory Engine, Tool/Permission/Approval, Workflow Engine, Audit Log và Desktop UI prototype.

## 1. Mục Tiêu

| Mục tiêu | Mô tả |
|---|---|
| Local-first | Dữ liệu người dùng mặc định nằm trên máy local |
| Markdown-native | Tri thức vẫn đọc được bằng file Markdown bình thường |
| AI có citation | Câu trả lời phải truy ngược được về nguồn, file, chunk hoặc tool output |
| Secure by default | Hành động nguy hiểm phải qua permission và approval |
| Audit được | Agent, memory, tool, workflow và approval đều có trace/log |
| Mở rộng được | Có chỗ cho tools, workflows, connectors, model providers và plugins |

## 2. Thành Phần Trong Repo

| Khu vực | Đường dẫn | Vai trò |
|---|---|---|
| HiveMind backend | `backend/` | FastAPI backend hiện có: knowledge ingestion, vector search, agent orchestration, Ollama |
| HiveMind frontend | `frontend/` | React/Vite UI hiện có cho knowledge, chat, agent monitor |
| BizFlow Java core | `pom.xml`, `src/main/java/com/bizflow` | Spring Boot 3 WebFlux / Java 21 scaffold cho agent runtime, workflow, approval, permission, tool, audit |
| BizFlow migrations | `src/main/resources/db/migration` | Flyway SQLite schema cho Agent Runtime và Workflow Engine |
| BizFlow desktop UI | `apps/desktop` | React + TypeScript + Tailwind prototype, ưu tiên Workflow Builder |
| Tài liệu | `docs/` | Hướng dẫn setup/run, kiến trúc UI, Workflow Engine, roadmap |

## 3. Chạy Nhanh HiveMind MD Hiện Có

Yêu cầu:

- Python 3.11+
- Node.js 20+
- Ollama

Backend:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Ollama:

```powershell
ollama pull llama3.1
ollama pull nomic-embed-text
```

Docker, nếu muốn chạy nguyên stack:

```powershell
docker compose up --build
```

## 4. Chạy Nhanh BizFlow Java Core

Yêu cầu:

- Java 21
- Maven 3.9+

```powershell
$env:JAVA_HOME='C:\Program Files\Java\jdk-21'
mvn test
mvn spring-boot:run
```

BizFlow Java core dùng Spring WebFlux ở API layer. Persistence hiện vẫn dùng SQLite JDBC/JPA blocking và được bọc qua bounded elastic scheduler để không chiếm Netty event-loop.

Mặc định backend BizFlow dự kiến chạy tại:

```text
http://127.0.0.1:8787
```

SQLite database mặc định:

```text
./data/bizflow.db
```

Có thể override bằng biến môi trường:

```powershell
$env:BIZFLOW_DB_PATH='D:\bizflow-data\bizflow.db'
$env:BIZFLOW_PORT='8787'
mvn spring-boot:run
```

## 5. Chạy Nhanh BizFlow Desktop UI Prototype

```powershell
cd apps/desktop
npm install
npm run dev
```

Mặc định frontend chạy tại:

```text
http://127.0.0.1:5173
```

Nếu cần đổi API backend:

```powershell
$env:VITE_BIZFLOW_API_URL='http://127.0.0.1:8787'
npm run dev
```

## 6. Tài Liệu Chính

| Tài liệu | Nội dung |
|---|---|
| [docs/setup-run.md](docs/setup-run.md) | Hướng dẫn setup, run, test, troubleshoot |
| [docs/frontend-ui.md](docs/frontend-ui.md) | Thiết kế Desktop UI, component, route, state |
| [docs/workflow-engine.md](docs/workflow-engine.md) | Workflow Engine, DSL, approval, retry, rollback, replay |
| [docs/roadmap.md](docs/roadmap.md) | Roadmap triển khai theo phase |
| [docs/architecture.md](docs/architecture.md) | Kiến trúc HiveMind MD hiện có |
| [docs/api-spec.md](docs/api-spec.md) | API HiveMind MD hiện có |

## 7. Kiến Trúc Tổng Quan

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
Local model trước, cloud model chỉ dùng khi user bật
```

Agent Runtime định hướng:

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

Workflow Engine định hướng:

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

## 8. Cấu Trúc Thư Mục

```text
.
├── backend/                  # HiveMind FastAPI backend hiện có
├── frontend/                 # HiveMind React frontend hiện có
├── src/                      # BizFlow Java Spring Boot local core scaffold
├── apps/
│   └── desktop/              # BizFlow React desktop UI prototype
├── docs/                     # Tài liệu kiến trúc, setup, workflow, UI
├── docker-compose.yml
├── pom.xml                   # Build file cho BizFlow Java core
└── README.md
```

## 9. Lưu Ý Phát Triển

- Không phá module HiveMind MD hiện có khi thêm BizFlow.
- Module BizFlow phải nằm trong boundary rõ ràng: `src/main/java/com/bizflow` và `apps/desktop`.
- Không commit database local, vector index, secret, log, file memory cá nhân.
- Dữ liệu sensitive mặc định dùng local model; cloud model phải opt-in.
- Hành động write/delete/shell/network phải đi qua permission và approval.

## 10. License

Xem [LICENSE](LICENSE).
