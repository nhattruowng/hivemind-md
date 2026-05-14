# BizFlow Local Agent - Workflow Engine

Tài liệu này mô tả thiết kế và scaffold triển khai Workflow Engine cho BizFlow Local Agent. Mục tiêu là chạy automation local-first, có trạng thái rõ ràng, approval gate, retry, pause/resume, rollback, replay/debug và audit timeline đầy đủ.

## 1. Mục Tiêu

| Mục tiêu | Yêu cầu triển khai |
|---|---|
| Tạo workflow từ UI | Workflow Builder sinh JSON DSL |
| Tạo workflow từ agent | Agent tạo draft, user phải duyệt trước khi lưu/chạy |
| Chạy thủ công | User bấm Run |
| Chạy theo lịch | Scheduler local tính `next_run_at` |
| Chạy theo event | Connector phát event, engine match binding |
| Step có input/output rõ | Mỗi step lưu input/output redacted |
| Tool/agent/model/memory step | StepExecutor điều phối theo `type` |
| Approval step | Workflow dừng ở `waiting_approval` |
| Retry/timeout | RetryPolicyEngine quyết định retry/backoff |
| Pause/resume/cancel | WorkflowRunner quản lý state transition |
| Rollback | Compensation action nếu step hỗ trợ |
| Replay/debug | Tạo run mới, không ghi đè run cũ |
| Audit | Mọi event quan trọng ghi vào timeline |

## 2. Kiến Trúc Module

| Module | Trách nhiệm | Input | Output | Bảng liên quan | API | Rủi ro | Cách xử lý |
|---|---|---|---|---|---|---|---|
| WorkflowService | tạo/sửa/xoá/activate/clone/version workflow | Workflow JSON | workflow definition | `workflows`, `workflow_versions`, `workflow_steps`, `workflow_triggers` | `/api/workflows` | DSL invalid | validate trước khi lưu |
| WorkflowRunner | tạo run, chạy step, pause/resume/cancel | workflow id, input | run state | `workflow_runs`, `workflow_step_runs` | `/api/workflows/{id}/run` | state sai | status transition rõ |
| StepExecutor | chạy tool/agent/condition/loop/approval/delay/notification/transform/memory/model | step config | step output | `workflow_step_runs` | internal | hành động nguy hiểm | permission + approval |
| ApprovalService | tạo approval, approve/reject/modify | pending action | decision | `approval_requests` | `/api/approvals` | bypass approval | mọi high/critical dừng run |
| RetryPolicyEngine | quyết định retry/backoff | attempt, error | retry/delay/fail | `retry_policies` | internal | duplicate side effect | idempotency key |
| RollbackManager | chạy compensation | failed/completed run | rollback status | `rollback_actions` | `/rollback` | action không rollback được | audit warning |
| WorkflowScheduler | trigger workflow theo lịch | schedule | due runs | `workflow_schedules` | `/schedule` | chạy trùng | lock/idempotency |
| EventTriggerManager | match connector event với workflow | event payload | workflow run | `workflow_event_bindings` | `/event-binding` | event spam | scope + debounce |
| WorkflowAuditService | ghi timeline đã redact | event | audit row | `workflow_audit_events` | `/timeline` | log secret | redaction |
| WorkflowReplayService | replay từ step | parent run, step | replay run mới | `workflow_replay_runs` | `/replay` | lặp action nguy hiểm | approval mới bắt buộc |

## 3. Loại Workflow

| Loại | Trigger | Use case | Input | Output | Risk | Approval rule |
|---|---|---|---|---|---|---|
| Manual | user bấm Run | tóm tắt file PDF | `file_path` | note/report | medium | step ghi file/note cần approval |
| Scheduled | cron tick | báo cáo hằng ngày | schedule context | daily report | medium | cần user duyệt workflow trước khi active |
| Event-based | connector event | ingest file mới | event payload | memory nodes | medium-high | folder scope bắt buộc |
| Agent-generated | agent đề xuất | tự động hoá task lặp lại | chat-derived DSL | draft workflow | high | user phải approve trước khi save/run |

## 4. Flow Thực Thi

### Manual Workflow

```text
User Click Run
  ↓
WorkflowService validate workflow
  ↓
WorkflowRunner create run
  ↓
Load workflow steps
  ↓
Execute step by step
  ↓
If approval required -> ApprovalService
  ↓
If error -> RetryPolicyEngine
  ↓
If failed -> mark failed
  ↓
If success -> mark completed
  ↓
Audit timeline
  ↓
Return result
```

### Scheduled Workflow

