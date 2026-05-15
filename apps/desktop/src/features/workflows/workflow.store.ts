import { addEdge, applyEdgeChanges, applyNodeChanges, type Connection, type EdgeChange, type NodeChange } from '@xyflow/react';
import { create } from 'zustand';

import type { WorkflowDefinition, WorkflowFlowEdge, WorkflowFlowNode, WorkflowStep, WorkflowStepType } from './workflow.types';

const defaultRetry = {
  max_attempts: 2,
  backoff_strategy: 'exponential' as const,
  initial_delay_ms: 1000,
  max_delay_ms: 30000
};

export const defaultWorkflowDefinition: WorkflowDefinition = {
  name: 'Untitled workflow',
  description: 'Draft automation built in BizFlow.',
  version: 1,
  status: 'draft',
  trigger: { type: 'manual' },
  input_schema: { type: 'object', properties: {} },
  output_schema: { type: 'object', properties: {} },
  variables: {},
  steps: [],
  error_policy: { type: 'retry_then_fail' },
  approval_policy: { high: 'always', critical: 'always', write: 'always' },
  retry_policy: defaultRetry,
  timeout_policy: { workflow_timeout_ms: 300000, timeout_action: 'fail' },
  created_by: 'user',
  metadata: {}
};

interface WorkflowBuilderState {
  workflowId?: string;
  definition: WorkflowDefinition;
  nodes: WorkflowFlowNode[];
  edges: WorkflowFlowEdge[];
  selectedNodeId?: string;
  setDefinition: (definition: WorkflowDefinition) => void;
  setSelectedNodeId: (nodeId?: string) => void;
  addStepNode: (type: WorkflowStepType, position: { x: number; y: number }) => void;
  updateStep: (stepId: string, patch: Partial<WorkflowStep>) => void;
  onNodesChange: (changes: NodeChange[]) => void;
  onEdgesChange: (changes: EdgeChange[]) => void;
  onConnect: (connection: Connection) => void;
}

export const useWorkflowBuilderStore = create<WorkflowBuilderState>((set, get) => ({
  definition: defaultWorkflowDefinition,
  nodes: [],
  edges: [],
  setDefinition: (definition) => set({ definition }),
  setSelectedNodeId: (selectedNodeId) => set({ selectedNodeId }),
  addStepNode: (type, position) => {
    const step = createStep(type);
    const node: WorkflowFlowNode = {
      id: step.id,
      type: 'workflowNode',
      position,
      data: { step }
    };
    set((state) => ({
      nodes: [...state.nodes, node],
      definition: { ...state.definition, steps: [...state.definition.steps, step] },
      selectedNodeId: step.id
    }));
  },
  updateStep: (stepId, patch) => {
    set((state) => {
      const steps = state.definition.steps.map((step) => (step.id === stepId ? { ...step, ...patch } : step));
      const nodes = state.nodes.map((node) =>
        node.id === stepId ? { ...node, data: { ...node.data, step: steps.find((step) => step.id === stepId)! } } : node
      );
      return { definition: { ...state.definition, steps }, nodes };
    });
  },
  onNodesChange: (changes) => set({ nodes: applyNodeChanges(changes, get().nodes) as unknown as WorkflowFlowNode[] }),
  onEdgesChange: (changes) => set({ edges: applyEdgeChanges(changes, get().edges) }),
  onConnect: (connection) => {
    set((state) => {
      const edges = addEdge({ ...connection, animated: true, type: 'smoothstep' }, state.edges);
      const steps = state.definition.steps.map((step) =>
        step.id === connection.target
          ? { ...step, depends_on: Array.from(new Set([...step.depends_on, connection.source!])) }
          : step
      );
      return { edges, definition: { ...state.definition, steps } };
    });
  }
}));

function createStep(type: WorkflowStepType): WorkflowStep {
  const id = `${type}_${Math.random().toString(36).slice(2, 8)}`;
  const risky = type === 'approval' || type === 'tool_call';
  return {
    id,
    name: titleForType(type),
    type,
    description: '',
    input: defaultInputForType(type),
    output_mapping: {},
    depends_on: [],
    retry_policy: defaultRetry,
    timeout_ms: 30000,
    requires_approval: type === 'approval',
    risk_level: risky ? 'medium' : 'low',
    permission_level: risky ? 'execute_with_approval' : 'read_only',
    compensation: {},
    on_success: {},
    on_failure: { policy: 'fail_fast' },
    metadata: {}
  };
}

function titleForType(type: WorkflowStepType) {
  return type
    .split('_')
    .map((part) => part[0].toUpperCase() + part.slice(1))
    .join(' ');
}

function defaultInputForType(type: WorkflowStepType): Record<string, unknown> {
  if (type === 'tool_call') {
    return { tool_name: 'read_local_file', args: {} };
  }
  if (type === 'memory_search') {
    return { query: '{{input.query}}', limit: 8 };
  }
  if (type === 'model_call') {
    return { task: 'summarize', privacy_level: 'internal' };
  }
  return {};
}
