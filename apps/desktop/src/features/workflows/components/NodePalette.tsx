import {
  Bell,
  Bot,
  Clock,
  GitBranch,
  Hourglass,
  Search,
  ShieldCheck,
  Split,
  Wrench,
  Zap
} from 'lucide-react';

import type { WorkflowStepType } from '../workflow.types';

const items: Array<{ type: WorkflowStepType; label: string; description: string; icon: typeof Wrench }> = [
  { type: 'tool_call', label: 'Tool Call', description: 'Call a registered tool', icon: Wrench },
  { type: 'agent_task', label: 'Agent Task', description: 'Ask planner/executor', icon: Bot },
  { type: 'condition', label: 'Condition', description: 'Branch by expression', icon: GitBranch },
  { type: 'loop', label: 'Loop', description: 'Repeat over items', icon: Hourglass },
  { type: 'approval', label: 'Approval', description: 'Require human decision', icon: ShieldCheck },
  { type: 'delay', label: 'Delay', description: 'Wait before next step', icon: Clock },
  { type: 'notification', label: 'Notification', description: 'Notify user', icon: Bell },
  { type: 'memory_search', label: 'Memory Search', description: 'Search local memory', icon: Search },
  { type: 'model_call', label: 'Model Call', description: 'Route to model', icon: Zap },
  { type: 'transform', label: 'Transform', description: 'Map JSON data', icon: Split }
];

export function NodePalette() {
  return (
    <aside className="w-64 shrink-0 border-r border-line bg-panel p-3">
      <div className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted">Node palette</div>
      <div className="space-y-2">
        {items.map((item) => (
          <button
            key={item.type}
            draggable
            onDragStart={(event) => {
              event.dataTransfer.setData('application/x-bizflow-step', item.type);
              event.dataTransfer.effectAllowed = 'move';
            }}
            className="flex w-full items-start gap-3 rounded-ui border border-line bg-panel2 p-3 text-left transition hover:border-sky-500/60 hover:bg-sky-500/10"
          >
            <item.icon className="mt-0.5 h-4 w-4 text-sky-200" />
            <span>
              <span className="block text-sm font-medium text-text">{item.label}</span>
              <span className="block text-xs text-muted">{item.description}</span>
            </span>
          </button>
        ))}
      </div>
    </aside>
  );
}
