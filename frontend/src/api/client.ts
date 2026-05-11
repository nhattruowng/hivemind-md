import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000
});

export type BuildMode = "quick" | "standard" | "deep";

export interface AgentLog {
  agent: string;
  status: string;
  message: string;
  stage?: string | null;
  score?: number | null;
  runtime_ms?: number | null;
  started_at?: string | null;
  ended_at?: string | null;
  input_count?: number | null;
  output_count?: number | null;
  data: Record<string, unknown>;
}

export interface BuildKnowledgePayload {
  topic: string;
  mode: BuildMode;
  category: string;
}

export interface BuildKnowledgeResponse {
  status: string;
  markdown_file: string;
  agent_logs: AgentLog[];
}

export interface RefreshKnowledgePayload {
  topic: string;
  mode: BuildMode;
  category: string;
}

export interface RefreshKnowledgeResponse {
  status: string;
  topic: string;
  category: string;
  files: string[];
  map_file: string;
  agent_logs: AgentLog[];
}

export interface DomainProfile {
  id: string;
  name: string;
  category: string;
  description: string;
  focus_areas: string[];
  worker_count: number;
  max_parallel_workers: number;
  use_llm_workers: number;
}

export interface AgentFrameworkPayload {
  topic: string;
  mode: BuildMode;
  category: string;
  profile_id: string;
}

export interface AgentFrameworkResponse {
  status: string;
  topic: string;
  category: string;
  profile: DomainProfile;
  files: string[];
  map_file: string;
  average_score: number;
  agent_scores: Record<string, number>;
  stages: Record<string, unknown>;
  agent_logs: AgentLog[];
}

export interface KnowledgeItem {
  title: string;
  category: string;
  file_path: string;
  updated_at: string;
  trust_score?: number | null;
}

export interface ChatResponse {
  answer: string;
  related_files: string[];
  sources: string[];
  conversation_id: string;
  chat_file: string;
  auto_refreshed: boolean;
  updated_files: string[];
  confidence?: number | null;
  grounding_score?: number | null;
  citations: Array<Record<string, unknown>>;
  verification: Record<string, unknown>;
  plan: Record<string, unknown>;
  agents_used: string[];
  tool_calls: Array<Record<string, unknown>>;
  needs_approval: boolean;
  approval_request?: Record<string, unknown> | null;
  token_estimate?: number | null;
  route: Record<string, unknown>;
  active_agents: number;
  agent_roles: Array<Record<string, string>>;
  agent_logs: AgentLog[];
}

export interface ChatPayload {
  message: string;
  conversation_id?: string | null;
  auto_refresh?: boolean;
  category?: string;
  mode?: BuildMode;
}

export interface KnowledgeCleanupResponse {
  status: string;
  dry_run: boolean;
  scanned_files: number;
  duplicate_groups: number;
  noise_files: number;
  quarantined_files: string[];
  report_file: string;
  map_file: string;
  agent_logs: AgentLog[];
}

export interface SelfImprovementSummary {
  total_runs: number;
  average_score: number;
  success_rate: number;
  total_lessons: number;
  total_prompt_versions: number;
  pending_workflow_suggestions: number;
}

export interface AgentRun {
  id: number;
  task_id: string;
  task: string;
  agent_name: string;
  input?: string | null;
  output?: string | null;
  score?: number | null;
  status: string;
  error_message?: string | null;
  runtime_ms?: number | null;
  created_at: string;
}

