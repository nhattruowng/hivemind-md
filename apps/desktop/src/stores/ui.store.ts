import { create } from 'zustand';

export type AppPage =
  | 'dashboard'
  | 'chat'
  | 'memory'
  | 'tools'
  | 'permissions'
  | 'approvals'
  | 'workflows'
  | 'agent-studio'
  | 'models'
  | 'connectors'
  | 'audit'
  | 'settings';

interface UiState {
  theme: 'dark';
  sidebarCollapsed: boolean;
  commandPaletteOpen: boolean;
  rightInspectorOpen: boolean;
  activeWorkspace: string;
  activePage: AppPage;
  selectedMemoryId?: string;
  selectedWorkflowId?: string;
  selectedWorkflowNodeId?: string;
  setActivePage: (page: AppPage) => void;
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
  activePage: 'dashboard',
  setActivePage: (activePage) => set({ activePage }),
  setSidebarCollapsed: (sidebarCollapsed) => set({ sidebarCollapsed }),
  setCommandPaletteOpen: (commandPaletteOpen) => set({ commandPaletteOpen }),
  setRightInspectorOpen: (rightInspectorOpen) => set({ rightInspectorOpen }),
  setSelectedWorkflowNodeId: (selectedWorkflowNodeId) => set({ selectedWorkflowNodeId })
}));
