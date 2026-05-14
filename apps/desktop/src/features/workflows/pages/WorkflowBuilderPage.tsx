import { Save, ShieldAlert } from 'lucide-react';

import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';

import { NodePalette } from '../components/NodePalette';
import { StepConfigPanel } from '../components/StepConfigPanel';
import { WorkflowCanvas } from '../components/WorkflowCanvas';
import { WorkflowJsonPreview } from '../components/WorkflowJsonPreview';
import { WorkflowRunTestPanel } from '../components/WorkflowRunTestPanel';
import { WorkflowValidationPanel } from '../components/WorkflowValidationPanel';
import { useSaveWorkflowMutation } from '../workflow.queries';
import { useWorkflowBuilderStore } from '../workflow.store';

export function WorkflowBuilderPage() {
  const definition = useWorkflowBuilderStore((state) => state.definition);
  const workflowId = useWorkflowBuilderStore((state) => state.workflowId);
  const saveMutation = useSaveWorkflowMutation(workflowId);

  return (
    <div className="grid h-full grid-cols-[256px_minmax(0,1fr)_320px] grid-rows-[56px_minmax(0,1fr)_260px] overflow-hidden">
      <header className="col-span-3 flex items-center gap-3 border-b border-line bg-panel px-4">
        <div>
          <h1 className="text-base font-semibold">Workflow Builder</h1>
          <p className="text-xs text-muted">Drag steps, configure risk, validate DSL, and test runs safely.</p>
        </div>
        <Badge className="ml-3">Draft</Badge>
        <Badge className="border-amber-500/40 bg-amber-500/10 text-amber-200">
          <ShieldAlert className="mr-1 h-3 w-3" />
          Approval enforced
        </Badge>
        <div className="ml-auto flex gap-2">
          <Button variant="secondary">Validate</Button>
          <Button variant="primary" icon={<Save className="h-4 w-4" />} disabled={saveMutation.isPending} onClick={() => saveMutation.mutate(definition)}>
            Save draft
          </Button>
        </div>
      </header>

      <NodePalette />
      <section className="min-w-0 bg-canvas">
        <WorkflowCanvas />
      </section>
      <StepConfigPanel />

      <div className="col-start-1 row-start-3 min-h-0">
        <WorkflowValidationPanel />
      </div>
      <div className="col-start-2 row-start-3 min-h-0">
        <WorkflowJsonPreview />
      </div>
      <div className="col-start-3 row-start-3 min-h-0">
        <WorkflowRunTestPanel workflowId={workflowId} />
      </div>
    </div>
  );
}
