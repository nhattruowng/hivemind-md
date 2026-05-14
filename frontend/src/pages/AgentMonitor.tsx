import { useAgentRun } from "../context/AgentRunContext";
import { formatValueLabel } from "../utils/labels";

const defaultAgents = [
  "SearchAgent",
  "CrawlerAgent",
  "CleanerAgent",
  "ExtractorAgent",
  "CriticAgent",
  "ComposerAgent",
  "IndexerAgent"
];

export function AgentMonitor() {
  const { logs } = useAgentRun();
  const rows = defaultAgents.map((agent) => {
    const log = logs.find((item) => item.agent === agent);
    return {
      agent,
      status: log?.status ?? "pending",
      message: log?.message ?? "Đang chờ"
    };
  });

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-white">Giám sát tác nhân</h1>
        <p className="mt-1 text-sm text-slate-400">Trạng thái mới nhất của quy trình tạo tri thức</p>
      </header>

      <div className="overflow-hidden rounded border border-line bg-panel shadow-soft">
        <table className="w-full border-collapse text-left text-sm">
          <thead className="bg-white/5 text-slate-300">
            <tr>
              <th className="px-4 py-3 font-medium">Tác nhân</th>
              <th className="px-4 py-3 font-medium">Trạng thái</th>
              <th className="px-4 py-3 font-medium">Thông báo</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.agent} className="border-t border-line">
                <td className="px-4 py-4 font-medium text-white">{row.agent}</td>
                <td className="px-4 py-4 text-slate-200">{formatValueLabel(row.status)}</td>
                <td className="px-4 py-4 text-slate-300">{row.message}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