```text
Scheduler Tick
  ↓
Find active workflows with schedule
  ↓
Check next_run_at
  ↓
Create workflow run
  ↓
Execute workflow
  ↓
Update next_run_at
  ↓
Audit
```

### Event-based Workflow

```text
Connector emits event
  ↓
EventTriggerManager receives event
  ↓
Match event condition
  ↓
Create workflow run with event payload
  ↓
Execute workflow
  ↓
Audit
```

### Approval Step

```text
Step requires approval
  ↓
Create approval request
  ↓
Workflow run status = waiting_approval
  ↓
User approve / reject / modify
  ↓
If approve -> continue
  ↓
If reject -> stop or skip by policy
  ↓
Audit decision
```

### Replay / Debug

```text
User opens failed run
  ↓
View step timeline
  ↓
Select failed step
  ↓
Inspect input / output / error
  ↓
Choose replay from this step
  ↓
Create replay run
  ↓
Reuse previous safe context
  ↓
Execute from selected step
  ↓
Require new approval for dangerous actions
  ↓
Audit replay
```

## 5. Thiết Kế Workflow DSL JSON

Workflow definition phải có schema ổn định để UI Builder, Agent Runtime và backend cùng hiểu.

```json
{
  "id": "wf_pdf_summary",
  "name": "Tóm tắt PDF",
  "description": "Đọc file PDF, tóm tắt và tạo note.",
  "version": 1,
  "status": "draft",
  "trigger": {
    "type": "manual"
  },
  "input_schema": {
    "type": "object",
    "required": ["file_path"],
    "properties": {
      "file_path": {
        "type": "string"
      }
    }
  },
  "output_schema": {
    "type": "object"
  },
  "variables": {},
  "steps": [
    {
      "id": "read_file",
      "name": "Đọc file",
      "type": "tool_call",
      "description": "Đọc nội dung file local",
      "input": {
        "tool_name": "read_local_file",
        "path": "{{input.file_path}}"
      },
      "output_mapping": {
        "file_content": "$.content"
      },
      "depends_on": [],
      "condition": {},
      "retry_policy": {
        "max_attempts": 2,
        "backoff_strategy": "fixed"
      },
      "timeout_ms": 30000,
      "requires_approval": false,
      "risk_level": "low",
      "permission_level": "read_only",
      "compensation": {},
      "on_success": {},
      "on_failure": {
        "policy": "fail_fast"
      },
      "metadata": {}
    }
  ],
  "error_policy": {
    "type": "retry_then_fail"
  },
  "approval_policy": {
    "medium": "when_write_or_external",
    "high": "always",
    "critical": "always"
  },
  "retry_policy": {
    "max_attempts": 2,
    "backoff_strategy": "exponential"
  },
  "timeout_policy": {
    "workflow_timeout_ms": 300000,
    "timeout_action": "fail"
  },
  "created_by": "user",
  "created_at": "2026-05-15T00:00:00Z",
  "updated_at": "2026-05-15T00:00:00Z",
  "metadata": {}
}
```

## 6. Loại Step

| Type | Ý nghĩa | Approval mặc định |
|---|---|---|
| `tool_call` | gọi tool đã đăng ký | phụ thuộc tool/risk |
| `agent_task` | giao task cho Agent Runtime | khi có tool nguy hiểm |
| `condition` | rẽ nhánh | không |
| `loop` | lặp qua list/input | nếu step con cần |
| `approval` | chờ human decision | chính là approval |
| `delay` | chờ theo thời gian | không |
| `notification` | gửi thông báo local | không, trừ external send |
| `transform` | biến đổi JSON/text | không |
| `memory_search` | tìm memory/context | theo sensitivity |
| `model_call` | gọi local/cloud model | cloud + sensitive cần approval |
| `sub_workflow` | gọi workflow con | theo workflow con |

## 7. Chuyển Trạng Thái

### Workflow Definition

| Status | Ý nghĩa | Next hợp lệ |
|---|---|---|
| `draft` | đang soạn, chưa chạy tự động | `active`, `deleted` |
| `active` | có thể chạy/manual/schedule/event | `paused`, `disabled`, `archived`, `deleted` |
| `paused` | tạm dừng trigger | `active`, `disabled` |
| `archived` | lưu lịch sử | `active`, `deleted` |
| `disabled` | bị tắt bởi user/policy | `active`, `deleted` |
| `deleted` | soft delete | không |

### Workflow Run

