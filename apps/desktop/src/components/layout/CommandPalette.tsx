import { Search } from 'lucide-react';

import { useUiStore } from '@/stores/ui.store';

export function CommandPalette() {
  const open = useUiStore((state) => state.commandPaletteOpen);
  const setOpen = useUiStore((state) => state.setCommandPaletteOpen);

  if (!open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/60 pt-24" onClick={() => setOpen(false)}>
      <div className="w-[640px] rounded-ui border border-line bg-panel shadow-2xl" onClick={(event) => event.stopPropagation()}>
        <div className="flex items-center gap-2 border-b border-line px-4 py-3">
          <Search className="h-4 w-4 text-muted" />
          <input
            autoFocus
            className="w-full bg-transparent text-sm outline-none placeholder:text-muted"
            placeholder="Run command, open workflow, search memory"
          />
        </div>
        <div className="p-3 text-sm text-muted">Start typing to navigate BizFlow.</div>
      </div>
    </div>
  );
}
