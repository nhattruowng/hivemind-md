import { Code2, FlaskConical, History, Play, ScrollText } from 'lucide-react';

import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';

const tabs = [
  { label: 'Tool Schema Editor', icon: Code2 },
  { label: 'Prompt Editor', icon: ScrollText },
  { label: 'Test Runner', icon: Play },
  { label: 'Trace Viewer', icon: History },
  { label: 'Evaluation Test Cases', icon: FlaskConical }
];

export function AgentStudioPage() {
  return (
    <div className="grid h-full grid-cols-[240px_1fr_360px] overflow-hidden bg-canvas">
      <aside className="border-r border-line bg-panel p-3">
        <div className="mb-3 text-sm font-semibold">Agent Studio</div>
        <div className="space-y-1">
          {tabs.map((tab, index) => (
            <button
              key={tab.label}
              className={`flex w-full items-center gap-2 rounded-ui px-3 py-2 text-left text-sm ${index === 0 ? 'bg-sky-500/15 text-sky-100' : 'text-muted hover:bg-panel2'}`}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </div>
      </aside>
      <main className="min-w-0 overflow-y-auto p-4">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold">Tool Schema Editor</h1>
            <p className="text-sm text-muted">Validate JSON Schema, generate samples, and save tool versions.</p>
          </div>
          <Button variant="primary">Validate schema</Button>
        </div>
        <div className="rounded-ui border border-line bg-panel">
          <div className="border-b border-line px-3 py-2 text-sm">input_schema.json</div>
          <textarea
            className="h-[520px] w-full resize-none bg-canvas p-4 font-mono text-xs text-slate-300 outline-none"
            defaultValue={JSON.stringify({ type: 'object', required: ['path'], properties: { path: { type: 'string' } } }, null, 2)}
          />
        </div>
      </main>
      <aside className="border-l border-line bg-panel p-4">
        <div className="text-sm font-semibold">Test Runner</div>
        <p className="mt-2 text-sm text-muted">Mock tool responses without touching the real local core.</p>
        <div className="mt-4 space-y-2">
          <Badge>Model: local</Badge>
          <Badge>Memory: mocked</Badge>
          <Badge>Tool call: dry run</Badge>
        </div>
        <Button className="mt-4 w-full" variant="primary" icon={<Play className="h-4 w-4" />}>
          Run test
        </Button>
      </aside>
    </div>
  );
}
