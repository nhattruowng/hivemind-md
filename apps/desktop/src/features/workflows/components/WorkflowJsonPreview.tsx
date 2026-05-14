import { Copy, FileJson, Wand2 } from 'lucide-react';
import { toast } from 'sonner';

import { Button } from '@/components/ui/Button';

import { useWorkflowBuilderStore } from '../workflow.store';

export function WorkflowJsonPreview() {
  const definition = useWorkflowBuilderStore((state) => state.definition);
  const json = JSON.stringify(definition, null, 2);

  return (
    <section className="flex h-full min-h-0 flex-col border-t border-line bg-panel">
      <div className="flex items-center gap-2 border-b border-line p-3">
        <FileJson className="h-4 w-4 text-sky-200" />
        <div className="text-sm font-semibold">JSON Preview</div>
        <div className="ml-auto flex gap-2">
          <Button
            variant="ghost"
            icon={<Copy className="h-4 w-4" />}
            onClick={() => {
              void navigator.clipboard.writeText(json);
              toast.success('Workflow JSON copied');
            }}
          >
            Copy
          </Button>
          <Button variant="ghost" icon={<Wand2 className="h-4 w-4" />}>
            Format
          </Button>
        </div>
      </div>
      <pre className="min-h-0 flex-1 overflow-auto p-3 font-mono text-xs leading-5 text-slate-300">{json}</pre>
    </section>
  );
}
