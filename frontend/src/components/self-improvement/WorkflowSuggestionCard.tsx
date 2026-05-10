import { CheckCircle2, XCircle } from "lucide-react";
import type { WorkflowSuggestion } from "../../api/client";
import { ImprovementPolicyBadge } from "./ImprovementPolicyBadge";

interface WorkflowSuggestionCardProps {
  suggestion: WorkflowSuggestion;
  onApply?: (id: number) => void;
  onReject?: (id: number) => void;
}

export function WorkflowSuggestionCard({ suggestion, onApply, onReject }: WorkflowSuggestionCardProps) {
  const canAct = suggestion.status === "pending";

  return (
    <article className="rounded border border-line bg-panel p-5 shadow-soft">
      <div className="grid gap-4 lg:grid-cols-[1fr_auto] lg:items-start">
        <div className="min-w-0 space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded border border-line px-2 py-1 text-xs text-slate-300">{suggestion.task_id}</span>
            <ImprovementPolicyBadge value={suggestion.risk_level} />
            <ImprovementPolicyBadge value={suggestion.status} />
          </div>
          <pre className="whitespace-pre-wrap break-words text-sm leading-6 text-white">{suggestion.suggestion}</pre>
          {suggestion.expected_benefit ? <p className="text-sm text-slate-300">{suggestion.expected_benefit}</p> : null}
          <p className="text-xs text-slate-500">{new Date(suggestion.updated_at).toLocaleString("vi-VN")}</p>
        </div>
        {canAct ? (
          <div className="flex flex-wrap gap-2">
            <button
              className="inline-flex min-h-10 items-center justify-center gap-2 rounded bg-accent px-3 text-sm font-semibold text-ink transition hover:bg-accent/90"
              onClick={() => onApply?.(suggestion.id)}
            type="button"
          >
            <CheckCircle2 size={16} aria-hidden="true" />
              Đánh dấu đã áp dụng
            </button>
            <button
              className="inline-flex min-h-10 items-center justify-center gap-2 rounded border border-line px-3 text-sm text-slate-200 transition hover:bg-white/10"
              onClick={() => onReject?.(suggestion.id)}
            type="button"
          >
            <XCircle size={16} aria-hidden="true" />
              Từ chối
            </button>
          </div>
        ) : null}
      </div>
    </article>
  );
}
