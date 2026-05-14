import { CheckCircle2, Eye } from "lucide-react";
import { useState } from "react";
import type { PromptVersion } from "../../api/client";
import { ImprovementPolicyBadge } from "./ImprovementPolicyBadge";

interface PromptVersionCardProps {
  version: PromptVersion;
  onActivate?: (id: number) => void;
}

export function PromptVersionCard({ version, onActivate }: PromptVersionCardProps) {
  const [open, setOpen] = useState(false);

  return (
    <article className="rounded border border-line bg-panel p-5 shadow-soft">
      <div className="grid gap-4 lg:grid-cols-[1fr_auto] lg:items-start">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-lg font-semibold text-white">{version.agent_name}</h2>
            <span className="rounded border border-line px-2 py-1 text-xs text-slate-300">{version.version}</span>
            <ImprovementPolicyBadge value={version.risk_level} />
            {version.is_active ? <ImprovementPolicyBadge value="active" /> : null}
          </div>
          <p className="mt-2 text-sm text-slate-400">
            Điểm {version.score ?? "Không có"} · {new Date(version.created_at).toLocaleString("vi-VN")}
          </p>
          {version.change_reason ? <p className="mt-3 text-sm text-slate-300">{version.change_reason}</p> : null}
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            className="inline-flex min-h-10 items-center justify-center gap-2 rounded border border-line px-3 text-sm text-slate-200 transition hover:bg-white/10"
            onClick={() => setOpen((value) => !value)}
            type="button"
          >
            <Eye size={16} aria-hidden="true" />
            Xem
          </button>
          {!version.is_active && onActivate ? (
            <button
              className="inline-flex min-h-10 items-center justify-center gap-2 rounded bg-accent px-3 text-sm font-semibold text-ink transition hover:bg-accent/90"
              onClick={() => onActivate(version.id)}
            type="button"
          >
            <CheckCircle2 size={16} aria-hidden="true" />
              Kích hoạt
            </button>
          ) : null}
        </div>
      </div>
      {open ? (
        <pre className="mt-4 max-h-96 overflow-auto whitespace-pre-wrap break-words rounded border border-line bg-ink p-4 text-sm leading-6 text-slate-300">
          {version.prompt}
        </pre>
      ) : null}
    </article>
  );
}
