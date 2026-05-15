import {
  Activity,
  Bot,
  Brain,
  Cable,
  CheckSquare,
  Database,
  GitBranch,
  Home,
  KeyRound,
  Settings,
  Shield,
  SlidersHorizontal,
  Wrench
} from 'lucide-react';

import type { AppPage } from '@/stores/ui.store';
import { useUiStore } from '@/stores/ui.store';
import { cn } from '@/utils/cn';

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: Home },
  { id: 'chat', label: 'Chat', icon: Bot },
  { id: 'memory', label: 'Memory Map', icon: Brain },
  { id: 'tools', label: 'Tool Manager', icon: Wrench },
  { id: 'permissions', label: 'Permissions', icon: Shield },
  { id: 'approvals', label: 'Approval Inbox', icon: CheckSquare },
  { id: 'workflows', label: 'Workflow Builder', icon: GitBranch },
  { id: 'agent-studio', label: 'Agent Studio', icon: SlidersHorizontal },
  { id: 'models', label: 'Models', icon: Database },
  { id: 'connectors', label: 'Connectors', icon: Cable },
  { id: 'audit', label: 'Audit Log', icon: Activity },
  { id: 'settings', label: 'Settings', icon: Settings }
] satisfies Array<{ id: AppPage; label: string; icon: typeof Home }>;

export function Sidebar() {
  const activePage = useUiStore((state) => state.activePage);
  const setActivePage = useUiStore((state) => state.setActivePage);

  return (
    <aside className="row-span-3 flex min-h-0 flex-col border-r border-line bg-panel">
      <div className="flex h-14 items-center gap-3 border-b border-line px-4">
        <div className="flex h-8 w-8 items-center justify-center rounded-ui border border-sky-500/40 bg-sky-500/15">
          <KeyRound className="h-4 w-4 text-sky-200" />
        </div>
        <div>
          <div className="text-sm font-semibold">BizFlow Local</div>
          <div className="text-xs text-muted">Privacy-first agent</div>
        </div>
      </div>
      <nav className="flex-1 space-y-1 overflow-y-auto p-3">
        {navItems.map((item) => (
          <button
            key={item.label}
            onClick={() => setActivePage(item.id)}
            className={cn(
              'flex w-full items-center gap-3 rounded-ui px-3 py-2 text-left text-sm transition',
              activePage === item.id ? 'bg-sky-500/15 text-sky-100' : 'text-muted hover:bg-panel2 hover:text-text'
            )}
          >
            <item.icon className="h-4 w-4" />
            {item.label}
          </button>
        ))}
      </nav>
    </aside>
  );
}
