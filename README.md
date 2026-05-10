# HiveMind MD

HiveMind MD là hệ thống multi-agent local-first để biến một chủ đề thành knowledge base Markdown có thể hỏi đáp bằng RAG. Hệ thống ưu tiên chạy local với Ollama, SQLite và ChromaDB, không fine-tune và không training lại model.

## Kiến trúc

```txt
React Frontend
    ↓
FastAPI Backend
    ↓
Agent Orchestrator
    ↓
Search → Crawl → Clean → Extract → Critic → Compose → Index
    ↓
Markdown Knowledge Base + Vector Database
    ↓
Answer Agent qua Ollama
```

## Self-Improvement

HiveMind MD có module Self-Improvement Loop để ghi lại lịch sử agent runs, chấm điểm output, lưu lesson vào SQLite/Markdown, tạo prompt versions và workflow suggestions có kiểm soát. Module không fine-tune model, không tự sửa code production và không tự apply workflow changes.

Các trang frontend mới:

- Self Improvement
- Agent Runs
- Prompt Versions
- Improvement Lessons
- Workflow Suggestions

Biến môi trường:

```env
SELF_IMPROVEMENT_ENABLED=true
AUTO_SAVE_LESSONS=true
AUTO_SAVE_PROMPT_VERSIONS=true
ALLOW_AUTO_PROMPT_APPLY=false
ALLOW_AUTO_WORKFLOW_APPLY=false
ALLOW_AUTO_CODE_PATCH=false
REFLECTION_SCORE_THRESHOLD=42
```

Tắt toàn bộ phần đánh giá/reflection bằng `SELF_IMPROVEMENT_ENABLED=false`. Việc ghi `agent_runs` vẫn được giữ để có audit trail cơ bản.

Xem thêm: `docs/self-improvement.md`.

## Yêu cầu hệ thống

- Python 3.11+ cho backend local
- Node.js 20+
- Docker và Docker Compose nếu chạy container
- Ollama local nếu muốn LLM extraction, embedding và chat đầy đủ

## Cài Ollama và model

```bash
ollama pull qwen2.5:7b
ollama pull qwen2.5:3b
ollama pull nomic-embed-text
```

## Chạy backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pytest -q
uvicorn app.main:app --reload
```

Windows PowerShell:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
pytest -q
uvicorn app.main:app --reload
```

Backend mac dinh dung JSON vector fallback. Neu muon dung ChromaDB, nen chay Python 3.11-3.12 roi cai them:

```powershell
pip install -r requirements-chroma.txt
```

## Chạy frontend

```bash
cd frontend
npm install
npm run dev
```

Mở `http://localhost:5173`.

## Chạy bằng Docker Compose

```bash
docker compose up --build
```

Backend expose `8000`, frontend expose `5173`. Ollama không chạy trong compose; backend trong container gọi Ollama host qua `http://host.docker.internal:11434`.

## Ví dụ sử dụng

```bash
curl -X POST http://localhost:8000/api/agents/build-knowledge \
  -H "Content-Type: application/json" \
  -d '{"topic":"Local Multi Agent Architecture","mode":"quick","category":"ai-systems"}'
```

Sau khi build, file Markdown nằm trong `backend/knowledge/<category>/<slug>.md`, metadata nằm trong SQLite, chunk được index vào ChromaDB hoặc JSON fallback.

## Làm mới kiến thức

Backend có API làm mới tri thức để search internet, crawl nguồn, chia nhỏ nội dung thành nhiều Markdown shard và cập nhật map cho agent:

```bash
curl -X POST http://localhost:8000/api/knowledge/refresh \
  -H "Content-Type: application/json" \
  -d '{"topic":"tài chính","mode":"standard","category":"general"}'
```

Kết quả được lưu theo cây `backend/knowledge/<category>/<topic>/index.md` và `sources/*.md`. File `backend/knowledge/_knowledge_map.md` là bản đồ nhanh để agent chọn đúng thư mục hoặc shard trước khi đọc chi tiết.

## Khung tác nhân chuyên sâu

Khi một chủ đề cần xử lý theo chuyên môn riêng, dùng Agent Framework:

```bash
curl -X POST http://localhost:8000/api/agent-framework/run \
  -H "Content-Type: application/json" \
  -d '{"topic":"quản trị rủi ro tài chính","mode":"standard","category":"general","profile_id":"finance"}'
```

Framework chạy 3 công đoạn:

1. Planner/Router chọn profile chuyên môn và chia nguồn thành 4-5 lane.
2. Worker agents xử lý từng lane nhỏ: crawl, clean, extract, critique với giới hạn song song để giảm tải phần cứng.
3. Synthesis/Filter hợp nhất kết quả, loại nguồn yếu, ghi Markdown shard và cập nhật `_knowledge_map.md`.

Profile hiện có: `general`, `economy`, `finance`, `programming`, `ai`. Gọi `GET /api/agent-framework/profiles` để xem cấu hình.

## Roadmap

- Streaming log realtime qua WebSocket hoặc SSE.
- Parallel crawl có giới hạn concurrency.
- Import Markdown thủ công và re-index.
- Settings API để cập nhật cấu hình runtime từ UI.
- Playwright crawler cho trang động cần JavaScript.

## Cấu trúc thư mục

```txt
hivemind-md/
├── backend/
├── frontend/
├── docs/
├── docker-compose.yml
├── .env.example
└── README.md
```

## Contributing

Xem [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache-2.0. Xem [LICENSE](LICENSE).
