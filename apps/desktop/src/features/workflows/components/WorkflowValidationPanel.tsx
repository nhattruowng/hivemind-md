import { AlertTriangle, CheckCircle2 } from 'lucide-react';

import { EmptyState } from '@/components/ui/EmptyState';
import { RiskBadge } from '@/components/ui/RiskBadge';

import { useWorkflowBuilderStore } from '../workflow.store';
import type { WorkflowValidationIssue } from '../workflow.types';

export function WorkflowValidationPanel() {
  const definition = useWorkflowBuilderStore((state) => state.definition);
  const edges = useWorkflowBuilderStore((state) => state.edges);
  const issues = validateWorkflow(definition.steps, edges.length);

  return (
    <section className="h-full overflow-y-auto border-t border-line bg-panel p-3">
      <div className="mb-3 flex items-center justify-between">
        <div className="text-sm font-semibold">Validation</div>
        <span className="text-xs text-muted">{issues.length} issues</span>
      </div>
      {issues.length === 0 ? (
        <EmptyState
          title="Workflow looks valid"
          description="No missing inputs, dangerous unapproved steps, or disconnected nodes detected."
          action={<CheckCircle2 className="h-5 w-5 text-emerald-300" />}
        />
      ) : (
        <div className="space-y-2">
          {issues.map((issue) => (
            <div key={issue.id} className="rounded-ui border border-line bg-canvas p-3">
              <div className="flex items-center gap-2 text-sm font-medium">
                <AlertTriangle className={issue.severity === 'error' ? 'h-4 w-4 text-red-300' : 'h-4 w-4 text-amber-300'} />
                {issue.title}
              </div>
              <p className="mt-1 text-xs text-muted">{issue.detail}</p>
            </div>
          ))}
        </div>
      )}
      <div className="mt-3 rounded-ui border border-amber-500/30 bg-amber-500/10 p-3 text-xs text-amber-100">
        Dangerous steps must be protected by approval. <RiskBadge risk="high" />
      </div>
    </section>
  );
}

function validateWorkflow(steps: ReturnType<typeof useWorkflowBuilderStore.getState>['definition']['steps'], edgeCount: number): WorkflowValidationIssue[] {
  const issues: WorkflowValidationIssue[] = [];
  if (steps.length === 0) {
    issues.push({
      id: 'no-steps',
      severity: 'error',
      title: 'No steps configured',
      detail: 'Drag a node from the palette into the canvas.'
    });
  }
  steps.forEach((step) => {
    if (!step.name.trim()) {
      issues.push({ id: `${step.id}-name`, severity: 'error', title: 'Missing step name', detail: 'Every step needs a readable name.', stepId: step.id });
    }
    if ((step.risk_level === 'high' || step.risk_level === 'critical') && !step.requires_approval) {
      issues.push({
        id: `${step.id}-approval`,
        severity: 'error',
        title: 'Dangerous step without approval',
        detail: `${step.name} is ${step.risk_level} risk and must require approval.`,
        stepId: step.id
      });
    }
    if (step.type === 'tool_call' && !step.input.tool_name) {
      issues.push({ id: `${step.id}-tool`, severity: 'error', title: 'Unknown tool', detail: 'Tool Call steps need input.tool_name.', stepId: step.id });
    }
  });
  if (steps.length > 1 && edgeCount === 0) {
    issues.push({ id: 'disconnected', severity: 'warning', title: 'Disconnected graph', detail: 'Connect nodes to make execution order explicit.' });
  }
  return issues;
}
