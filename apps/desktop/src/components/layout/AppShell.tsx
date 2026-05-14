import type { ReactNode } from 'react';

import { CommandPalette } from '@/components/layout/CommandPalette';
import { Sidebar } from '@/components/layout/Sidebar';
import { StatusBar } from '@/components/layout/StatusBar';
import { TopBar } from '@/components/layout/TopBar';

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="grid h-screen grid-cols-[256px_1fr] grid-rows-[52px_1fr_28px] overflow-hidden bg-canvas text-text">
      <Sidebar />
      <TopBar />
      <main className="col-start-2 row-start-2 min-w-0 overflow-hidden border-l border-line bg-canvas">{children}</main>
      <StatusBar />
      <CommandPalette />
    </div>
  );
}
