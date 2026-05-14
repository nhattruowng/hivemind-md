# Tài Liệu Desktop UI BizFlow

Tài liệu này mô tả UI desktop cho BizFlow Local Agent. Mục tiêu là tạo một app developer-focused, dark mode, không chỉ là chatbot, mà còn có Workflow Builder, Approval Inbox, Memory, Tool Manager, Agent Studio và Audit Log.

## 1. Công Nghệ Sử Dụng

| Lớp | Công nghệ | Lý do chọn |
|---|---|---|
| Desktop shell | Tauri v2, planned | nhẹ, native, hợp với local-first |
| Frontend | React + TypeScript | ecosystem mạnh, type safety |
| Build | Vite | nhanh, cấu hình đơn giản |
| Styling | Tailwind CSS | token hoá UI nhanh, hợp dark mode |
| Server state | TanStack Query | cache API, loading/error state rõ |
| Client state | Zustand | nhẹ, dễ tách store theo feature |
| Workflow canvas | React Flow | kéo-thả node/edge, custom node tốt |
| Icons | lucide-react | nhất quán, nhẹ |
| Toast | Sonner | feedback nhanh |

## 2. UI Hiện Có

| Thành phần | Trạng thái | Ghi chú |
|---|---|---|
| AppShell | đã có | Sidebar, TopBar, Main, StatusBar |
| Sidebar | đã có | điều hướng chính |
| TopBar | đã có | workspace/search/model status placeholder |
| StatusBar | đã có | core/model/vector/audit status placeholder |
| CommandPalette | placeholder | cần nối shortcut `Ctrl/Cmd+K` |
| Workflow Builder | đã có skeleton | React Flow canvas, palette, config, JSON preview |
| Approval Inbox | đã có skeleton | danh sách/detail, approve/reject placeholder |
| Agent Studio | đã có skeleton | tabs/khung test tool/prompt |

## 3. Cấu Trúc Frontend

```text
apps/desktop/src/
  app/
  components/
    layout/
    ui/
  features/
    agent-studio/
    approvals/
    workflows/
  services/
  stores/
  styles/
  types/
  utils/
```

## 4. Workflow Builder

| File | Vai trò |
|---|---|
| `WorkflowBuilderPage.tsx` | layout tổng cho builder |
| `WorkflowCanvas.tsx` | React Flow canvas |
| `WorkflowNode.tsx` | custom node UI |
| `NodePalette.tsx` | palette kéo-thả node |
| `StepConfigPanel.tsx` | panel chỉnh cấu hình step |
| `WorkflowValidationPanel.tsx` | cảnh báo/lỗi validation DSL |
| `WorkflowJsonPreview.tsx` | preview workflow JSON |
| `WorkflowRunTestPanel.tsx` | panel dry-run/test |
| `workflow.types.ts` | TypeScript type cho workflow |
| `workflow.api.ts` | API client |
| `workflow.queries.ts` | TanStack Query hooks |
| `workflow.store.ts` | Zustand state cho builder |

## 5. Palette Node

| Node | Mục đích | Risk mặc định |
|---|---|---|
| Tool Call | gọi tool đã đăng ký | phụ thuộc tool |
| Agent Task | giao task cho agent runtime | medium |
| Condition | rẽ nhánh logic | low |
| Loop | lặp qua danh sách/input | medium |
| Approval | chờ user duyệt | low |
| Delay | chờ theo thời gian | low |
| Notification | báo cho user | low |
| Memory Search | tìm memory/context | low-medium |
| Model Call | gọi local/cloud model | medium |

## 6. Layout Workflow Builder

```text
┌─────────────────────────────────────────────────────────────┐
│ TopBar                                                      │
├──────────────┬──────────────────────────────┬───────────────┤
│ Node Palette │ React Flow Canvas            │ Config Panel  │
│              │                              │               │
├──────────────┼──────────────────────────────┼───────────────┤
│ Validation   │ JSON Preview                 │ Run Test      │
└──────────────┴──────────────────────────────┴───────────────┘
```

## 7. Quản Lý State

| Loại state | Công cụ | Ví dụ |
|---|---|---|
| Server state | TanStack Query | workflow list, approval list, run timeline |
| UI state global | Zustand | sidebar collapsed, command palette open, theme |
| Builder draft | Zustand | nodes, edges, selected node, dirty state |
| Form state | React Hook Form + Zod, planned | step config, permission policy, approval modify |

## 8. Query Key

```ts
workflowKeys.all
workflowKeys.lists()
workflowKeys.detail(workflowId)
workflowKeys.run(runId)
workflowKeys.timeline(runId)

approvalKeys.all
approvalKeys.list()
approvalKeys.detail(approvalId)
```

## 9. UX Quy Định

| Quy định | Lý do |
|---|---|
| Dark mode mặc định | hợp developer tool và desktop app |
| Risk badge luôn hiện với action nguy hiểm | user phải thấy rủi ro trước khi duyệt |
| Không chỉ dùng màu để báo risk | hỗ trợ accessibility |
| Delete/write/shell phải có confirm/approval rõ | tránh agent tự ý hành động |
| JSON preview readonly mặc định | tránh user không kỹ thuật làm hỏng DSL |
| Developer mode mới cho sửa JSON trực tiếp | cân bằng power user và an toàn |

## 10. Việc Cần Làm Tiếp

| Việc | Ưu tiên |
|---|---|
| Thêm router thật cho Dashboard, Chat, Memory, Tools, Models, Audit, Settings | cao |
| Nối Workflow Builder với API save/run/test | cao |
| Thêm CodeMirror JSON editor | trung bình |
| Thêm React Hook Form + Zod cho step config | cao |
| Thêm Tauri shell và native commands | cao |
| Thêm Playwright screenshot/e2e tests | trung bình |
