# Agent Flow

## Build knowledge

```txt
User Topic
  ↓
SearchAgent: tạo keyword và tìm URL
  ↓
CrawlerAgent: crawl nội dung từng URL, bỏ qua nguồn lỗi
  ↓
CleanerAgent: chuẩn hóa raw text
  ↓
ExtractorAgent: rút trích summary, key points, concepts, risks
  ↓
CriticAgent: chấm trust score
  ↓
ComposerAgent: tạo Markdown và lưu metadata SQLite
  ↓
IndexerAgent: chunk Markdown, embed và lưu vector
```

Mode:

- `quick`: 3 nguồn
- `standard`: 5 nguồn
- `deep`: 10 nguồn

## Chat với knowledge

```txt
Question
  ↓
AnswerAgent
  ↓
Embed question
  ↓
Search vector store
  ↓
Retrieve related chunks
  ↓
Prompt Ollama với context
  ↓
Answer + related files + sources
```

Nếu không có chunk phù hợp, AnswerAgent trả lời rằng knowledge base chưa có đủ dữ liệu.