| Status | Ý nghĩa | Next hợp lệ |
|---|---|---|
| `pending` | đã tạo, chưa chạy | `running`, `cancelled` |
| `running` | đang chạy | `waiting_approval`, `paused`, `completed`, `failed`, `cancelled` |
| `waiting_approval` | dừng chờ user | `running`, `failed`, `cancelled` |
| `paused` | user pause | `running`, `cancelled` |
| `completed` | chạy thành công | `rollback_running` |
| `failed` | chạy lỗi | `rollback_running`, `cancelled` |
| `cancelled` | user huỷ | không |
| `rollback_running` | đang rollback | `rollback_completed`, `rollback_failed` |
| `rollback_completed` | rollback xong | không |
| `rollback_failed` | rollback lỗi | không |

### Step Run

| Status | Ý nghĩa | Next hợp lệ |
|---|---|---|
| `pending` | chưa chạy | `running`, `skipped` |
| `running` | đang chạy | `success`, `failed`, `waiting_approval`, `retrying` |
| `waiting_approval` | chờ duyệt | `success`, `failed`, `skipped` |
| `success` | step thành công | `rolled_back` |
| `failed` | step lỗi | `retrying`, `rollback_failed` |
| `retrying` | đang chờ retry | `running`, `failed` |
| `skipped` | bị bỏ qua do condition/policy | không |
| `cancelled` | bị huỷ | không |
| `rolled_back` | compensation thành công | không |
| `rollback_failed` | compensation lỗi | không |

## 8. Database Schema Chính

| Bảng | Mục đích |
|---|---|
| `workflows` | workflow definition hiện tại |
| `workflow_versions` | lịch sử version DSL |
| `workflow_steps` | step đã normalize từ DSL |
| `workflow_triggers` | trigger manual/schedule/event/agent_generated |
| `workflow_runs` | mỗi lần chạy workflow |
| `workflow_step_runs` | trạng thái/input/output/error từng step |
| `workflow_schedules` | lịch chạy |
| `workflow_event_bindings` | mapping event -> workflow |
| `workflow_audit_events` | timeline audit |
| `workflow_replay_runs` | liên kết run replay với run gốc |
| `approval_requests` | approval gate |
| `retry_policies` | policy retry reusable |
| `rollback_actions` | compensation/rollback |

DDL mẫu nằm trong:

```text
src/main/resources/db/migration/V2__workflow_engine_schema.sql
```

## 9. Hợp Đồng API

### API Workflow Definition

| Method | Endpoint | Permission | Request | Response | Status |
|---|---|---|---|---|---|
| POST | `/api/workflows` | `workflow.write` | `CreateWorkflowRequest` | `WorkflowResponse` | 201/400 |
| GET | `/api/workflows` | `workflow.read` | query filter | list | 200 |
| GET | `/api/workflows/{workflowId}` | `workflow.read` | none | workflow | 200/404 |
| PUT | `/api/workflows/{workflowId}` | `workflow.write` | `UpdateWorkflowRequest` | workflow | 200/400 |
| DELETE | `/api/workflows/{workflowId}` | `workflow.delete` | none | none | 204/404 |
| POST | `/api/workflows/{workflowId}/activate` | `workflow.activate` | none | workflow | 200 |
| POST | `/api/workflows/{workflowId}/pause` | `workflow.pause` | none | workflow | 200 |
| POST | `/api/workflows/{workflowId}/clone` | `workflow.write` | none | workflow | 201 |
| GET | `/api/workflows/{workflowId}/versions` | `workflow.read` | none | versions | 200 |

### API Workflow Run

| Method | Endpoint | Permission | Request | Response | Status |
|---|---|---|---|---|---|
| POST | `/api/workflows/{workflowId}/run` | `workflow.run` | `{"input":{},"createdBy":"user"}` | run | 202 |
| GET | `/api/workflows/runs/{runId}` | `workflow.read` | none | run | 200 |
| GET | `/api/workflows/runs/{runId}/timeline` | `workflow.read` | none | timeline | 200 |
| POST | `/api/workflows/runs/{runId}/pause` | `workflow.control` | none | run | 200 |
| POST | `/api/workflows/runs/{runId}/resume` | `workflow.control` | none | run | 200 |
| POST | `/api/workflows/runs/{runId}/cancel` | `workflow.control` | none | run | 200 |
| POST | `/api/workflows/runs/{runId}/retry` | `workflow.control` | optional input | run | 202 |
| POST | `/api/workflows/runs/{runId}/rollback` | `workflow.control` | reason | rollback run | 202 |

### API Debug / Replay

