import { RefreshCcw } from "lucide-react";
import { useEffect, useState } from "react";
import { listAgentRuns, type AgentRun } from "../api/client";
import { AgentRunTable } from "../components/self-improvement/AgentRunTable";

export function AgentRuns() {
  const [runs, setRuns] = useState<AgentRun[]>([]);
  const [agentName, setAgentName] = useState("");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const data = await listAgentRuns({
        agent_name: agentName || undefined,
        status: status || undefined,
        limit: 100
      });
      setRuns(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-white">Lượt chạy tác nhân</h1>
        <p className="mt-1 text-sm text-slate-400">Các lần thực thi tác nhân và điểm đánh giá đã ghi nhận</p>
      </header>

      <section className="grid gap-3 rounded border border-line bg-panel p-4 shadow-soft md:grid-cols-[1fr_180px_auto]">
        <input
          className="min-h-11 rounded border border-line bg-ink px-3 text-sm text-white"
          onChange={(event) => setAgentName(event.target.value)}
          placeholder="Tên tác nhân"
          value={agentName}
        />
        <select
          className="min-h-11 rounded border border-line bg-ink px-3 text-sm text-white"
          onChange={(event) => setStatus(event.target.value)}
          value={status}
        >
          <option value="">Tất cả trạng thái</option>
          <option value="success">Thành công</option>
          <option value="failed">Thất bại</option>
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

      <AgentRunTable runs={runs} />
    </div>
  );
}
