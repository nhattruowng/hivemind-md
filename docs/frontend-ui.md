# Frontend UI Guide

## 1. Stack

| Layer | Technology |
|---|---|
| App shell | Tauri v2 planned |
| Frontend | React + TypeScript |
| Build | Vite |
| Styling | Tailwind CSS |
| Server state | TanStack Query |
| Client UI state | Zustand |
| Workflow canvas | React Flow |
| Icons | lucide-react |
| Toast | Sonner |

## 2. Current UI

The current frontend scaffold includes:

- AppShell
- Sidebar
- TopBar
- StatusBar
- CommandPalette placeholder
- Workflow Builder page
- React Flow canvas
- Node palette
- Custom workflow node
- Step configuration panel
- Workflow JSON preview
- Validation panel
- Run test panel
- Approval Inbox page
- Agent Studio skeleton

## 3. Frontend Folder Structure

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

## 4. Workflow Builder Files

| File | Purpose |
|---|---|
| `WorkflowBuilderPage.tsx` | Builder layout |
| `WorkflowCanvas.tsx` | React Flow canvas |
| `WorkflowNode.tsx` | Custom workflow node |
| `NodePalette.tsx` | Draggable node palette |
| `StepConfigPanel.tsx` | Step editing panel |
| `WorkflowValidationPanel.tsx` | DSL validation warnings/errors |
| `WorkflowJsonPreview.tsx` | Readable workflow JSON |
| `WorkflowRunTestPanel.tsx` | Dry-run/test panel |
| `workflow.types.ts` | Workflow TypeScript types |
| `workflow.api.ts` | Workflow API client |
| `workflow.queries.ts` | TanStack Query hooks |
| `workflow.store.ts` | Zustand builder state |

## 5. Workflow Builder UX

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

## 6. State Management

| State type | Tool |
|---|---|
| Server state | TanStack Query |
| Workflow builder local draft | Zustand |
| Global UI state | Zustand |
| Future forms | React Hook Form + Zod |

## 7. Query Keys

```ts
workflowKeys.all
workflowKeys.lists()
workflowKeys.detail(workflowId)

approvalKeys.all
approvalKeys.list()
approvalKeys.detail(approvalId)
```

## 8. Next UI Tasks

1. Add router integration.
2. Add real route pages for Dashboard, Chat, Memory, Tools, Models, Audit, Settings.
3. Add CodeMirror JSON editor.
4. Add form validation with React Hook Form + Zod.
5. Add Tauri shell and native commands.
6. Add Playwright screenshot tests.