| Method | Endpoint | Mục đích |
|---|---|---|
| GET | `/api/workflows/runs/{runId}/steps/{stepRunId}` | xem step run |
| GET | `/api/workflows/runs/{runId}/steps/{stepRunId}/input` | xem input redacted |
| GET | `/api/workflows/runs/{runId}/steps/{stepRunId}/output` | xem output redacted |
| POST | `/api/workflows/runs/{runId}/steps/{stepRunId}/replay` | tạo replay run từ step |

## 10. Cổng Approval

Bắt buộc approval với:

| Action | Lý do |
|---|---|
| write file | thay đổi dữ liệu local |
| delete file | mất dữ liệu |
| send email | tác động ra ngoài |
| execute shell command | rủi ro hệ thống |
| network call chưa whitelist | rò rỉ dữ liệu |
| cloud model với sensitive data | privacy risk |
| workflow do agent tự tạo | user cần duyệt |
| plugin/tool mới cài | quyền chưa được tin cậy |

Approval request cần có:

| Field | Ý nghĩa |
|---|---|
| `workflow_id`, `run_id`, `step_run_id` | liên kết workflow |
| `step_name`, `action_type`, `tool_name` | hành động cần duyệt |
| `risk_level`, `permission_level` | mức rủi ro/quyền |
| `input_preview`, `diff_preview` | preview đã redact |
| `expected_effect` | mô tả điều sẽ xảy ra |
| `expires_at`, `status` | hạn và trạng thái |
| `decision`, `decision_reason`, `decided_at` | quyết định user |

Quy tắc:

- Không auto-approve `critical`.
- `modify_and_approve` phải validate input mới.
- Approval expired thì workflow `failed` hoặc `paused` theo policy.
- Replay action nguy hiểm cần approval mới, không dùng lại approval cũ.

## 11. Retry / Timeout / Rollback

### Chính Sách Retry

```json
{
  "max_attempts": 3,
  "backoff_strategy": "exponential",
  "initial_delay_ms": 1000,
  "max_delay_ms": 30000,
  "retry_on_errors": ["TIMEOUT", "TEMPORARY_UNAVAILABLE"],
  "do_not_retry_on_errors": ["PERMISSION_DENIED", "VALIDATION_ERROR"]
}
```

| Strategy | Cách tính |
|---|---|
| `fixed` | delay cố định |
| `linear` | tăng tuyến tính theo attempt |
| `exponential` | delay tăng theo luỹ thừa, có max cap |

### Chính Sách Timeout

| Field | Ý nghĩa |
|---|---|
| `step_timeout_ms` | timeout từng step |
| `workflow_timeout_ms` | timeout toàn workflow |
| `timeout_action` | `fail`, `retry`, `pause_for_user` |

### Rollback

| Step | Compensation khả thi |
|---|---|
| `create_note` | xoá note hoặc mark archived |
| `write_file` | restore previous content |
| `create_memory` | delete/expire memory |
| `send_email` | không rollback được, chỉ audit warning |
| `delete_file` | restore từ backup nếu có |

Rollback tự động chỉ nên áp dụng với action low/medium có compensation an toàn. High/critical rollback cũng cần approval nếu có thể làm thay đổi dữ liệu.

## 12. Replay Và Debug

Yêu cầu:

- Replay luôn tạo `workflow_run` mới.
- Có `replay_parent_run_id`.
- Không ghi đè input/output run cũ.
- Chỉ dùng context đã lưu trong run cũ.
- Cho phép user sửa input step trước khi replay.
- Hành động nguy hiểm trong replay cần approval mới.

Debug UI cần hiển thị:

| Thành phần | Nội dung |
|---|---|
| Workflow graph | node/edge với status |
| Timeline | step status, duration, retry count |
| Step detail | input/output redacted, error stack |
| Approval decision | ai duyệt, lúc nào, lý do |
| Tool/model logs | tool call, model call, latency |
| Replay action | replay from this step |

## 13. Service Layer

| Service | Method chính | Ghi chú |
|---|---|---|
| WorkflowService | `createWorkflow`, `updateWorkflow`, `activateWorkflow`, `cloneWorkflow`, `createVersion` | transaction khi lưu DSL + steps |
| WorkflowRunner | `startRun`, `executeRun`, `pauseRun`, `resumeRun`, `cancelRun`, `failRun` | quản lý state |
| StepExecutor | `executeStep`, `executeToolCallStep`, `executeAgentTaskStep`, `executeApprovalStep` | gọi permission/approval/tool |
| ApprovalService | `createApprovalRequest`, `approve`, `reject`, `modifyAndApprove` | audit mọi decision |
| RetryPolicyEngine | `shouldRetry`, `calculateNextDelay`, `recordAttempt` | tránh retry lỗi permission |
| RollbackManager | `rollbackRun`, `rollbackStep`, `executeCompensationAction` | audit rollback |
| WorkflowScheduler | `registerSchedule`, `calculateNextRun`, `triggerDueWorkflows` | Spring Scheduling/Quartz |
| EventTriggerManager | `registerBinding`, `handleEvent`, `matchWorkflow` | local event bus |
| WorkflowAuditService | `logEvent`, `getTimeline`, `redactSensitiveData` | không log secret raw |
| WorkflowReplayService | `createReplayRun`, `replayFromStep`, `loadPreviousContext` | replay run mới |

