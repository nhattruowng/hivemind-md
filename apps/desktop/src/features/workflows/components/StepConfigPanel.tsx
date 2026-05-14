import { useMemo } from 'react';

import { Button } from '@/components/ui/Button';
import { PermissionBadge } from '@/components/ui/PermissionBadge';
import { RiskBadge } from '@/components/ui/RiskBadge';
import type { PermissionLevel, RiskLevel } from '@/types/common.types';

import { useWorkflowBuilderStore } from '../workflow.store';

const riskOptions: RiskLevel[] = ['low', 'medium', 'high', 'critical'];
const permissionOptions: PermissionLevel[] = ['read_only', 'write_draft', 'execute_with_approval', 'execute_auto', 'forbidden'];

export function StepConfigPanel() {
  const selectedNodeId = useWorkflowBuilderStore((state) => state.selectedNodeId);
  const nodes = useWorkflowBuilderStore((state) => state.nodes);
  const updateStep = useWorkflowBuilderStore((state) => state.updateStep);

  const selected = useMemo(() => nodes.find((node) => node.id === selectedNodeId), [nodes, selectedNodeId]);

  if (!selected) {
    return (
      <aside className="w-80 shrink-0 border-l border-line bg-panel p-4">
        <div className="text-sm font-semibold">Step config</div>
        <p className="mt-2 text-sm text-muted">Select a workflow node to edit input mapping, risk, retry, timeout and compensation.</p>
      </aside>
    );
  }

  const step = selected.data.step;

  return (
    <aside className="w-80 shrink-0 overflow-y-auto border-l border-line bg-panel">
      <div className="border-b border-line p-4">
        <div className="text-sm font-semibold">Step config</div>
        <div className="mt-2 flex flex-wrap gap-2">
          <RiskBadge risk={step.risk_level} />
          <PermissionBadge permission={step.permission_level} />
        </div>
      </div>
      <div className="space-y-4 p-4">
        <label className="block">
          <span className="text-xs text-muted">Name</span>
          <input
            className="mt-1 h-9 w-full rounded-ui border border-line bg-canvas px-3 text-sm outline-none focus:border-sky-400"
            value={step.name}
            onChange={(event) => updateStep(step.id, { name: event.target.value })}
          />
        </label>
        <label className="block">
          <span className="text-xs text-muted">Description</span>
          <textarea
            className="mt-1 h-20 w-full resize-none rounded-ui border border-line bg-canvas px-3 py-2 text-sm outline-none focus:border-sky-400"
            value={step.description ?? ''}
            onChange={(event) => updateStep(step.id, { description: event.target.value })}
          />
        </label>
        <label className="block">
          <span className="text-xs text-muted">Risk level</span>
          <select
            className="mt-1 h-9 w-full rounded-ui border border-line bg-canvas px-3 text-sm outline-none focus:border-sky-400"
            value={step.risk_level}
            onChange={(event) => updateStep(step.id, { risk_level: event.target.value as RiskLevel })}
          >
            {riskOptions.map((risk) => (
              <option key={risk} value={risk}>
                {risk}
              </option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className="text-xs text-muted">Permission</span>
          <select
            className="mt-1 h-9 w-full rounded-ui border border-line bg-canvas px-3 text-sm outline-none focus:border-sky-400"
            value={step.permission_level}
            onChange={(event) => updateStep(step.id, { permission_level: event.target.value as PermissionLevel })}
          >
            {permissionOptions.map((permission) => (
              <option key={permission} value={permission}>
                {permission}
              </option>
            ))}
          </select>
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={step.requires_approval}
            onChange={(event) => updateStep(step.id, { requires_approval: event.target.checked })}
          />
          Requires approval
        </label>
        <label className="block">
          <span className="text-xs text-muted">Timeout ms</span>
          <input
            type="number"
            className="mt-1 h-9 w-full rounded-ui border border-line bg-canvas px-3 text-sm outline-none focus:border-sky-400"
            value={step.timeout_ms}
            onChange={(event) => updateStep(step.id, { timeout_ms: Number(event.target.value) })}
          />
        </label>
        <JsonTextarea
          label="Input JSON"
          value={step.input}
          onChange={(input) => updateStep(step.id, { input })}
        />
        <JsonTextarea
          label="Output mapping JSON"
          value={step.output_mapping}
          onChange={(output_mapping) => updateStep(step.id, { output_mapping })}
        />
        <JsonTextarea
          label="Compensation JSON"
          value={step.compensation ?? {}}
          onChange={(compensation) => updateStep(step.id, { compensation })}
        />
        <Button className="w-full" variant="primary">
          Apply step config
        </Button>
      </div>
    </aside>
  );
}

function JsonTextarea({
  label,
  value,
  onChange
}: {
  label: string;
  value: Record<string, unknown>;
  onChange: (value: Record<string, unknown>) => void;
}) {
  return (
    <label className="block">
      <span className="text-xs text-muted">{label}</span>
      <textarea
        className="mt-1 h-28 w-full resize-none rounded-ui border border-line bg-canvas px-3 py-2 font-mono text-xs outline-none focus:border-sky-400"
        value={JSON.stringify(value, null, 2)}
        onChange={(event) => {
          try {
            onChange(JSON.parse(event.target.value) as Record<string, unknown>);
          } catch {
            // Keep user typing; validation panel will surface invalid JSON once editor is upgraded.
          }
        }}
      />
    </label>
  );
}
