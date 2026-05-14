import { create } from 'zustand';

interface UiState {
  theme: 'dark';
  sidebarCollapsed: boolean;
  commandPaletteOpen: boolean;
  rightInspectorOpen: boolean;
  activeWorkspace: string;
  selectedMemoryId?: string;
  selectedWorkflowId?: string;
  selectedWorkflowNodeId?: string;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setCommandPaletteOpen: (open: boolean) => void;
  setRightInspectorOpen: (open: boolean) => void;
  setSelectedWorkflowNodeId: (nodeId?: string) => void;
}

export const useUiStore = create<UiState>((set) => ({
  theme: 'dark',
  sidebarCollapsed: false,
  commandPaletteOpen: false,
  rightInspectorOpen: true,
  activeWorkspace: 'Local Workspace',
  setSidebarCollapsed: (sidebarCollapsed) => set({ sidebarCollapsed }),
  setCommandPaletteOpen: (commandPaletteOpen) => set({ commandPaletteOpen }),
  setRightInspectorOpen: (rightInspectorOpen) => set({ rightInspectorOpen }),
  setSelectedWorkflowNodeId: (selectedWorkflowNodeId) => set({ selectedWorkflowNodeId })
}));
