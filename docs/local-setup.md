# Setup Local Cho HiveMind MD

Tài liệu này dành cho phần HiveMind MD hiện có. Nếu cần setup BizFlow Java core và Desktop UI, xem thêm `docs/setup-run.md`.

## 1. Python Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Trên Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## 2. Node Frontend

```bash
cd frontend
npm install
npm run dev
```

## 3. Ollama

```bash
ollama pull qwen2.5:7b
ollama pull qwen2.5:3b
ollama pull nomic-embed-text
```

Kiểm tra:

```bash
curl http://localhost:11434/api/tags
curl http://localhost:8000/api/health/ollama
```

## 4. Docker

```bash
docker compose up --build
```

## 5. Lỗi Thường Gặp

| Lỗi | Cách xử lý |
|---|---|
| Ollama unavailable | kiểm tra Ollama đang chạy và `OLLAMA_BASE_URL` |
| Không crawl được nguồn | website có thể chặn crawler; workflow sẽ bỏ qua nguồn lỗi |
| ChromaDB lỗi cài đặt | backend tự chuyển sang JSON fallback |
| Frontend không gọi được API | kiểm tra `VITE_API_BASE_URL` và CORS |
| Pip build `pydantic-core` trên Windows/MSYS | dùng Python CPython chính thức từ python.org hoặc chạy bằng Docker |
