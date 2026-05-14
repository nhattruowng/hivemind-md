import type { PermissionLevel, RiskLevel } from '@/types/common.types';

export type ApprovalStatus =
  | 'pending'
  | 'approved'
  | 'rejected'
  | 'expired'
  | 'modified'
  | 'executing'
  | 'completed_after_approval'
  | 'failed_after_approval';

export interface ApprovalRequest {
  id: string;
  workflowId?: string;
  runId?: string;
  stepRunId?: string;
  stepName?: string;
  title?: string;
  requestedBy: string;
  toolName?: string;
  actionType: string;
  riskLevel: RiskLevel;
  permissionLevel: PermissionLevel;
  resourceType: string;
  resourceId?: string;
  previewJson: Record<string, unknown>;
  inputPreviewJson?: Record<string, unknown>;
  outputPreviewJson?: Record<string, unknown>;
  diffPreviewJson?: Record<string, unknown>;
  expectedEffect?: string;
  status: ApprovalStatus;
  reason?: string;
  createdAt: string;
  expiresAt?: string;
}

export interface ApprovalDecisionPayload {
  reason?: string;
  modifiedAction?: Record<string, unknown>;
}
