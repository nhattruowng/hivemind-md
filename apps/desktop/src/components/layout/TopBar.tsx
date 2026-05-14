import { Bell, Circle, Command, Search } from 'lucide-react';

import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { useUiStore } from '@/stores/ui.store';

export function TopBar() {
  const activeWorkspace = useUiStore((state) => state.activeWorkspace);
  const setCommandPaletteOpen = useUiStore((state) => state.setCommandPaletteOpen);

  return (
    <header className="col-start-2 row-start-1 flex items-center gap-3 border-b border-line bg-panel px-4">
      <Badge>{activeWorkspace}</Badge>
      <div className="flex h-9 min-w-[360px] items-center gap-2 rounded-ui border border-line bg-canvas px-3 text-muted">
        <Search className="h-4 w-4" />
        <span className="text-sm">Search memory, workflows, tools</span>
      </div>
      <div className="ml-auto flex items-center gap-2">
        <Badge className="gap-2 border-emerald-500/40 bg-emerald-500/10 text-emerald-200">
          <Circle className="h-2 w-2 fill-emerald-400" />
          Ollama local
        </Badge>
        <Badge className="border-amber-500/40 bg-amber-500/10 text-amber-200">
          <Bell className="mr-1 h-3 w-3" />3 approvals
        </Badge>
        <Button variant="ghost" icon={<Command className="h-4 w-4" />} onClick={() => setCommandPaletteOpen(true)}>
          Ctrl K
        </Button>
      </div>
    </header>
  );
}
