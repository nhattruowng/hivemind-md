export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';
export type PermissionLevel =
  | 'read_only'
  | 'write_draft'
  | 'execute_with_approval'
  | 'execute_auto'
  | 'forbidden';
export type RunStatus =
  | 'pending'
  | 'running'
  | 'waiting_approval'
  | 'paused'
  | 'completed'
  | 'failed'
  | 'cancelled'
  | 'rollback_running'
  | 'rollback_completed'
  | 'rollback_failed';

export interface ApiResponse<T> {
  data: T;
  trace_id?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}
