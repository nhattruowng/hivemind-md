import type { PermissionLevel, RiskLevel, RunStatus } from '@/types/common.types';
import type { WorkflowDefinition, WorkflowStep } from '@/features/workflows/workflow.types';

export interface AgentRun {
  id: string;
  userId?: string;
  userMessage: string;
  intent?: string;
  status: RunStatus;
  riskLevel: RiskLevel;
  requiresMemory: boolean;
  requiresTools: boolean;
  approvalRequired: boolean;
  confidence: number;
  createdAt: string;
}

export interface AgentRunStep {
  id: string;
  runId: string;
  stepIndex: number;
  stepType: string;
  toolName?: string;
  status: string;
  input: Record<string, unknown>;
  output?: Record<string, unknown>;
}

export interface AgentTrace {
  id: string;
  runId: string;
  eventType: string;
  payload: Record<string, unknown>;
  createdAt: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
  createdAt: string;
  toolCalls?: ToolCallCard[];
  citations?: MemoryNode[];
}

export interface ToolCallCard {
  toolName: string;
  status: string;
  riskLevel: RiskLevel;
  approvalRequestId?: string;
  inputPreview: Record<string, unknown>;
  outputPreview?: Record<string, unknown>;
}

export interface MemoryNode {
  id: string;
  sourceId: string;
  memoryType: string;
  title?: string;
  content: string;
  summary?: string;
  confidenceScore: number;
  sensitivityLevel: 'public' | 'internal' | 'sensitive' | 'secret';
  status: string;
  sourceTrace: Record<string, unknown>;
}

export interface MemorySource {
  id: string;
  sourceType: string;
  uri?: string;
  filePath?: string;
  fileHash?: string;
  sourceMissing: boolean;
}

export interface MemoryRelation {
  id: string;
  fromMemoryId: string;
  toMemoryId: string;
  relationType: string;
  confidenceScore: number;
}

export interface MemoryVersion {
  id: string;
  memoryId: string;
  version: number;
  action: string;
  snapshot: Record<string, unknown>;
  createdAt: string;
}

export interface ToolDefinition {
  name: string;
  displayName: string;
  description: string;
  category: string;
  version: string;
  inputSchema: Record<string, unknown>;
  outputSchema: Record<string, unknown>;
  permissionLevel: PermissionLevel;
  riskLevel: RiskLevel;
  requiresApproval: boolean;
  enabled: boolean;
}

export interface ToolPermission {
  id: string;
  toolName: string;
  action: string;
  scopeType: string;
  scopeValue: string;
  permissionLevel: PermissionLevel;
}

export interface WorkflowRun {
  id: string;
  workflowId: string;
  workflowVersion: number;
  status: RunStatus;
  input: Record<string, unknown>;
  output?: Record<string, unknown>;
}

export interface WorkflowStepRun {
  id: string;
  runId: string;
  stepKey: string;
  stepName: string;
  status: string;
  attempt: number;
}

export interface WorkflowAuditEvent {
  id: string;
  runId: string;
  stepRunId?: string;
  eventType: string;
  status: string;
  message: string;
}

export interface ModelConfig {
  id: string;
  provider: 'ollama' | 'llama_cpp' | 'openai' | 'anthropic' | 'gemini';
  modelName: string;
  taskType: string;
  privacyMax: string;
  enabled: boolean;
}

export interface ConnectorConfig {
  id: string;
  connectorType: string;
  displayName: string;
  status: 'disabled' | 'enabled' | 'syncing' | 'error';
  scope: Record<string, unknown>;
}

export interface AuditLogEvent {
  id: string;
  eventType: string;
  actorType: string;
  resourceType?: string;
  resourceId?: string;
  riskLevel?: RiskLevel;
  summary: string;
  redactedPayload: Record<string, unknown>;
  createdAt: string;
}

export interface DashboardSummary {
  pendingApprovals: number;
  activeWorkflows: number;
  recentAgentRuns: AgentRun[];
  memoryStats: { total: number; conflicted: number; lowConfidence: number };
  toolRiskAlerts: ToolDefinition[];
  localModelStatus: 'online' | 'offline' | 'degraded';
}

export type WorkflowReactFlowNodeData = {
  step: WorkflowStep;
  validationState?: 'valid' | 'warning' | 'error';
};

export type ApprovalAction = 'approve' | 'reject' | 'modify_and_approve' | 'always_allow_tool' | 'always_allow_folder' | 'never_allow';

export type { WorkflowDefinition, WorkflowStep };
