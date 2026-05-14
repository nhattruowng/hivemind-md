import { apiClient } from '@/services/apiClient';

import type { ApprovalDecisionPayload, ApprovalRequest } from './approval.types';

export const approvalApi = {
  list: () => apiClient.get<ApprovalRequest[]>('/api/approvals'),
  get: (approvalId: string) => apiClient.get<ApprovalRequest>(`/api/approvals/${approvalId}`),
  approve: (approvalId: string, payload: ApprovalDecisionPayload) =>
    apiClient.post<ApprovalRequest>(`/api/approvals/${approvalId}/approve`, payload),
  reject: (approvalId: string, payload: ApprovalDecisionPayload) =>
    apiClient.post<ApprovalRequest>(`/api/approvals/${approvalId}/reject`, payload),
  modifyAndApprove: (approvalId: string, payload: ApprovalDecisionPayload) =>
    apiClient.post<ApprovalRequest>(`/api/approvals/${approvalId}/modify-and-approve`, payload)
};
