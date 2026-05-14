import { Check, FileDiff, X } from 'lucide-react';
import { useState } from 'react';

import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import { ErrorState } from '@/components/ui/ErrorState';
import { LoadingSkeleton } from '@/components/ui/LoadingSkeleton';
import { PermissionBadge } from '@/components/ui/PermissionBadge';
import { RiskBadge } from '@/components/ui/RiskBadge';
import { StatusBadge } from '@/components/ui/StatusBadge';

import { useApprovalDecisionMutation, useApprovalsQuery } from '../approval.queries';
import type { ApprovalRequest } from '../approval.types';

export function ApprovalInboxPage() {
  const approvalsQuery = useApprovalsQuery();
  const [selectedId, setSelectedId] = useState<string>();
  const approveMutation = useApprovalDecisionMutation('approve');
  const rejectMutation = useApprovalDecisionMutation('reject');

  if (approvalsQuery.isLoading) {
    return <LoadingSkeleton className="m-4 h-80" />;
  }
  if (approvalsQuery.isError) {
    return <ErrorState title="Approvals failed to load" message={approvalsQuery.error.message} onRetry={() => void approvalsQuery.refetch()} />;
  }

  const approvals = approvalsQuery.data ?? [];
  const selected = approvals.find((approval) => approval.id === selectedId) ?? approvals[0];

  return (
    <div className="grid h-full grid-cols-[420px_1fr] overflow-hidden bg-canvas">
      <section className="border-r border-line bg-panel">
        <div className="border-b border-line p-4">
          <h1 className="text-base font-semibold">Approval Inbox</h1>
          <p className="mt-1 text-sm text-muted">Review risky actions before the agent or workflow continues.</p>
        </div>
        {approvals.length === 0 ? (
          <div className="p-4">
            <EmptyState title="No pending approvals" description="Risky actions and workflow gates will appear here." />
          </div>
        ) : (
          <div className="space-y-2 overflow-y-auto p-3">
            {approvals.map((approval) => (
              <button
                key={approval.id}
                className="w-full rounded-ui border border-line bg-panel2 p-3 text-left hover:border-sky-500/50"
                onClick={() => setSelectedId(approval.id)}
              >
                <div className="flex items-center justify-between gap-3">
                  <div className="truncate text-sm font-medium">{approval.title ?? approval.stepName ?? approval.actionType}</div>
                  <StatusBadge status={approval.status} />
                </div>
                <div className="mt-3 flex flex-wrap gap-2">
                  <RiskBadge risk={approval.riskLevel} />
                  <PermissionBadge permission={approval.permissionLevel} />
                </div>
                <div className="mt-2 text-xs text-muted">{approval.toolName ?? approval.workflowId ?? approval.requestedBy}</div>
              </button>
            ))}
          </div>
        )}
      </section>

      <ApprovalDetail
        approval={selected}
        onApprove={(approvalId) => approveMutation.mutate({ approvalId, reason: 'Approved from desktop UI' })}
        onReject={(approvalId) => rejectMutation.mutate({ approvalId, reason: 'Rejected from desktop UI' })}
        busy={approveMutation.isPending || rejectMutation.isPending}
      />
    </div>
  );
}

function ApprovalDetail({
  approval,
  onApprove,
  onReject,
  busy
}: {
  approval?: ApprovalRequest;
  onApprove: (approvalId: string) => void;
  onReject: (approvalId: string) => void;
  busy: boolean;
}) {
  if (!approval) {
    return <EmptyState title="Select an approval" description="Approval details, previews and diffs will show here." />;
  }

  return (
    <section className="min-w-0 overflow-y-auto p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold">{approval.title ?? approval.stepName ?? approval.actionType}</h2>
          <p className="mt-1 text-sm text-muted">{approval.expectedEffect ?? 'This action needs your confirmation before execution.'}</p>
        </div>
        <div className="flex gap-2">
          <RiskBadge risk={approval.riskLevel} />
          <StatusBadge status={approval.status} />
        </div>
      </div>
      <div className="mt-5 grid grid-cols-2 gap-3">
        <Info label="Requested by" value={approval.requestedBy} />
        <Info label="Tool" value={approval.toolName ?? 'workflow step'} />
        <Info label="Action" value={approval.actionType} />
        <Info label="Resource" value={approval.resourceId ?? approval.resourceType} />
      </div>
      <Preview title="Input preview" value={approval.inputPreviewJson ?? approval.previewJson} />
      <Preview title="Diff preview" value={approval.diffPreviewJson ?? {}} icon={<FileDiff className="h-4 w-4" />} />
      <div className="mt-5 rounded-ui border border-rose-500/30 bg-rose-500/10 p-4">
        <div className="text-sm font-semibold text-rose-100">Risk explanation</div>
        <p className="mt-2 text-sm text-rose-100/75">
          This action may change local data, call a privileged tool, or continue a workflow after a human gate. Review the input and affected resource before approving.
        </p>
      </div>
      <div className="mt-5 flex items-center justify-end gap-3">
        <Button variant="ghost">Always allow this folder</Button>
        <Button variant="danger" icon={<X className="h-4 w-4" />} disabled={busy} onClick={() => onReject(approval.id)}>
          Reject
        </Button>
        <Button variant="primary" icon={<Check className="h-4 w-4" />} disabled={busy} onClick={() => onApprove(approval.id)}>
          Approve
        </Button>
      </div>
    </section>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-ui border border-line bg-panel p-3">
      <div className="text-xs text-muted">{label}</div>
      <div className="mt-1 truncate text-sm">{value}</div>
    </div>
  );
}

function Preview({ title, value, icon }: { title: string; value: unknown; icon?: React.ReactNode }) {
  return (
    <div className="mt-5 rounded-ui border border-line bg-panel">
      <div className="flex items-center gap-2 border-b border-line px-3 py-2 text-sm font-medium">
        {icon}
        {title}
      </div>
      <pre className="max-h-72 overflow-auto p-3 font-mono text-xs text-slate-300">{JSON.stringify(value, null, 2)}</pre>
    </div>
  );
}
