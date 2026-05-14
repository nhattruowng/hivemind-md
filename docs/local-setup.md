# Local Setup

## Python

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Node

```bash
cd frontend
npm install
npm run dev
```

## Ollama

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

## Docker

```bash
docker compose up --build
```

## Lỗi thường gặp

- **Ollama unavailable**: kiểm tra Ollama đang chạy và `OLLAMA_BASE_URL`.
- **Không crawl được nguồn**: website có thể chặn crawler; workflow sẽ bỏ qua nguồn lỗi.
- **ChromaDB lỗi cài đặt**: backend tự chuyển sang JSON fallback.
- **Frontend không gọi được API**: kiểm tra `VITE_API_BASE_URL` và CORS.
- **Pip build `pydantic-core` trên Windows/MSYS**: dùng Python CPython chính thức từ python.org hoặc chạy bằng Docker; MSYS Python có thể thiếu wheel phù hợp và yêu cầu MSVC linker.
