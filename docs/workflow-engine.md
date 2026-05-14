# BizFlow Local Agent - Workflow Engine

## 1. Executive Summary

The Workflow Engine runs local-first business automations with explicit state, approval gates, retry, pause/resume, rollback hooks, replay/debug, and audit timeline. The MVP implementation uses Java 21, Spring Boot 3, SQLite JDBC, Flyway, Spring Scheduling, REST controllers, Jackson JSON, Jakarta Validation, and JUnit 5.

## 2. Workflow Engine Architecture

| Module | Responsibility | Input | Output | Tables | API | Risk | Mitigation |
|---|---|---|---|---|---|---|---|
| WorkflowService | Create/update/delete/activate/clone/version workflow DSL | Workflow JSON | Workflow definition | `workflows`, `workflow_versions`, `workflow_steps`, `workflow_triggers` | `/api/workflows` | Invalid DSL | Validate before save |
| WorkflowRunner | Create run, execute steps, pause/resume/cancel/retry | Workflow id, input | Run state | `workflow_runs`, `workflow_step_runs` | `/api/workflows/{id}/run` | Bad state transition | Explicit statuses |
| StepExecutor | Execute tool/agent/condition/loop/approval/delay/notification/transform/memory/model/subflow | Step config | Step output | `workflow_step_runs` | internal | Dangerous action | Approval gate |
| ApprovalService | Create approval, approve/reject/modify | Pending action | Decision | `approval_requests` | `/api/approvals` | Bypass | All high/critical actions stop run |
| RetryPolicyEngine | Retry decision and backoff | Attempt, error | Retry/delay | `retry_policies` | internal | Duplicate side effects | Idempotency key |
| RollbackManager | Compensation actions | Failed/completed run | Rollback status | `rollback_actions` | `/rollback` | Non-reversible action | Audit warning |
| WorkflowScheduler | Cron-based local scheduler | Schedule | Due runs | `workflow_schedules` | `/schedule` | Duplicate runs | `idempotency_key` |
| EventTriggerManager | Match connector events | Event payload | Runs | `workflow_event_bindings` | `/event-binding` | Event spam | Scope + debounce future |
| WorkflowAuditService | Redacted timeline | Event | Audit row | `workflow_audit_events` | `/timeline` | Sensitive logs | Redaction |
| WorkflowReplayService | Replay from step | Parent run, step | New run | `workflow_replay_runs` | `/replay` | Repeated dangerous action | New approval required |

## 3. Workflow Types

| Type | Trigger | Use case | Input | Output | Risk | Approval rule | Example |
|---|---|---|---|---|---|---|---|
| Manual | User clicks Run | Summarize PDF | `file_path` | Note/report | Medium | Write steps require approval | Summarize one contract |
| Scheduled | Cron tick | Daily report | schedule context | Daily note | Medium | First activation + write approval | 08:00 report |
| Event-based | Connector event | Ingest new file | event payload | Memory nodes | Medium-high | Folder scope required | New file in folder |
| Agent-generated | Agent proposes | Automate repeated task | chat-derived DSL | Draft workflow | High | User must approve before save/run | “Every morning summarize tasks” |

## 4. Execution Flow Diagrams

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
If approval required → ApprovalService
  ↓
If error → RetryPolicyEngine
  ↓
If failed → mark failed
  ↓
If success → mark completed
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
User approve/reject/modify
  ↓
If approve → continue
  ↓
If reject → stop or skip based on config
  ↓
Audit decision
```

### Replay/Debug

```text
User opens failed run
  ↓
View step timeline
  ↓
Select failed step
  ↓
Inspect input/output/error
  ↓
Choose replay from this step
  ↓
Create replay run
  ↓
Reuse previous run context where safe
  ↓
Execute from selected step
  ↓
