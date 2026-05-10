import { formatValueLabel } from "../../utils/labels";

interface ImprovementPolicyBadgeProps {
  value: string;
}

const tones: Record<string, string> = {
  low: "border-emerald-400/40 bg-emerald-400/10 text-emerald-200",
  medium: "border-amber-400/40 bg-amber-400/10 text-amber-200",
  high: "border-red-400/40 bg-red-400/10 text-red-200",
  active: "border-emerald-400/40 bg-emerald-400/10 text-emerald-200",
  pending: "border-sky-400/40 bg-sky-400/10 text-sky-200",
  applied: "border-emerald-400/40 bg-emerald-400/10 text-emerald-200",
  rejected: "border-slate-500/40 bg-slate-500/10 text-slate-300",
  archived: "border-slate-500/40 bg-slate-500/10 text-slate-300",
  success: "border-emerald-400/40 bg-emerald-400/10 text-emerald-200",
  failed: "border-red-400/40 bg-red-400/10 text-red-200"
};

export function ImprovementPolicyBadge({ value }: ImprovementPolicyBadgeProps) {
  const normalized = value.toLowerCase();
  return (
    <span className={`inline-flex min-h-7 items-center rounded border px-2 text-xs font-medium ${tones[normalized] ?? tones.pending}`}>
      {formatValueLabel(value)}
    </span>
  );
}