## 14. Ví Dụ Workflow JSON

### Tóm tắt PDF và tạo note

```json
{
  "name": "Tóm tắt PDF",
  "trigger": {"type": "manual"},
  "input_schema": {
    "type": "object",
    "required": ["file_path"],
    "properties": {"file_path": {"type": "string"}}
  },
  "steps": [
    {
      "id": "read",
      "type": "tool_call",
      "input": {"tool_name": "read_local_file", "path": "{{input.file_path}}"},
      "risk_level": "low",
      "permission_level": "read_only",
      "requires_approval": false
    },
    {
      "id": "summarize",
      "type": "model_call",
      "depends_on": ["read"],
      "input": {"prompt": "Tóm tắt nội dung sau", "content": "{{steps.read.output.content}}"},
      "risk_level": "medium",
      "requires_approval": false
    },
    {
      "id": "create_note",
      "type": "tool_call",
      "depends_on": ["summarize"],
      "input": {"tool_name": "create_note", "content": "{{steps.summarize.output.text}}"},
      "risk_level": "medium",
      "permission_level": "write_draft",
      "requires_approval": true
    }
  ],
  "approval_policy": {"medium": "when_write_or_external", "high": "always", "critical": "always"},
  "retry_policy": {"max_attempts": 2, "backoff_strategy": "exponential"},
  "error_policy": {"type": "retry_then_fail"}
}
```

### Quét thư mục và tạo memory

```json
{
  "name": "Quét thư mục và ingest memory",
  "trigger": {"type": "manual"},
  "input_schema": {
    "type": "object",
    "required": ["folder_path"],
    "properties": {"folder_path": {"type": "string"}}
  },
  "steps": [
    {
      "id": "list_files",
      "type": "tool_call",
      "input": {"tool_name": "list_directory", "path": "{{input.folder_path}}"},
      "risk_level": "low",
      "permission_level": "read_only"
    },
    {
      "id": "ingest_each",
      "type": "loop",
      "depends_on": ["list_files"],
      "input": {"items": "{{steps.list_files.output.files}}"},
      "risk_level": "medium"
    }
  ],
  "approval_policy": {"medium": "folder_scope_required", "high": "always", "critical": "always"},
  "retry_policy": {"max_attempts": 3, "backoff_strategy": "exponential"},
  "error_policy": {"type": "continue_on_error"}
}
```

## 15. Chiến Lược Test

| Test | Input | Expected | Type | Priority |
|---|---|---|---|---|
| validate DSL thiếu step id | workflow JSON invalid | validation error | unit | P0 |
| status transition sai | `completed -> running` | bị chặn | unit | P0 |
| retry exponential | attempt 1/2/3 | delay tăng đúng | unit | P1 |
| write file cần approval | tool write | run `waiting_approval` | integration | P0 |
| approve tiếp tục workflow | approval approved | run chạy tiếp | integration | P0 |
| reject dừng workflow | approval rejected | run failed/skipped theo policy | integration | P0 |
| replay từ step lỗi | failed run | run mới có parent | integration | P1 |
| replay action nguy hiểm | replay write/delete | tạo approval mới | security | P0 |
| sensitive audit redaction | input chứa token | log không có raw token | security | P0 |
| app crash giữa workflow | running run | recover pending/running state | failure | P1 |

## 16. Kế Hoạch Triển Khai

| Bước | Việc cần làm |
|---|---|
| 1 | Hoàn thiện validation DSL trong `WorkflowService` |
| 2 | Nối `StepExecutor` với Tool Router thật |
| 3 | Thêm permission/approval check trước mọi write/delete/shell/network |
| 4 | Lưu input/output redacted cho từng step run |
| 5 | Hoàn thiện pause/resume/cancel/retry state transition |
| 6 | Thêm replay run mới với parent run id |
| 7 | Viết integration tests cho run/approval/replay |
| 8 | Nối Workflow Builder UI với API save/run/timeline |