export interface ImprovementLesson {
  id: number;
  title: string;
  lesson_type: string;
  agent_name?: string | null;
  task_id?: string | null;
  content: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface PromptVersion {
  id: number;
  agent_name: string;
  version: string;
  prompt: string;
  score?: number | null;
  is_active: number;
  risk_level: string;
  change_reason?: string | null;
  created_at: string;
}

export interface WorkflowSuggestion {
  id: number;
  task_id: string;
  suggestion: string;
  expected_benefit?: string | null;
  risk_level: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface PlatformAgent {
  id: string;
  user_id?: string | null;
  name: string;
  slug: string;
  category: string;
  description?: string | null;
  role: string;
  goal?: string | null;
  system_prompt?: string | null;
  default_model?: string | null;
  temperature: number;
  risk_level: "low" | "medium" | "high";
  allowed_tools: string[];
  input_schema: Record<string, unknown>;
  output_schema: Record<string, unknown>;
  evaluation_metrics: string[];
  is_system: boolean;
  is_active: boolean;
  config: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface CreateAgentPayload {
  name: string;
  category?: string;
  description?: string;
  role: string;
  goal?: string;
  system_prompt?: string;
  default_model?: string;
  temperature?: number;
  risk_level?: "low" | "medium" | "high";
  allowed_tools?: string[];
  evaluation_metrics?: string[];
  config?: Record<string, unknown>;
}

export interface RuntimeTimelineItem {
  agent_id?: string;
  agent: string;
  category?: string;
  status: string;
  message: string;
  data: Record<string, unknown>;
  confidence?: number | null;
  sources?: unknown[];
  tool_calls?: Array<Record<string, unknown>>;
  risk_level?: string;
  runtime_ms?: number;
}

export interface AgentRuntimeResponse {
  task_id: string;
  agent: PlatformAgent;
  result: RuntimeTimelineItem;
  timeline: RuntimeTimelineItem[];
}

export interface PlanPreviewResponse {
  task_id?: string | null;
  intent: Record<string, unknown>;
  route: Record<string, unknown>;
  plan: Record<string, unknown>;
  routing: Record<string, unknown>;
  agents_used: string[];
  confidence?: number | null;
  needs_approval: boolean;
  timeline: RuntimeTimelineItem[];
}

export interface ListAgentRunsParams {
  agent_name?: string;
  status?: string;
  limit?: number;
}

export interface ListLessonsParams {
  agent_name?: string;
  lesson_type?: string;
  status?: string;
}

export interface ListPromptVersionsParams {
  agent_name?: string;
}

export interface ListWorkflowSuggestionsParams {
  status?: string;
  risk_level?: string;
}

export const healthCheck = async () => {
  const { data } = await apiClient.get<{ status: string; service: string }>("/api/health");
  return data;
};

export const ollamaHealth = async () => {
  const { data } = await apiClient.get<{ status: string; models: string[]; error?: string }>("/api/health/ollama");
  return data;
};

export const buildKnowledge = async (payload: BuildKnowledgePayload) => {
  const { data } = await apiClient.post<BuildKnowledgeResponse>("/api/agents/build-knowledge", payload);
  return data;
};

export const listPlatformAgents = async () => {
  const { data } = await apiClient.get<PlatformAgent[]>("/api/agents");
  return data;
};

export const createPlatformAgent = async (payload: CreateAgentPayload) => {
  const { data } = await apiClient.post<PlatformAgent>("/api/agents", payload);
  return data;
};

export const testPlatformAgent = async (agentId: string, input: Record<string, unknown>) => {
  const { data } = await apiClient.post<AgentRuntimeResponse>(`/api/agents/${agentId}/test`, { input });
  return data;
};

export const previewChatPlan = async (message: string) => {
  const { data } = await apiClient.post<PlanPreviewResponse>("/api/chat/plan-preview", { message });
  return data;
};

export const refreshKnowledge = async (payload: RefreshKnowledgePayload) => {
  const { data } = await apiClient.post<RefreshKnowledgeResponse>("/api/knowledge/refresh", payload);
  return data;
};

export const readKnowledgeMap = async () => {
  const { data } = await apiClient.get<{ map_file: string; content: string }>("/api/knowledge/map");
  return data;
};

export const listDomainProfiles = async () => {
  const { data } = await apiClient.get<DomainProfile[]>("/api/agent-framework/profiles");
  return data;
};

export const runAgentFramework = async (payload: AgentFrameworkPayload) => {
  const { data } = await apiClient.post<AgentFrameworkResponse>("/api/agent-framework/run", payload);
  return data;
};

export const listKnowledge = async () => {
  const { data } = await apiClient.get<KnowledgeItem[]>("/api/knowledge");
  return data;
};

export const readKnowledge = async (filePath: string) => {
  const { data } = await apiClient.get<{ content: string }>("/api/knowledge/read", {
    params: { file_path: filePath }
  });
  return data;
};

export const deleteKnowledge = async (filePath: string, approved = false) => {
  const { data } = await apiClient.delete<{ status: string; deleted: string }>("/api/knowledge/delete", {
    data: { file_path: filePath, approved }
  });
  return data;
};

export const chat = async (payload: string | ChatPayload) => {
  const body = typeof payload === "string" ? { message: payload } : payload;
  const { data } = await apiClient.post<ChatResponse>("/api/chat", body);
  return data;
};

export const cleanupKnowledge = async (payload: { dry_run?: boolean; min_trust?: number; approved?: boolean } = {}) => {
  const { data } = await apiClient.post<KnowledgeCleanupResponse>("/api/knowledge/cleanup", payload);
  return data;
};

export const getSelfImprovementSummary = async () => {
  const { data } = await apiClient.get<SelfImprovementSummary>("/api/self-improvement/summary");
  return data;
};

export const listAgentRuns = async (params: ListAgentRunsParams = {}) => {
  const { data } = await apiClient.get<AgentRun[]>("/api/self-improvement/runs", { params });
  return data;
};

export const listImprovementLessons = async (params: ListLessonsParams = {}) => {
  const { data } = await apiClient.get<ImprovementLesson[]>("/api/self-improvement/lessons", { params });
  return data;
};

export const archiveLesson = async (id: number) => {
  const { data } = await apiClient.post<ImprovementLesson>(`/api/self-improvement/lessons/${id}/archive`);
  return data;
};

export const listPromptVersions = async (params: ListPromptVersionsParams = {}) => {
  const { data } = await apiClient.get<PromptVersion[]>("/api/self-improvement/prompt-versions", { params });
  return data;
};

export const activatePromptVersion = async (id: number) => {
  const { data } = await apiClient.post<PromptVersion>(`/api/self-improvement/prompt-versions/${id}/activate`);
  return data;
};

export const listWorkflowSuggestions = async (params: ListWorkflowSuggestionsParams = {}) => {
  const { data } = await apiClient.get<WorkflowSuggestion[]>("/api/self-improvement/workflow-suggestions", { params });
  return data;
};

export const rejectWorkflowSuggestion = async (id: number) => {
  const { data } = await apiClient.post<WorkflowSuggestion>(`/api/self-improvement/workflow-suggestions/${id}/reject`);
  return data;
};

export const markWorkflowSuggestionApplied = async (id: number) => {
  const { data } = await apiClient.post<WorkflowSuggestion>(`/api/self-improvement/workflow-suggestions/${id}/apply`);
  return data;
};
