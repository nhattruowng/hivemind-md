import { Circle } from 'lucide-react';

export function StatusBar() {
  return (
    <footer className="col-span-2 row-start-3 flex items-center gap-4 border-t border-line bg-panel px-3 text-xs text-muted">
      <span className="flex items-center gap-1">
        <Circle className="h-2 w-2 fill-emerald-400 text-emerald-400" />
        Local core online
      </span>
      <span>Vector DB: ready</span>
      <span>Last audit: workflow validation completed</span>
      <span className="ml-auto">Dark mode · Developer mode</span>
    </footer>
  );
}
