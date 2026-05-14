# Đặc Tả API HiveMind MD

Base URL mặc định:

```text
http://localhost:8000
```

## 1. Health

```http
GET /api/health
```

Response:

```json
{
  "status": "ok",
  "service": "HiveMind MD Backend"
}
```

## 2. Kiểm Tra Ollama

```http
GET /api/health/ollama
```

Response phụ thuộc trạng thái Ollama local. Nếu Ollama chưa chạy, API trả lỗi hoặc status không sẵn sàng.

## 3. Build Knowledge

```http
POST /api/agents/build-knowledge
```

Request:

```json
{
  "topic": "Local Multi Agent Architecture",
  "mode": "quick",
  "category": "ai-systems"
}
```

Response:

```json
{
  "status": "success",
  "markdown_file": "ai-systems/local-multi-agent-architecture.md",
  "agent_logs": []
}
```

Ví dụ curl:

```bash
curl -X POST http://localhost:8000/api/agents/build-knowledge \
  -H "Content-Type: application/json" \
  -d '{"topic":"Local Multi Agent Architecture","mode":"quick","category":"ai-systems"}'
```

## 4. Danh Sách Knowledge

```http
GET /api/knowledge
```

Trả về danh sách file knowledge đã build.

## 5. Đọc Knowledge

```http
GET /api/knowledge/read?file_path=ai-systems/local-multi-agent-architecture.md
```

Trả về nội dung Markdown và metadata liên quan.

## 6. Xoá Knowledge

```http
DELETE /api/knowledge/delete
```

Request:

```json
{
  "file_path": "ai-systems/local-multi-agent-architecture.md"
}
```

## 7. Chat

```http
POST /api/chat
```

Request:

```json
{
  "message": "Hệ thống này dùng agent nào?"
}
```

Response:

```json
{
  "answer": "string",
  "related_files": [],
  "sources": []
}
```

## 8. Ghi Chú

- API này là của HiveMind MD backend hiện có.
- BizFlow Java core có API riêng cho workflow/agent/approval trong `src/main/java/com/bizflow`.
- Khi tích hợp hai hướng, cần chuẩn hoá response envelope, error code và audit trace.
