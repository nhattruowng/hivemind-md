# Hướng Dẫn Setup Và Chạy Dự Án

Tài liệu này hướng dẫn cách cài đặt, chạy, test và xử lý lỗi cho repo `hivemind-md`, bao gồm HiveMind MD hiện có và scaffold BizFlow Local Agent.

## 1. Yêu Cầu Môi Trường

| Thành phần | Phiên bản khuyến nghị | Dùng cho |
|---|---:|---|
| Git | mới nhất | clone/push code |
| Python | 3.11+ | HiveMind backend FastAPI |
| Node.js | 20+ | HiveMind frontend và BizFlow desktop UI |
| npm | 10+ | cài package frontend |
| Java JDK | 21 | BizFlow Java core |
| Maven | 3.9+ | build/test/run BizFlow Java core |
| Ollama | mới nhất | local LLM và embedding |
| Docker | optional | chạy stack HiveMind bằng compose |

## 2. Clone Repo

```powershell
git clone https://github.com/nhattruowng/hivemind-md.git
cd hivemind-md
```

## 2.1. Chạy Một Lệnh Cho Toàn Bộ Dev Stack

Ở thư mục root repo, copy và dán:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev-all.ps1
```

Lệnh này tự xử lý Maven nếu máy chưa có `mvn`, tạo Python venv, cài BizFlow desktop UI dependencies, rồi chạy:

| Service | URL | Log |
|---|---|---|
| HiveMind FastAPI backend | `http://127.0.0.1:8000` | `logs/dev/hivemind-backend.log` |
| BizFlow Java backend | `http://127.0.0.1:8787` | `logs/dev/bizflow-backend.log` |
| BizFlow Desktop UI | `http://127.0.0.1:5173` | `logs/dev/frontend.log` |

Dừng tất cả:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\stop-all.ps1
```

Terminal chạy `dev-all.ps1` sẽ giữ mở để dev stack sống ổn định. Nếu muốn start xong và trả prompt ngay, dùng thêm `-NoWait`.

## 3. Chạy HiveMind MD Backend

Backend HiveMind dùng FastAPI, SQLite, vector store và Ollama.

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Kiểm tra health:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

Kiểm tra Ollama:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health/ollama
```

## 4. Chạy HiveMind MD Frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend thường chạy tại:

```text
http://127.0.0.1:5173
```

Nếu cần đổi backend API:

```powershell
$env:VITE_API_BASE_URL='http://127.0.0.1:8000'
npm run dev
```

## 5. Cài Và Chạy Ollama

Cài Ollama, sau đó pull model:

```powershell
ollama pull llama3.1
ollama pull nomic-embed-text
```

Kiểm tra model local:

```powershell
ollama list
Invoke-RestMethod http://127.0.0.1:11434/api/tags
```

## 6. Chạy HiveMind Bằng Docker

```powershell
docker compose up --build
```

Dùng Docker khi môi trường Python/Node local bị lệch version hoặc muốn chạy nhanh stack hiện có.

## 7. Chạy BizFlow Java Core

BizFlow Java core là Spring Boot 3 WebFlux app dùng Java 21, SQLite JDBC/JPA và Flyway migration. Do SQLite/JPA là blocking, API WebFlux bọc các call persistence qua `BlockingJpaBridge` để chạy trên bounded elastic scheduler.

```powershell
$env:JAVA_HOME='C:\Program Files\Java\jdk-21'
mvn test
mvn spring-boot:run
```

Backend BizFlow dự kiến chạy tại:

```text
http://127.0.0.1:8787
```

Smoke test cơ bản:

```powershell
Invoke-RestMethod http://127.0.0.1:8787/api/workflows
```

## 8. Cấu Hình BizFlow Java Core

File cấu hình:

```text
src/main/resources/application.yml
```

Các biến môi trường quan trọng:

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `BIZFLOW_DB_PATH` | `./data/bizflow.db` | đường dẫn SQLite DB local |
| `BIZFLOW_PORT` | `8787` | port backend BizFlow |

Ví dụ:

```powershell
$env:BIZFLOW_DB_PATH='D:\bizflow-data\bizflow.db'
$env:BIZFLOW_PORT='8787'
mvn spring-boot:run
```

## 9. Database Migration

Flyway chạy migration tự động khi BizFlow backend khởi động.

| Migration | Mục đích |
|---|---|
| `V1__agent_runtime_schema.sql` | agent run, tool, permission, approval, model call, audit |
| `V2__workflow_engine_schema.sql` | workflow, step, run, schedule, event, replay, retry, rollback |

Thư mục migration:

```text
src/main/resources/db/migration/
```

## 10. Chạy BizFlow Desktop UI Prototype

```powershell
cd apps/desktop
npm install
npm run dev
```

Frontend BizFlow mặc định chạy tại:

```text
http://127.0.0.1:5173
```

Đổi backend API:

```powershell
$env:VITE_BIZFLOW_API_URL='http://127.0.0.1:8787'
npm run dev
```

UI hiện ưu tiên Workflow Builder, Approval Inbox và Agent Studio skeleton.

## 11. Chạy Backend Và Frontend BizFlow Cùng Lúc

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

Mở:

```text
http://127.0.0.1:5173
```

## 12. Test

HiveMind backend:

```powershell
cd backend
pytest
```

HiveMind frontend:

```powershell
cd frontend
npm run build
```

BizFlow Java core:

```powershell
mvn test
```

BizFlow desktop UI:

```powershell
cd apps/desktop
npm run build
```

## 13. Trạng Thái Hiện Tại

| Khu vực | Trạng thái |
|---|---|
| HiveMind FastAPI backend | đã có sẵn |
| HiveMind React frontend | đã có sẵn |
| BizFlow Spring Boot scaffold | đã tạo |
| SQLite/Flyway schema cho Agent Runtime | đã tạo |
| SQLite/Flyway schema cho Workflow Engine | đã tạo |
| BizFlow desktop UI prototype | đã tạo |
| Tauri v2 shell | chưa scaffold |
| Memory Engine production API | chưa triển khai đầy đủ |
| Tool execution thật | còn stub ở một số flow |
| Model Router adapters | chưa hoàn thiện |
| Connector Manager | chưa triển khai |

## 14. Lỗi Thường Gặp

| Lỗi | Cách xử lý |
|---|---|
| `mvn` not found | cài Maven hoặc thêm Maven vào `PATH` |
| Java sai version | đặt `JAVA_HOME` về JDK 21 |
| SQLite DB locked | tắt process đang giữ DB rồi chạy lại |
| Frontend không gọi được backend | kiểm tra `VITE_API_BASE_URL` hoặc `VITE_BIZFLOW_API_URL` |
| Ollama unavailable | kiểm tra Ollama đang chạy và model đã pull |
| `npm install` lỗi | kiểm tra Node 20+, xoá cache npm nếu cần |
| Python dependency lỗi trên Windows | dùng Python CPython chính thức hoặc Docker |