Audit replay
```

## 5. Workflow DSL JSON Design

```json
{
  "id": "wf_pdf_summary",
  "name": "Summarize PDF",
  "description": "Read a PDF, summarize it, and create a note.",
  "version": 1,
  "status": "draft",
  "trigger": {"type": "manual"},
  "input_schema": {
    "type": "object",
    "required": ["file_path"],
    "properties": {"file_path": {"type": "string"}}
  },
  "output_schema": {"type": "object"},
  "variables": {},
  "steps": [
    {
      "id": "read_file",
      "name": "Read file",
      "type": "tool_call",
      "input": {"tool_name": "read_local_file", "path": "{{input.file_path}}"},
      "output_mapping": {"file_content": "$.content"},
      "depends_on": [],
      "condition": {},
      "retry_policy": {"max_attempts": 2, "backoff_strategy": "fixed"},
      "timeout_ms": 30000,
      "requires_approval": false,
      "risk_level": "low",
      "permission_level": "read_only",
      "compensation": {},
      "on_success": {},
      "on_failure": {"policy": "fail_fast"},
      "metadata": {}
    }
  ],
  "error_policy": {"type": "retry_then_fail"},
  "approval_policy": {"high": "always", "critical": "always"},
  "retry_policy": {"max_attempts": 2, "backoff_strategy": "exponential"},
  "timeout_policy": {"workflow_timeout_ms": 300000, "timeout_action": "fail"},
  "created_by": "user",
  "created_at": "2026-05-14T00:00:00Z",
  "updated_at": "2026-05-14T00:00:00Z",
  "metadata": {}
}
```

## 6. Status Transition Design

| Entity | Status | Meaning | Next valid states |
|---|---|---|---|
| Definition | `draft` | Editable, not runnable | `active`, `deleted` |
| Definition | `active` | Runnable | `paused`, `disabled`, `archived`, `deleted` |
| Definition | `paused` | Temporarily not triggered | `active`, `disabled` |
| Definition | `archived` | Historical | `active`, `deleted` |
| Definition | `disabled` | Blocked by user/system | `active`, `deleted` |
| Definition | `deleted` | Soft deleted | none |
| Run | `pending` | Created not started | `running`, `cancelled` |
| Run | `running` | Executing | `waiting_approval`, `paused`, `completed`, `failed`, `cancelled` |
| Run | `waiting_approval` | Paused on approval | `running`, `failed`, `cancelled` |
| Run | `paused` | User paused | `running`, `cancelled` |
| Run | `completed` | Success | `rollback_running` |
| Run | `failed` | Failed | `rollback_running`, `cancelled` |
| Step | `pending` | Not started | `running`, `skipped` |
| Step | `running` | Executing | `success`, `failed`, `waiting_approval`, `retrying` |
| Step | `waiting_approval` | Needs user decision | `success`, `failed`, `skipped` |
| Step | `success` | Completed | `rolled_back` |
| Step | `failed` | Failed | `retrying`, `rollback_failed` |

## 7. API Contract

| Method | Endpoint | Permission | Request | Response | Codes | Errors |
|---|---|---|---|---|---|---|
| POST | `/api/workflows` | `workflow.write` | `CreateWorkflowRequest` | `WorkflowResponse` | 201, 400 | `WORKFLOW_VALIDATION_FAILED` |
| GET | `/api/workflows` | `workflow.read` | none | workflow list | 200 | none |
| GET | `/api/workflows/{id}` | `workflow.read` | none | workflow | 200, 404 | `BAD_REQUEST` |
| PUT | `/api/workflows/{id}` | `workflow.write` | `UpdateWorkflowRequest` | workflow | 200, 400 | validation |
| DELETE | `/api/workflows/{id}` | `workflow.delete` | none | none | 204 | not found |
| POST | `/api/workflows/{id}/activate` | `workflow.activate` | none | workflow | 200 | validation |
| POST | `/api/workflows/{id}/pause` | `workflow.pause` | none | workflow | 200 | not found |
| POST | `/api/workflows/{id}/clone` | `workflow.write` | none | workflow | 201 | not found |
| GET | `/api/workflows/{id}/versions` | `workflow.read` | none | versions | 200 | not found |
| POST | `/api/workflows/{id}/run` | `workflow.run` | `{"input":{},"createdBy":"user"}` | run | 202 | approval required |
| GET | `/api/workflows/runs/{runId}` | `workflow.read` | none | run | 200 | not found |
| GET | `/api/workflows/runs/{runId}/timeline` | `workflow.read` | none | timeline | 200 | not found |
| POST | `/api/workflows/runs/{runId}/pause` | `workflow.control` | none | run | 200 | invalid state |
| POST | `/api/workflows/runs/{runId}/resume` | `workflow.control` | none | run | 200 | invalid state |
| POST | `/api/workflows/runs/{runId}/cancel` | `workflow.control` | none | run | 200 | invalid state |
| POST | `/api/workflows/runs/{runId}/rollback` | `workflow.rollback` | none | run | 200 | rollback failed |
| POST | `/api/workflows/runs/{runId}/steps/{stepRunId}/replay` | `workflow.replay` | `{"inputOverride":{}}` | new run | 202/200 | approval required |

## 8. Approval Gate Design

Approval is mandatory for write file, delete file, send email, shell execution, non-whitelisted network call, cloud model with sensitive data, first connector access, and agent-generated workflow activation.

Approval request contains: `id`, `workflow_id`, `run_id`, `step_run_id`, `step_name`, `action_type`, `tool_name`, `risk_level`, `permission_level`, `input_preview`, `output_preview`, `expected_effect`, `diff_preview`, `created_at`, `expires_at`, `status`, `decision`, `decision_reason`, `decided_at`.

Critical actions are never auto-approved by default. Replay of dangerous steps creates a fresh approval.

## 9. Retry / Timeout / Rollback

| Policy | Fields |
|---|---|
| Retry | `max_attempts`, `backoff_strategy`, `initial_delay_ms`, `max_delay_ms`, `retry_on_errors`, `do_not_retry_on_errors` |
| Timeout | `step_timeout_ms`, `workflow_timeout_ms`, `timeout_action` |
| Rollback | Step `compensation` plus `rollback_actions` table |

Rollback examples: `create_note → archive_note`, `write_file → restore previous content`, `create_memory → delete_memory`, `send_email → cannot rollback, audit warning`.

## 10. Workflow JSON Examples

### 10.1 Summarize PDF

```json
{
  "trigger": {"type": "manual"},
  "input_schema": {"type": "object", "required": ["file_path"]},
  "steps": [
    {"id": "read", "name": "Read file", "type": "tool_call", "input": {"tool_name": "read_local_file", "path": "{{input.file_path}}"}, "risk_level": "low", "permission_level": "read_only"},
    {"id": "extract", "name": "Extract text", "type": "tool_call", "input": {"tool_name": "extract_pdf_text"}, "depends_on": ["read"], "risk_level": "low", "permission_level": "read_only"},
    {"id": "summarize", "name": "Summarize", "type": "agent_task", "input": {"task": "summarize_document"}, "depends_on": ["extract"], "risk_level": "low", "permission_level": "read_only"},
    {"id": "note", "name": "Create note", "type": "tool_call", "input": {"tool_name": "create_note"}, "depends_on": ["summarize"], "requires_approval": true, "risk_level": "medium", "permission_level": "write_draft"}
  ],
  "approval_policy": {"write": "always"},
  "retry_policy": {"max_attempts": 2, "backoff_strategy": "exponential"},
  "error_policy": {"type": "retry_then_fail"}
}
```

### 10.2 Scan Folder And Create Memory

```json
{
  "trigger": {"type": "event", "event_type": "file_created"},
  "input_schema": {"type": "object", "required": ["folder_path"]},
  "steps": [
    {"id": "list", "name": "List directory", "type": "tool_call", "input": {"tool_name": "list_directory", "path": "{{input.folder_path}}"}, "risk_level": "low", "permission_level": "read_only"},
    {"id": "filter", "name": "Filter files", "type": "transform", "depends_on": ["list"], "risk_level": "low", "permission_level": "read_only"},
    {"id": "loop", "name": "Ingest each file", "type": "loop", "depends_on": ["filter"], "input": {"items": "{{steps.filter.output.files}}"}, "risk_level": "medium", "permission_level": "execute_auto"},
    {"id": "report", "name": "Report result", "type": "notification", "depends_on": ["loop"], "risk_level": "low", "permission_level": "execute_auto"}
  ],
  "approval_policy": {"folder_first_access": "always"},
  "retry_policy": {"max_attempts": 3, "backoff_strategy": "linear"},
  "error_policy": {"type": "continue_on_error"}
}
```

### 10.3 Draft Email But Do Not Send

```json
{
  "trigger": {"type": "manual"},
  "input_schema": {"type": "object", "required": ["recipient", "topic"]},
  "steps": [
    {"id": "context", "name": "Gather memory context", "type": "memory_search", "input": {"query": "{{input.topic}}"}, "risk_level": "low", "permission_level": "read_only"},
    {"id": "draft", "name": "Draft email", "type": "agent_task", "depends_on": ["context"], "input": {"recipient": "{{input.recipient}}"}, "risk_level": "medium", "permission_level": "write_draft"},
    {"id": "approval", "name": "Preview draft", "type": "approval", "depends_on": ["draft"], "requires_approval": true, "risk_level": "medium", "permission_level": "execute_with_approval"},
    {"id": "save", "name": "Save draft", "type": "tool_call", "depends_on": ["approval"], "input": {"tool_name": "create_note"}, "risk_level": "medium", "permission_level": "write_draft"}
  ],
  "approval_policy": {"send_email": "forbidden", "write_draft": "approval"},
  "retry_policy": {"max_attempts": 1},
  "error_policy": {"type": "require_user_decision"}
}
```

### 10.4 Daily Report

```json
{
  "trigger": {"type": "schedule", "cron": "0 0 8 * * *", "timezone": "Asia/Saigon"},
  "input_schema": {"type": "object"},
  "steps": [
    {"id": "recent", "name": "Get recent memory", "type": "memory_search", "input": {"query": "recent tasks"}, "risk_level": "low", "permission_level": "read_only"},
    {"id": "summary", "name": "Summarize tasks", "type": "agent_task", "depends_on": ["recent"], "risk_level": "low", "permission_level": "read_only"},
    {"id": "report", "name": "Generate report", "type": "model_call", "depends_on": ["summary"], "risk_level": "medium", "permission_level": "execute_auto"},
    {"id": "note", "name": "Create report note", "type": "tool_call", "depends_on": ["report"], "input": {"tool_name": "create_note"}, "requires_approval": true, "risk_level": "medium", "permission_level": "write_draft"},
    {"id": "notify", "name": "Notify user", "type": "notification", "depends_on": ["note"], "risk_level": "low", "permission_level": "execute_auto"}
  ],
  "approval_policy": {"write": "always"},
  "retry_policy": {"max_attempts": 2, "backoff_strategy": "fixed"},
  "error_policy": {"type": "retry_then_fail"}
}
```

## 11. UI Requirements

| Screen | Purpose | Components | APIs | Empty | Loading | Error | Actions |
|---|---|---|---|---|---|---|---|
| Workflow List | See workflows | table, trigger/status chips | `GET /api/workflows` | no workflows | skeleton rows | retry panel | run, edit, activate |
| Workflow Builder | Build DSL | React Flow canvas, config panel, JSON preview | create/update/activate | blank canvas | validating | invalid DSL list | save draft, activate |
| Run Timeline | Inspect run | step list, duration, retries, audit events | run/timeline | no runs | timeline skeleton | error details | pause/resume/cancel |
| Approval Inbox | Decide pending actions | risk badge, preview, diff | approvals APIs | no approvals | cards skeleton | failed decision | approve/reject/modify |
| Debugger | Replay/debug | graph, step IO, logs | step/debug/replay | no failed step | loading logs | replay error | replay from step |

## 12. Testing Strategy

| Test | Input | Expected | Type | Priority |
|---|---|---|---|---|
| DSL validation | missing steps | validation error | Unit | P0 |
| Status transition | running→paused→running | valid states | Unit | P0 |
| Condition eval | true condition | next step runs | Unit | P1 |
| Retry calculation | exponential policy | capped delay | Unit | P0 |
| Approval rule | high-risk write | approval required | Unit | P0 |
| Rollback decision | no compensation | audit warning | Unit | P1 |
| Schedule calculation | cron daily | next run computed | Unit | P1 |
| Event matching | `file_created` | workflow matched | Unit | P1 |
| Create→run→complete | simple transform workflow | completed | Integration | P0 |
| Approval approve | write step | resume continues | Integration | P0 |
| Approval reject | write step | failed/skipped | Integration | P0 |
| Replay from failed | failed step | new replay run | Integration | P0 |
| Critical no auto approve | critical shell | waiting approval | Security | P0 |
| Audit redaction | token in input | redacted token | Security | P0 |
| 100 steps | long workflow | stable timeline | Performance | P1 |
| Crash mid-run | running state | recover/replay | Failure | P1 |

## 13. Risks & Mitigation

| Risk | Impact | Likelihood | Prevention | Detection | Recovery |
|---|---:|---:|---|---|---|
| Dangerous action | High | Medium | Approval gate | Audit timeline | Cancel/rollback |
| Approval bypass | Critical | Low | Central StepExecutor check | Security tests | Disable workflow |
| Replay repeats side effect | High | Medium | Fresh approval for risky replay | Replay audit | Rollback where possible |
| Retry duplicate action | High | Medium | Idempotency key | Duplicate detection | Compensation |
| Email cannot rollback | High | Medium | Draft-only by default | Audit | Notify user |
| App crash | Medium | Medium | Durable state | startup scan | resume/replay |
| Bad state | High | Medium | explicit enums | transition tests | mark failed |
| Duplicate scheduled run | Medium | Medium | idempotency key | run query | cancel duplicate |
| Event spam | Medium | Medium | scope/rate limit future | event counts | disable binding |
| Sensitive audit | High | Medium | redaction | audit tests | purge logs |
| DSL payload injection | High | Medium | schema validation | validation logs | reject DSL |
| Invalid UI workflow | Medium | High | builder validation | API 400 | save draft only |

## 14. Implementation Plan

1. Finish tool-router integration inside `StepExecutor`.
2. Add permission engine checks before approval creation.
3. Add real condition/loop/transform expression evaluator.
4. Add run context variable interpolation.
5. Add Quartz if Spring Scheduling becomes insufficient.
6. Add crash recovery job for `running` runs.
7. Add approval expiry handler.
8. Add full integration tests with SQLite temp DB.
