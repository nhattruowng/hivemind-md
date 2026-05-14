import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

import { workflowApi } from './workflow.api';
import type { WorkflowDefinition } from './workflow.types';

export const workflowKeys = {
  all: ['workflows'] as const,
  lists: () => [...workflowKeys.all, 'list'] as const,
  detail: (workflowId: string) => [...workflowKeys.all, 'detail', workflowId] as const
};

export function useWorkflowsQuery() {
  return useQuery({
    queryKey: workflowKeys.lists(),
    queryFn: workflowApi.list
  });
}

export function useSaveWorkflowMutation(workflowId?: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (definition: WorkflowDefinition) =>
      workflowId ? workflowApi.update(workflowId, definition) : workflowApi.create(definition),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: workflowKeys.all });
      toast.success('Workflow draft saved');
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : 'Unable to save workflow');
    }
  });
}

export function useRunWorkflowMutation(workflowId?: string) {
  return useMutation({
    mutationFn: (input: Record<string, unknown>) => {
      if (!workflowId) {
        throw new Error('Save the workflow before running a test');
      }
      return workflowApi.run(workflowId, input);
    },
    onSuccess: (run) => toast.success(`Workflow run started: ${run.id}`),
    onError: (error) => toast.error(error instanceof Error ? error.message : 'Unable to run workflow')
  });
}
