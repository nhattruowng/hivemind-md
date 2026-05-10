import { CheckCircle2, CircleDashed, Loader2, XCircle } from "lucide-react";
import { formatValueLabel } from "../utils/labels";

interface AgentStatusCardProps {
  agent: string;
  status: string;
  message: string;
  score?: number | null;
  runtimeMs?: number | null;
}

const statusStyles: Record<string, string> = {
  success: "border-accent/40 bg-accent/10 text-accent",
  failed: "border-red-400/40 bg-red-400/10 text-red-300",
  running: "border-signal/40 bg-signal/10 text-signal",
  pending: "border-slate-500/40 bg-slate-500/10 text-slate-300"
};

export function AgentStatusCard({ agent, status, message, score, runtimeMs }: AgentStatusCardProps) {
  const normalized = status.toLowerCase();
  const Icon =
    normalized === "success"
      ? CheckCircle2
      : normalized === "failed"
        ? XCircle
        : normalized === "running"
          ? Loader2
          : CircleDashed;

  return (
    <div className="rounded border border-line bg-panel p-4 shadow-soft">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="truncate text-sm font-semibold text-white">{agent}</div>
          <p className="mt-2 text-sm leading-6 text-slate-300">{message || "Đang chờ"}</p>
          {score != null || runtimeMs != null ? (
            <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-400">
              {score != null ? <span>Điểm {Math.round(score * 100)}%</span> : null}
              {runtimeMs != null ? <span>{formatRuntime(runtimeMs)}</span> : null}
            </div>
          ) : null}
        </div>
        <span
          className={[
            "inline-flex min-h-8 shrink-0 items-center gap-2 rounded border px-2.5 text-xs font-medium",
            statusStyles[normalized] ?? statusStyles.pending
          ].join(" ")}
        >
          <Icon size={15} className={normalized === "running" ? "animate-spin" : ""} aria-hidden="true" />
          {formatValueLabel(normalized || "pending")}
        </span>
      </div>
    </div>
  );
}

function formatRuntime(value: number) {
  if (value < 1000) return `${value}ms`;
  return `${(value / 1000).toFixed(1)}s`;
}
