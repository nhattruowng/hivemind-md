import { Handle, Position, type NodeProps } from '@xyflow/react';
import { Bell, Bot, Clock, GitBranch, Hourglass, ListFilter, Network, Search, ShieldCheck, Split, Wrench, Zap } from 'lucide-react';

import { RiskBadge } from '@/components/ui/RiskBadge';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { cn } from '@/utils/cn';

import type { WorkflowFlowNode, WorkflowStepType } from '../workflow.types';

const icons: Record<WorkflowStepType, typeof Wrench> = {
  tool_call: Wrench,
  agent_task: Bot,
  condition: GitBranch,
  loop: Hourglass,
  approval: ShieldCheck,
  delay: Clock,
  notification: Bell,
  memory_search: Search,
  model_call: Zap,
  transform: Split,
  sub_workflow: Network
};

export function WorkflowNode({ data, selected }: NodeProps<WorkflowFlowNode>) {
  const Icon = icons[data.step.type];

  return (
    <div
      className={cn(
        'w-[240px] rounded-ui border bg-panel shadow-xl transition',
        selected ? 'border-sky-400 ring-2 ring-sky-500/30' : 'border-line'
      )}
    >
      <Handle type="target" position={Position.Left} />
      <div className="border-b border-line p-3">
        <div className="flex items-start gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-ui border border-line bg-panel2">
            <Icon className="h-4 w-4 text-sky-200" />
          </div>
          <div className="min-w-0">
            <div className="truncate text-sm font-semibold text-text">{data.step.name}</div>
            <div className="text-xs text-muted">{data.step.type.replace(/_/g, ' ')}</div>
          </div>
        </div>
      </div>
      <div className="space-y-2 p-3">
        <div className="flex flex-wrap gap-2">
          <RiskBadge risk={data.step.risk_level} />
          {data.step.requires_approval ? <StatusBadge status="waiting_approval" /> : null}
        </div>
        <div className="flex items-center gap-2 text-xs text-muted">
          <ListFilter className="h-3 w-3" />
          {data.step.depends_on.length ? `${data.step.depends_on.length} dependencies` : 'No dependencies'}
        </div>
      </div>
      <Handle type="source" position={Position.Right} />
    </div>
  );
}
