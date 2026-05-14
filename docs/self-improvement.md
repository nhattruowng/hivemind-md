# Self-Improvement Loop

Self-Improvement Loop giúp HiveMind MD ghi lại mỗi lần agent chạy, tự đánh giá kết quả, rút ra bài học tái sử dụng và đề xuất cải tiến prompt hoặc workflow theo cơ chế kiểm soát an toàn.

## Kiến trúc

```txt
Agent Workflow
  -> agent_runs + agent_scoreboard
  -> Evaluator Agent
  -> Reflection Agent -> SQLite + Markdown memory
  -> Prompt Optimizer Agent -> prompt_versions
  -> Workflow Optimizer Agent -> workflow_suggestions
```

Module này vẫn giữ hướng local-first: dữ liệu nằm trong SQLite và Markdown dưới `backend/knowledge/self-improvement/`. Ollama được dùng khi có sẵn; nếu Ollama lỗi hoặc trả JSON không hợp lệ, backend dùng fallback rule-based.

## Các Agent Mới

- `EvaluatorAgent`: chấm output theo thang 0-60, trả strengths, weaknesses, missing parts, hallucination risk và improvement suggestions.
- `ReflectionAgent`: tạo lesson khi score thấp hơn threshold hoặc evaluator yêu cầu reflect.
- `PromptOptimizerAgent`: tạo prompt version mới, mặc định inactive.
- `WorkflowOptimizerAgent`: tạo workflow suggestion dạng pending.

## Database Schema

Các bảng mới:

- `agent_runs`: lịch sử mỗi lần agent chạy.
- `improvement_lessons`: bài học được lưu vào SQLite.
- `prompt_versions`: nhiều phiên bản prompt theo agent.
- `workflow_suggestions`: đề xuất workflow chờ duyệt.
- `agent_scoreboard`: tổng hợp total runs, success/fail, score và runtime trung bình.

Nếu dự án chưa có migration system, `app.database.init_db()` tự tạo bảng khi backend startup.

## Safety Policy

Mặc định:

- Tự ghi agent run: có.
- Tự lưu lesson: có.
- Tự lưu prompt version: có.
- Tự active prompt mới: không.
- Tự lưu workflow suggestion: có.
- Tự apply workflow suggestion: không.
- Tự sửa code production: không.
- Tự fine-tune model: không.

Các biến môi trường:

```env
SELF_IMPROVEMENT_ENABLED=true
AUTO_SAVE_LESSONS=true
AUTO_SAVE_PROMPT_VERSIONS=true
ALLOW_AUTO_PROMPT_APPLY=false
ALLOW_AUTO_WORKFLOW_APPLY=false
ALLOW_AUTO_CODE_PATCH=false
REFLECTION_SCORE_THRESHOLD=42
```

## API Endpoints

- `GET /api/self-improvement/summary`
- `GET /api/self-improvement/runs`
- `GET /api/self-improvement/lessons`
- `POST /api/self-improvement/lessons/{lesson_id}/archive`
- `GET /api/self-improvement/prompt-versions`
- `POST /api/self-improvement/prompt-versions/{version_id}/activate`
- `GET /api/self-improvement/workflow-suggestions`
- `POST /api/self-improvement/workflow-suggestions/{suggestion_id}/reject`
- `POST /api/self-improvement/workflow-suggestions/{suggestion_id}/apply`

`apply` với workflow suggestion chỉ đánh dấu trạng thái `applied`; MVP không tự sửa workflow thật.

## Dashboard

Frontend có các trang:

- Self Improvement: summary, top agents, failures, latest lessons.
- Agent Runs: bảng lịch sử chạy agent, filter theo agent/status.
- Prompt Versions: xem prompt version và active thủ công.
- Improvement Lessons: xem/archive lesson.
- Workflow Suggestions: mark applied hoặc reject suggestion.

## Giới Hạn Hiện Tại

- Self-improvement chạy trong cùng request ở MVP nên có thể làm request build lâu hơn nếu Ollama phản hồi chậm.
- Prompt version active mới được lưu trong DB; agent production chưa tự đọc active prompt để thay hành vi.
- Workflow suggestion chỉ là đề xuất quản trị, không tự thay đổi code hoặc thứ tự agent.
- Markdown lesson append đơn giản, chưa có đồng bộ ngược khi archive.

## Vì Sao Không Fine-Tune

HiveMind MD ưu tiên local-first, dễ kiểm soát và an toàn vận hành. Fine-tune làm tăng chi phí, tạo state khó audit và dễ dẫn tới thay đổi hành vi không rõ nguồn gốc. Module này chỉ dùng memory, evaluation và prompt/workflow suggestions để cải thiện có kiểm soát.

## Roadmap

- Worker nền cho self-improvement để không chặn request build.
- UI so sánh prompt versions side-by-side.
- Cơ chế agent đọc active prompt theo chính sách.
- Rule engine để gom lỗi lặp lại thành pattern.
- Review queue cho patch/diff code nếu sau này bật suggestion code.
