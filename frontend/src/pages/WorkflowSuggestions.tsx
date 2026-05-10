import { RefreshCcw } from "lucide-react";
import { useEffect, useState } from "react";
import {
  listWorkflowSuggestions,
  markWorkflowSuggestionApplied,
  rejectWorkflowSuggestion,
  type WorkflowSuggestion
} from "../api/client";
import { WorkflowSuggestionCard } from "../components/self-improvement/WorkflowSuggestionCard";

export function WorkflowSuggestions() {
  const [suggestions, setSuggestions] = useState<WorkflowSuggestion[]>([]);
  const [status, setStatus] = useState("pending");
  const [riskLevel, setRiskLevel] = useState("");
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      setSuggestions(
        await listWorkflowSuggestions({
          status: status || undefined,
          risk_level: riskLevel || undefined
        })
      );
    } finally {
      setLoading(false);
    }
  };

  const markApplied = async (id: number) => {
    await markWorkflowSuggestionApplied(id);
    await load();
  };

  const reject = async (id: number) => {
    await rejectWorkflowSuggestion(id);
    await load();
  };

  useEffect(() => {
    void load();
  }, []);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-white">Gợi ý quy trình</h1>
        <p className="mt-1 text-sm text-slate-400">Các cải thiện quy trình đang chờ được rà soát thủ công</p>
      </header>

      <section className="grid gap-3 rounded border border-line bg-panel p-4 shadow-soft md:grid-cols-[180px_180px_auto]">
        <select
          className="min-h-11 rounded border border-line bg-ink px-3 text-sm text-white"
          onChange={(event) => setStatus(event.target.value)}
          value={status}
        >
          <option value="">Tất cả trạng thái</option>
          <option value="pending">Đang chờ</option>
          <option value="applied">Đã áp dụng</option>
          <option value="rejected">Đã từ chối</option>
        </select>
        <select
          className="min-h-11 rounded border border-line bg-ink px-3 text-sm text-white"
          onChange={(event) => setRiskLevel(event.target.value)}
          value={riskLevel}
        >
          <option value="">Tất cả mức rủi ro</option>
          <option value="low">Thấp</option>
          <option value="medium">Trung bình</option>
          <option value="high">Cao</option>
        </select>
        <button
          className="inline-flex min-h-11 items-center justify-center gap-2 rounded bg-accent px-4 text-sm font-semibold text-ink transition hover:bg-accent/90 disabled:opacity-60"
          disabled={loading}
          onClick={() => void load()}
          type="button"
        >
          <RefreshCcw size={16} aria-hidden="true" />
          Làm mới
        </button>
      </section>

      <section className="space-y-4">
        {suggestions.map((suggestion) => (
          <WorkflowSuggestionCard
            key={suggestion.id}
            suggestion={suggestion}
            onApply={(id) => void markApplied(id)}
            onReject={(id) => void reject(id)}
          />
        ))}
        {!suggestions.length ? (
          <p className="rounded border border-line bg-panel p-5 text-sm text-slate-400">Chưa có gợi ý quy trình.</p>
        ) : null}
      </section>
    </div>
  );
}
