import { Background, Controls, MiniMap, ReactFlow, ReactFlowProvider, type NodeTypes, useReactFlow } from '@xyflow/react';
import { useCallback, useMemo, type DragEvent } from 'react';

import { useWorkflowBuilderStore } from '../workflow.store';
import type { WorkflowStepType } from '../workflow.types';
import { WorkflowNode } from './WorkflowNode';

const nodeTypes: NodeTypes = {
  workflowNode: WorkflowNode
};

export function WorkflowCanvas() {
  return (
    <ReactFlowProvider>
      <WorkflowCanvasInner />
    </ReactFlowProvider>
  );
}

function WorkflowCanvasInner() {
  const nodes = useWorkflowBuilderStore((state) => state.nodes);
  const edges = useWorkflowBuilderStore((state) => state.edges);
  const onNodesChange = useWorkflowBuilderStore((state) => state.onNodesChange);
  const onEdgesChange = useWorkflowBuilderStore((state) => state.onEdgesChange);
  const onConnect = useWorkflowBuilderStore((state) => state.onConnect);
  const addStepNode = useWorkflowBuilderStore((state) => state.addStepNode);
  const setSelectedNodeId = useWorkflowBuilderStore((state) => state.setSelectedNodeId);
  const { screenToFlowPosition } = useReactFlow();

  const defaultEdgeOptions = useMemo(() => ({ type: 'smoothstep', animated: true }), []);

  const handleDrop = useCallback(
    (event: DragEvent) => {
      event.preventDefault();
      const type = event.dataTransfer.getData('application/x-bizflow-step') as WorkflowStepType;
      if (!type) {
        return;
      }
      addStepNode(type, screenToFlowPosition({ x: event.clientX, y: event.clientY }));
    },
    [addStepNode, screenToFlowPosition]
  );

  return (
    <div className="h-full" onDragOver={(event) => event.preventDefault()} onDrop={handleDrop}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={(_, node) => setSelectedNodeId(node.id)}
        onPaneClick={() => setSelectedNodeId(undefined)}
        defaultEdgeOptions={defaultEdgeOptions}
        fitView
      >
        <Background color="#1f2937" gap={24} />
        <Controls className="!border-line !bg-panel !text-text" />
        <MiniMap className="!bg-panel" maskColor="rgba(8,11,16,0.65)" />
      </ReactFlow>
    </div>
  );
}
