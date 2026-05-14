import { apiClient } from '@/services/apiClient';

import type { WorkflowDefinition, WorkflowResponse, WorkflowRun } from './workflow.types';

interface CreateWorkflowPayload {
  name: string;
  description?: string;
  triggerType: string;
  definition: WorkflowDefinition;
  createdBy: string;
}

export const workflowApi = {
  list: () => apiClient.get<WorkflowResponse[]>('/api/workflows'),
  get: (workflowId: string) => apiClient.get<WorkflowResponse>(`/api/workflows/${workflowId}`),
  create: (definition: WorkflowDefinition) =>
    apiClient.post<WorkflowResponse>('/api/workflows', {
      name: definition.name,
      description: definition.description,
      triggerType: definition.trigger.type,
      definition,
      createdBy: definition.created_by ?? 'user'
    } satisfies CreateWorkflowPayload),
  update: (workflowId: string, definition: WorkflowDefinition) =>
    apiClient.put<WorkflowResponse>(`/api/workflows/${workflowId}`, {
      name: definition.name,
      description: definition.description,
      definition,
      updatedBy: 'user'
    }),
  activate: (workflowId: string) => apiClient.post<WorkflowResponse>(`/api/workflows/${workflowId}/activate`),
  run: (workflowId: string, input: Record<string, unknown>) =>
    apiClient.post<WorkflowRun>(`/api/workflows/${workflowId}/run`, {
      input,
      createdBy: 'user',
      idempotencyKey: `ui-${Date.now()}`
    })
};
