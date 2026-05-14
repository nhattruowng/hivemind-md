import { Play, ShieldCheck } from 'lucide-react';

import { Button } from '@/components/ui/Button';
import { ErrorState } from '@/components/ui/ErrorState';
import { LoadingSkeleton } from '@/components/ui/LoadingSkeleton';

import { useRunWorkflowMutation } from '../workflow.queries';

export function WorkflowRunTestPanel({ workflowId }: { workflowId?: string }) {
  const runMutation = useRunWorkflowMutation(workflowId);

  return (
    <section className="border-t border-line bg-panel p-3">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <div className="text-sm font-semibold">Run test</div>
          <div className="text-xs text-muted">Dry-run support will mock approvals and tool outputs.</div>
        </div>
        <Button
          variant="primary"
          icon={<Play className="h-4 w-4" />}
          onClick={() => runMutation.mutate({ dry_run: true })}
          disabled={runMutation.isPending}
        >
          Run test
        </Button>
      </div>
      <div className="rounded-ui border border-line bg-canvas p-3 text-xs text-muted">
        <div className="mb-2 flex items-center gap-2 text-amber-100">
          <ShieldCheck className="h-4 w-4" />
          Approval mock enabled
        </div>
        Risky steps will stop at the approval boundary unless mocked.
      </div>
      {runMutation.isPending ? <LoadingSkeleton className="mt-3 h-16" /> : null}
      {runMutation.isError ? (
        <div className="mt-3">
          <ErrorState title="Run test failed" message={runMutation.error.message} onRetry={() => runMutation.mutate({ dry_run: true })} />
        </div>
      ) : null}
    </section>
  );
}
