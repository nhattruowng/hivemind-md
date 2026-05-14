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

import { cn } from '@/utils/cn';

const navItems = [
  { label: 'Dashboard', icon: Home, active: false },
  { label: 'Chat', icon: Bot, active: false },
  { label: 'Memory', icon: Brain, active: false },
  { label: 'Tools', icon: Wrench, active: false },
  { label: 'Permissions', icon: Shield, active: false },
  { label: 'Approvals', icon: CheckSquare, active: false },
  { label: 'Workflows', icon: GitBranch, active: true },
  { label: 'Agent Studio', icon: SlidersHorizontal, active: false },
  { label: 'Models', icon: Database, active: false },
  { label: 'Connectors', icon: Cable, active: false },
  { label: 'Audit Log', icon: Activity, active: false },
  { label: 'Settings', icon: Settings, active: false }
];

export function Sidebar() {
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
            className={cn(
              'flex w-full items-center gap-3 rounded-ui px-3 py-2 text-left text-sm transition',
              item.active ? 'bg-sky-500/15 text-sky-100' : 'text-muted hover:bg-panel2 hover:text-text'
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
