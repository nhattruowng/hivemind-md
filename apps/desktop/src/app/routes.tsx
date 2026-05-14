import type { ComponentType } from 'react';

import { ApprovalInboxPage } from '@/features/approvals/pages/ApprovalInboxPage';
import { AgentStudioPage } from '@/features/agent-studio/pages/AgentStudioPage';
import { WorkflowBuilderPage } from '@/features/workflows/pages/WorkflowBuilderPage';

export interface AppRoute {
  path: string;
  label: string;
  component: ComponentType;
  layout: 'app' | 'builder' | 'detail';
  guard?: string;
}

export const appRoutes: AppRoute[] = [
  { path: '/dashboard', label: 'Dashboard', component: WorkflowBuilderPage, layout: 'app' },
  { path: '/chat', label: 'Chat with Agent', component: WorkflowBuilderPage, layout: 'app' },
  { path: '/memory', label: 'Memory List', component: WorkflowBuilderPage, layout: 'app' },
  { path: '/memory/map', label: 'Memory Map', component: WorkflowBuilderPage, layout: 'app' },
  { path: '/memory/:memoryId', label: 'Memory Detail', component: WorkflowBuilderPage, layout: 'detail' },
  { path: '/memory/sources/:sourceId', label: 'Source Viewer', component: WorkflowBuilderPage, layout: 'detail' },
  { path: '/memory/conflicts', label: 'Memory Conflict Review', component: WorkflowBuilderPage, layout: 'app' },
  { path: '/tools', label: 'Tool Manager', component: WorkflowBuilderPage, layout: 'app' },
  { path: '/tools/:toolName', label: 'Tool Detail', component: WorkflowBuilderPage, layout: 'detail' },
  { path: '/permissions', label: 'Permission Center', component: WorkflowBuilderPage, layout: 'app', guard: 'developer' },
  { path: '/approvals', label: 'Approval Inbox', component: ApprovalInboxPage, layout: 'app' },
  { path: '/approvals/:approvalId', label: 'Approval Detail', component: ApprovalInboxPage, layout: 'detail' },
  { path: '/workflows', label: 'Workflow List', component: WorkflowBuilderPage, layout: 'app' },
  { path: '/workflows/new', label: 'New Workflow', component: WorkflowBuilderPage, layout: 'builder' },
  { path: '/workflows/:workflowId', label: 'Workflow Detail', component: WorkflowBuilderPage, layout: 'detail' },
  { path: '/workflows/:workflowId/builder', label: 'Workflow Builder', component: WorkflowBuilderPage, layout: 'builder' },
  { path: '/workflows/runs/:runId', label: 'Workflow Run Timeline', component: WorkflowBuilderPage, layout: 'detail' },
  { path: '/workflows/runs/:runId/debug', label: 'Workflow Debugger', component: WorkflowBuilderPage, layout: 'detail' },
  { path: '/agent-studio', label: 'Agent Studio', component: AgentStudioPage, layout: 'app', guard: 'developer' },
  { path: '/agent-studio/tools', label: 'Tool Schema Editor', component: AgentStudioPage, layout: 'app', guard: 'developer' },
  { path: '/agent-studio/prompts', label: 'Prompt Editor', component: AgentStudioPage, layout: 'app', guard: 'developer' },
  { path: '/agent-studio/evaluations', label: 'Evaluations', component: AgentStudioPage, layout: 'app', guard: 'developer' },
  { path: '/models', label: 'Model Settings', component: WorkflowBuilderPage, layout: 'app' },
  { path: '/connectors', label: 'Connectors', component: WorkflowBuilderPage, layout: 'app' },
  { path: '/audit', label: 'Audit Log', component: WorkflowBuilderPage, layout: 'app' },
  { path: '/settings', label: 'Settings', component: WorkflowBuilderPage, layout: 'app' }
];
