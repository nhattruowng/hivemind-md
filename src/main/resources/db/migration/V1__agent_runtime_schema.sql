PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 5000;

CREATE TABLE IF NOT EXISTS agent_runs (
  id TEXT PRIMARY KEY,
  user_id TEXT,
  user_message TEXT NOT NULL,
  intent TEXT,
  status TEXT NOT NULL,
  risk_level TEXT NOT NULL,
  requires_memory INTEGER NOT NULL DEFAULT 0,
  requires_tools INTEGER NOT NULL DEFAULT 0,
  approval_required INTEGER NOT NULL DEFAULT 0,
  approval_request_id TEXT,
  confidence REAL NOT NULL DEFAULT 0.0,
  error_message TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  completed_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_agent_runs_status ON agent_runs(status, created_at);

CREATE TABLE IF NOT EXISTS agent_run_steps (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES agent_runs(id) ON DELETE CASCADE,
  step_index INTEGER NOT NULL,
  step_type TEXT NOT NULL,
  tool_name TEXT,
  status TEXT NOT NULL,
  input_json TEXT NOT NULL DEFAULT '{}',
  output_json TEXT,
  error_message TEXT,
  created_at TEXT NOT NULL,
  completed_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_agent_run_steps_run ON agent_run_steps(run_id, step_index);

CREATE TABLE IF NOT EXISTS agent_traces (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES agent_runs(id) ON DELETE CASCADE,
  event_type TEXT NOT NULL,
  payload_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_agent_traces_run ON agent_traces(run_id, created_at);

CREATE TABLE IF NOT EXISTS tool_definitions (
  name TEXT PRIMARY KEY,
  display_name TEXT NOT NULL,
  description TEXT NOT NULL,
  category TEXT NOT NULL,
  version TEXT NOT NULL,
  input_schema_json TEXT NOT NULL,
  output_schema_json TEXT NOT NULL,
  permission_level TEXT NOT NULL,
  risk_level TEXT NOT NULL,
  requires_approval INTEGER NOT NULL DEFAULT 0,
  allowed_paths_json TEXT NOT NULL DEFAULT '[]',
  blocked_paths_json TEXT NOT NULL DEFAULT '[]',
  network_access INTEGER NOT NULL DEFAULT 0,
  timeout_ms INTEGER NOT NULL DEFAULT 30000,
  max_retries INTEGER NOT NULL DEFAULT 0,
  audit_enabled INTEGER NOT NULL DEFAULT 1,
  enabled INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tool_definitions_category ON tool_definitions(category);
CREATE INDEX IF NOT EXISTS idx_tool_definitions_enabled ON tool_definitions(enabled);

CREATE TABLE IF NOT EXISTS tool_permissions (
  id TEXT PRIMARY KEY,
  tool_name TEXT NOT NULL REFERENCES tool_definitions(name) ON DELETE CASCADE,
  action TEXT NOT NULL,
  scope_type TEXT NOT NULL,
  scope_value TEXT NOT NULL,
  permission_level TEXT NOT NULL,
  risk_level_ceiling TEXT NOT NULL,
  enabled INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tool_permissions_lookup ON tool_permissions(tool_name, action, scope_type, enabled);

CREATE TABLE IF NOT EXISTS tool_call_logs (
  id TEXT PRIMARY KEY,
  run_id TEXT,
  tool_name TEXT NOT NULL,
  status TEXT NOT NULL,
  risk_level TEXT NOT NULL,
  permission_decision TEXT NOT NULL,
  redacted_input_json TEXT NOT NULL DEFAULT '{}',
  redacted_output_json TEXT,
  error_message TEXT,
  approval_request_id TEXT,
  started_at TEXT NOT NULL,
  completed_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_tool_call_logs_run ON tool_call_logs(run_id, started_at);
CREATE INDEX IF NOT EXISTS idx_tool_call_logs_tool ON tool_call_logs(tool_name, started_at);

CREATE TABLE IF NOT EXISTS approval_requests (
  id TEXT PRIMARY KEY,
  run_id TEXT,
  tool_name TEXT,
  action_type TEXT NOT NULL,
  resource_type TEXT NOT NULL,
  resource_id TEXT,
  risk_level TEXT NOT NULL,
  status TEXT NOT NULL,
  requested_by TEXT NOT NULL,
  preview_json TEXT NOT NULL,
  diff_preview_json TEXT NOT NULL DEFAULT '{}',
  action_json TEXT NOT NULL,
  decision_json TEXT,
  reason TEXT,
  created_at TEXT NOT NULL,
  decided_at TEXT,
  expires_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_approval_requests_status ON approval_requests(status, created_at);

CREATE TABLE IF NOT EXISTS permission_policies (
  id TEXT PRIMARY KEY,
  subject_type TEXT NOT NULL,
  subject_id TEXT,
  tool_name TEXT,
  action TEXT NOT NULL,
  scope_type TEXT NOT NULL,
  scope_value TEXT NOT NULL,
  permission_level TEXT NOT NULL,
  risk_level_ceiling TEXT NOT NULL,
  enabled INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_permission_policies_lookup ON permission_policies(tool_name, action, scope_type, enabled);

CREATE TABLE IF NOT EXISTS model_call_logs (
  id TEXT PRIMARY KEY,
  run_id TEXT,
  provider TEXT NOT NULL,
  model_name TEXT NOT NULL,
  task_type TEXT NOT NULL,
  privacy_level TEXT NOT NULL,
  status TEXT NOT NULL,
  prompt_tokens INTEGER,
  completion_tokens INTEGER,
  error_message TEXT,
  started_at TEXT NOT NULL,
  completed_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_model_call_logs_run ON model_call_logs(run_id, started_at);

CREATE TABLE IF NOT EXISTS audit_logs (
  id TEXT PRIMARY KEY,
  run_id TEXT,
  event_type TEXT NOT NULL,
  actor_type TEXT NOT NULL,
  actor_id TEXT,
  resource_type TEXT,
  resource_id TEXT,
  risk_level TEXT,
  status TEXT NOT NULL,
  summary TEXT NOT NULL,
  redacted_payload_json TEXT NOT NULL DEFAULT '{}',
  trace_id TEXT,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_logs_run ON audit_logs(run_id, created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_event ON audit_logs(event_type, created_at);
