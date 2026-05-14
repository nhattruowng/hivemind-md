# API Spec

Base URL: `http://localhost:8000`

## Health

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

## Ollama Health

```http
GET /api/health/ollama
```

## Build Knowledge

```http
POST /api/agents/build-knowledge
```

Body:

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

Curl:

```bash
curl -X POST http://localhost:8000/api/agents/build-knowledge \
  -H "Content-Type: application/json" \
  -d '{"topic":"Local Multi Agent Architecture","mode":"quick","category":"ai-systems"}'
```

## List Knowledge

```http
GET /api/knowledge
```

## Read Knowledge

```http
GET /api/knowledge/read?file_path=ai-systems/local-multi-agent-architecture.md
```

## Delete Knowledge

```http
DELETE /api/knowledge/delete
```

Body:

```json
{
  "file_path": "ai-systems/local-multi-agent-architecture.md"
}
```

## Chat

```http
POST /api/chat
```

Body:

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

