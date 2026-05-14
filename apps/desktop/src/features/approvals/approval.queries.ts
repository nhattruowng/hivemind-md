import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

import { approvalApi } from './approval.api';

export const approvalKeys = {
  all: ['approvals'] as const,
  list: () => [...approvalKeys.all, 'list'] as const,
  detail: (id: string) => [...approvalKeys.all, 'detail', id] as const
};

export function useApprovalsQuery() {
  return useQuery({ queryKey: approvalKeys.list(), queryFn: approvalApi.list });
}

export function useApprovalDecisionMutation(action: 'approve' | 'reject' | 'modifyAndApprove') {
  const queryClient = useQueryClient();
  const mutationFn = approvalApi[action];
  return useMutation({
    mutationFn: ({ approvalId, reason }: { approvalId: string; reason?: string }) => mutationFn(approvalId, { reason }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: approvalKeys.all });
      toast.success('Approval decision recorded');
    },
    onError: (error) => toast.error(error instanceof Error ? error.message : 'Approval decision failed')
  });
}
