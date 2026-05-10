# Kiến trúc HiveMind MD

HiveMind MD dùng kiến trúc local-first: frontend React gọi FastAPI backend, backend điều phối các agent nhẹ để xây knowledge base Markdown, index vào vector database và trả lời bằng RAG qua Ollama.

## Thành phần

- **Frontend**: React, TypeScript, TailwindCSS, Vite. Gồm Dashboard, Builder, Agent Monitor, Explorer, Chat và Settings.
- **Backend**: FastAPI, Pydantic, SQLite. Cung cấp API health, build knowledge, knowledge CRUD và chat.
- **Agent Orchestrator**: chạy tuần tự các agent để giảm độ phức tạp ở MVP.
- **Markdown Knowledge Base**: lưu mỗi chủ đề thành một file `.md` trong `backend/knowledge/<category>/<slug>.md`.
- **Vector Database**: ưu tiên ChromaDB. Nếu ChromaDB không khả dụng, hệ thống dùng JSON vector fallback để vẫn chạy được MVP.
- **Ollama**: dùng cho generation và embedding. Nếu Ollama chưa sẵn sàng, workflow có fallback heuristic và luôn ghi rõ giới hạn.

## Luồng dữ liệu

```txt
User topic
  -> FastAPI
  -> OrchestratorAgent
  -> SearchAgent
  -> CrawlerAgent
  -> CleanerAgent
  -> ExtractorAgent
  -> CriticAgent
  -> ComposerAgent
  -> IndexerAgent
  -> Markdown + SQLite + Vector Store
```

