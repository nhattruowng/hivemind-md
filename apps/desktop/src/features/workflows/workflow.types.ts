import type { Edge, Node } from '@xyflow/react';

import type { PermissionLevel, RiskLevel, RunStatus } from '@/types/common.types';

export type WorkflowTriggerType = 'manual' | 'schedule' | 'event' | 'agent_generated';
export type WorkflowStatus = 'draft' | 'active' | 'paused' | 'archived' | 'disabled' | 'deleted';
export type WorkflowStepType =
  | 'tool_call'
  | 'agent_task'
  | 'condition'
  | 'loop'
  | 'approval'
  | 'delay'
  | 'notification'
  | 'memory_search'
  | 'model_call'
  | 'transform'
  | 'sub_workflow';

export interface WorkflowStep {
  id: string;
  name: string;
  type: WorkflowStepType;
  description?: string;
  input: Record<string, unknown>;
  output_mapping: Record<string, unknown>;
  depends_on: string[];
  condition?: Record<string, unknown>;
  retry_policy?: WorkflowRetryPolicy;
  timeout_ms: number;
  requires_approval: boolean;
  risk_level: RiskLevel;
  permission_level: PermissionLevel;
  compensation?: Record<string, unknown>;
  on_success?: Record<string, unknown>;
  on_failure?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

export interface WorkflowRetryPolicy {
  max_attempts: number;
  backoff_strategy: 'fixed' | 'linear' | 'exponential';
  initial_delay_ms?: number;
  max_delay_ms?: number;
}

export interface WorkflowDefinition {
  id?: string;
  name: string;
  description?: string;
  version: number;
  status: WorkflowStatus;
  trigger: {
    type: WorkflowTriggerType;
    cron?: string;
    timezone?: string;
    event_type?: string;
  };
  input_schema: Record<string, unknown>;
  output_schema: Record<string, unknown>;
  variables: Record<string, unknown>;
  steps: WorkflowStep[];
  error_policy: Record<string, unknown>;
  approval_policy: Record<string, unknown>;
  retry_policy: WorkflowRetryPolicy;
  timeout_policy: Record<string, unknown>;
  created_by?: string;
  metadata?: Record<string, unknown>;
}

export interface WorkflowResponse {
  id: string;
  name: string;
  description?: string;
  status: WorkflowStatus;
  triggerType: WorkflowTriggerType;
  version: number;
  definition: WorkflowDefinition;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
}

export interface WorkflowRun {
  id: string;
  workflowId: string;
  workflowVersion: number;
  status: RunStatus;
  triggerType: WorkflowTriggerType;
  input: Record<string, unknown>;
  output?: Record<string, unknown>;
  error?: Record<string, unknown>;
  replayParentRunId?: string;
  createdBy: string;
  startedAt?: string;
  completedAt?: string;
}

export interface WorkflowStepRun {
  id: string;
  runId: string;
  stepKey: string;
  stepName: string;
  stepType: WorkflowStepType;
  status: string;
  attempt: number;
  input: Record<string, unknown>;
  output?: Record<string, unknown>;
  error?: Record<string, unknown>;
  approvalRequestId?: string;
  startedAt?: string;
  completedAt?: string;
}

export interface WorkflowAuditEvent {
  id: string;
  eventType: string;
  status: string;
  message: string;
  payload: Record<string, unknown>;
  createdAt: string;
}

export interface WorkflowNodeData {
  step: WorkflowStep;
  selected?: boolean;
}

export type WorkflowFlowNode = Node<WorkflowNodeData, 'workflowNode'>;
export type WorkflowFlowEdge = Edge;

export interface WorkflowValidationIssue {
  id: string;
  severity: 'error' | 'warning';
  title: string;
  detail: string;
  stepId?: string;
}
