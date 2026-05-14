ALTER TABLE approval_requests ADD COLUMN workflow_id TEXT;
ALTER TABLE approval_requests ADD COLUMN step_run_id TEXT;
ALTER TABLE approval_requests ADD COLUMN step_name TEXT;
ALTER TABLE approval_requests ADD COLUMN permission_level TEXT;
ALTER TABLE approval_requests ADD COLUMN input_preview_json TEXT DEFAULT '{}';
ALTER TABLE approval_requests ADD COLUMN output_preview_json TEXT DEFAULT '{}';
ALTER TABLE approval_requests ADD COLUMN expected_effect TEXT;

CREATE TABLE IF NOT EXISTS workflows (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  status TEXT NOT NULL,
  trigger_type TEXT NOT NULL,
  current_version INTEGER NOT NULL DEFAULT 1,
  definition_json TEXT NOT NULL,
  input_schema_json TEXT NOT NULL DEFAULT '{}',
  output_schema_json TEXT NOT NULL DEFAULT '{}',
  variables_json TEXT NOT NULL DEFAULT '{}',
  error_policy_json TEXT NOT NULL DEFAULT '{}',
  approval_policy_json TEXT NOT NULL DEFAULT '{}',
  retry_policy_json TEXT NOT NULL DEFAULT '{}',
  timeout_policy_json TEXT NOT NULL DEFAULT '{}',
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  deleted_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows(status, updated_at);
CREATE INDEX IF NOT EXISTS idx_workflows_trigger ON workflows(trigger_type, status);

CREATE TABLE IF NOT EXISTS workflow_versions (
  id TEXT PRIMARY KEY,
  workflow_id TEXT NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
  version INTEGER NOT NULL,
  definition_json TEXT NOT NULL,
  change_reason TEXT,
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL,
  UNIQUE(workflow_id, version)
);
CREATE INDEX IF NOT EXISTS idx_workflow_versions_workflow ON workflow_versions(workflow_id, version);

CREATE TABLE IF NOT EXISTS workflow_steps (
  id TEXT PRIMARY KEY,
  workflow_id TEXT NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
  step_key TEXT NOT NULL,
  name TEXT NOT NULL,
  type TEXT NOT NULL,
  description TEXT,
  input_json TEXT NOT NULL DEFAULT '{}',
  output_mapping_json TEXT NOT NULL DEFAULT '{}',
  depends_on_json TEXT NOT NULL DEFAULT '[]',
  condition_json TEXT NOT NULL DEFAULT '{}',
  retry_policy_json TEXT NOT NULL DEFAULT '{}',
  timeout_ms INTEGER NOT NULL DEFAULT 30000,
  requires_approval INTEGER NOT NULL DEFAULT 0,
  risk_level TEXT NOT NULL,
  permission_level TEXT NOT NULL,
  compensation_json TEXT NOT NULL DEFAULT '{}',
  on_success_json TEXT NOT NULL DEFAULT '{}',
  on_failure_json TEXT NOT NULL DEFAULT '{}',
  metadata_json TEXT NOT NULL DEFAULT '{}',
  step_order INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(workflow_id, step_key)
);
CREATE INDEX IF NOT EXISTS idx_workflow_steps_workflow ON workflow_steps(workflow_id, step_order);

CREATE TABLE IF NOT EXISTS workflow_triggers (
  id TEXT PRIMARY KEY,
  workflow_id TEXT NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
  trigger_type TEXT NOT NULL,
  config_json TEXT NOT NULL DEFAULT '{}',
  enabled INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_workflow_triggers_workflow ON workflow_triggers(workflow_id, enabled);

CREATE TABLE IF NOT EXISTS workflow_runs (
  id TEXT PRIMARY KEY,
  workflow_id TEXT NOT NULL REFERENCES workflows(id),
  workflow_version INTEGER NOT NULL,
  status TEXT NOT NULL,
  trigger_type TEXT NOT NULL,
  input_json TEXT NOT NULL DEFAULT '{}',
  output_json TEXT,
  error_json TEXT,
  replay_parent_run_id TEXT,
  replay_from_step_run_id TEXT,
  idempotency_key TEXT,
  created_by TEXT NOT NULL,
  started_at TEXT,
  updated_at TEXT NOT NULL,
  completed_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_workflow_runs_workflow ON workflow_runs(workflow_id, started_at);
CREATE INDEX IF NOT EXISTS idx_workflow_runs_status ON workflow_runs(status, updated_at);

CREATE TABLE IF NOT EXISTS workflow_step_runs (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES workflow_runs(id) ON DELETE CASCADE,
  workflow_id TEXT NOT NULL,
  step_key TEXT NOT NULL,
  step_name TEXT NOT NULL,
  step_type TEXT NOT NULL,
  status TEXT NOT NULL,
  attempt INTEGER NOT NULL DEFAULT 1,
  max_attempts INTEGER NOT NULL DEFAULT 1,
  input_json TEXT NOT NULL DEFAULT '{}',
  output_json TEXT,
  redacted_input_json TEXT NOT NULL DEFAULT '{}',
  redacted_output_json TEXT,
  error_json TEXT,
  approval_request_id TEXT,
  tool_call_log_id TEXT,
  model_call_log_id TEXT,
  started_at TEXT,
  updated_at TEXT NOT NULL,
  completed_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_workflow_step_runs_run ON workflow_step_runs(run_id, started_at);
CREATE INDEX IF NOT EXISTS idx_workflow_step_runs_status ON workflow_step_runs(status, updated_at);

CREATE TABLE IF NOT EXISTS workflow_variables (
  id TEXT PRIMARY KEY,
  workflow_id TEXT NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  value_json TEXT NOT NULL,
  is_secret INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(workflow_id, name)
);

CREATE TABLE IF NOT EXISTS workflow_run_context (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES workflow_runs(id) ON DELETE CASCADE,
  context_key TEXT NOT NULL,
  value_json TEXT NOT NULL,
  redacted_value_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(run_id, context_key)
);
CREATE INDEX IF NOT EXISTS idx_workflow_run_context_run ON workflow_run_context(run_id);

CREATE TABLE IF NOT EXISTS workflow_schedules (
  id TEXT PRIMARY KEY,
  workflow_id TEXT NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
  cron_expression TEXT NOT NULL,
  timezone TEXT NOT NULL,
  next_run_at TEXT,
  last_run_at TEXT,
  enabled INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_workflow_schedules_due ON workflow_schedules(enabled, next_run_at);

CREATE TABLE IF NOT EXISTS workflow_event_bindings (
  id TEXT PRIMARY KEY,
  workflow_id TEXT NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
  event_type TEXT NOT NULL,
  condition_json TEXT NOT NULL DEFAULT '{}',
  source_scope_json TEXT NOT NULL DEFAULT '{}',
  enabled INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_workflow_event_bindings_event ON workflow_event_bindings(event_type, enabled);

CREATE TABLE IF NOT EXISTS workflow_audit_events (
  id TEXT PRIMARY KEY,
  workflow_id TEXT,
  run_id TEXT,
  step_run_id TEXT,
  event_type TEXT NOT NULL,
  status TEXT NOT NULL,
  message TEXT NOT NULL,
  risk_level TEXT,
  redacted_payload_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_workflow_audit_run ON workflow_audit_events(run_id, created_at);
CREATE INDEX IF NOT EXISTS idx_workflow_audit_workflow ON workflow_audit_events(workflow_id, created_at);

CREATE TABLE IF NOT EXISTS workflow_replay_runs (
  id TEXT PRIMARY KEY,
  parent_run_id TEXT NOT NULL REFERENCES workflow_runs(id),
  replay_run_id TEXT NOT NULL REFERENCES workflow_runs(id),
  from_step_run_id TEXT NOT NULL,
  input_override_json TEXT NOT NULL DEFAULT '{}',
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_workflow_replay_parent ON workflow_replay_runs(parent_run_id, created_at);

CREATE TABLE IF NOT EXISTS retry_policies (
  id TEXT PRIMARY KEY,
  owner_type TEXT NOT NULL,
  owner_id TEXT NOT NULL,
  max_attempts INTEGER NOT NULL DEFAULT 1,
  backoff_strategy TEXT NOT NULL,
  initial_delay_ms INTEGER NOT NULL DEFAULT 1000,
  max_delay_ms INTEGER NOT NULL DEFAULT 30000,
  retry_on_errors_json TEXT NOT NULL DEFAULT '[]',
  do_not_retry_on_errors_json TEXT NOT NULL DEFAULT '[]',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_retry_policies_owner ON retry_policies(owner_type, owner_id);

CREATE TABLE IF NOT EXISTS rollback_actions (
  id TEXT PRIMARY KEY,
  workflow_id TEXT NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
  step_key TEXT NOT NULL,
  compensation_type TEXT NOT NULL,
  compensation_json TEXT NOT NULL,
  requires_approval INTEGER NOT NULL DEFAULT 1,
  status TEXT NOT NULL DEFAULT 'active',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_rollback_actions_step ON rollback_actions(workflow_id, step_key);
