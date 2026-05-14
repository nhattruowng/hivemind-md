# Roadmap BizFlow Local Agent

Roadmap này ưu tiên xây được sản phẩm thật, local-first, có kiểm soát hành động nguy hiểm và có audit đầy đủ.

## Phase 1: Nền Tảng Dự Án

| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| Spring Boot backend scaffold | xong | Java 21, Spring Boot 3 |
| SQLite/Flyway setup | xong | migration trong `src/main/resources/db/migration` |
| Schema Agent/Tool/Approval/Audit | xong | migration `V1` |
| Schema Workflow cơ bản | xong | migration `V2` |
| React desktop UI scaffold | xong | trong `apps/desktop` |
| Workflow Builder skeleton | xong | React Flow |

Tiêu chí hoàn tất:

- Repo build được theo module.
- Có tài liệu setup/run.
- Không phá code HiveMind hiện có.

## Phase 2: Workflow Engine Hardening

| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| StepExecutor gọi Tool Router thật | todo | thay stub hiện tại |
| Permission check trong workflow | todo | mọi write/delete/shell/network phải check |
| Approval expiry/retry handling | todo | expired phải pause/fail theo policy |
| Run context interpolation | todo | `{{input.file_path}}`, output mapping |
| Condition/loop evaluator | todo | điều kiện an toàn, không eval code tuỳ tiện |
| Workflow integration tests | todo | create/run/pause/resume/replay |

Tiêu chí hoàn tất:

- Workflow manual chạy end-to-end.
- Hành động nguy hiểm dừng ở Approval Inbox.
- Timeline có input/output đã redact.

## Phase 3: Memory Engine

| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| Memory schema production | todo | source trace, version, confidence |
| File ingestion | todo | txt/md/pdf/docx |
| Semantic/keyword/hybrid search | todo | vector DB local |
| Source trace UI | todo | file path, hash, page/line/chunk |
| Confidence/versioning | todo | update tạo version mới |
| Sensitive data policy | todo | local-only, redact, forget |

Tiêu chí hoàn tất:

- Ingest file tạo memory có source trace.
- Search trả citation đúng.
- Soft delete/hard delete hoạt động.

## Phase 4: Agent Runtime

| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| Intent Router | todo | phân loại chat/search/tool/workflow |
| Context Builder | todo | lấy memory/context theo permission |
| Planner/Executor/Verifier | todo | tách vai trò rõ |
| Model Router integration | todo | local first, cloud opt-in |
| Trace viewer | todo | span theo agent run |

Tiêu chí hoàn tất:

- Agent trả response có trace.
- Tool call luôn qua permission.
- Verifier chặn output/action rủi ro.

## Phase 5: Desktop Release

| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| Tauri v2 shell | todo | native desktop |
| Native file commands | todo | scope theo permission |
| Packaging/signing | todo | Windows/macOS/Linux |
| Auto-update | todo | Tauri updater hoặc manual |
| Backup/restore | todo | backup encrypted |

Tiêu chí hoàn tất:

- Có installer.
- Update không làm mất dữ liệu user.
- Log/crash report local có thể export.

## Ưu Tiên Ngắn Hạn

1. Hoàn thiện Workflow Builder save/run với backend.
2. Thêm approval flow thật cho write/delete/shell.
3. Thêm Memory Engine schema và ingestion tối thiểu.
4. Nối Agent Runtime với memory search và tool call.
5. Tạo bộ e2e demo: ingest file -> hỏi agent -> tạo workflow -> approval -> audit.
