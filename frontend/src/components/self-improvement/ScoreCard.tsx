import type { LucideIcon } from "lucide-react";

interface ScoreCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
}

export function ScoreCard({ label, value, icon: Icon }: ScoreCardProps) {
  return (
    <div className="rounded border border-line bg-panel p-5 shadow-soft">
      <div className="flex items-center justify-between gap-4">
        <div className="min-w-0">
          <p className="text-sm text-slate-400">{label}</p>
          <p className="mt-2 break-words text-2xl font-semibold text-white">{value}</p>
        </div>
        <div className="grid h-11 w-11 shrink-0 place-items-center rounded bg-white/10 text-signal">
          <Icon size={21} aria-hidden="true" />
        </div>
      </div>
    </div>
  );
}
